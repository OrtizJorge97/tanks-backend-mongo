from flask import Flask, json, request, jsonify, make_response, url_for, render_template
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt
from flask_jwt_extended import create_refresh_token
import bcrypt
import concurrent.futures
import logging

import time
from datetime import timedelta

from .. import ts, email_salt, host_url, front_url
from . import auth_blueprint
from .models import *
from .utilities.constants import *
from .Services.database import AsyncDataBaseManager
from .Services.notifications import send_email
from app.main.Services.database import mongodb_handler

#AsyncDataBaseManager.db.close()
# Create a route to authenticate your users and return JWTs. The
# create_access_token() function is used to actually generate the JWT.
@auth_blueprint.route("/add-user", methods=["POST"])
@mongodb_handler
def add_user(db, args, kwargs):
    print("IN REAL FUNCTION")
    
    user = request.get_json()
    name = user["name"]
    last_name = user["lastName"]
    email = user["email"]
    password = user["password"]
    company = user["company"]
    role = roles["Supervisor"]

    users = db['users']
    try:
        print("------------PRINTING RESULTS OF SELECT NOSQL-----------")
        print(users.find_one({"email": email}))
        user_db = users.find_one({"email": email})
        if user_db:
            print(f"returned user_db {user_db}")
            return make_response(jsonify({"msg": "User already registered"}), 200)
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        print(f"hashed: {hashed}")
        user_db = users.find_one({"company": company})
        if not user_db:
            role = roles["Supervisor"]
        else:
            role = roles["Operator"]
            
        user_id = users.insert_one({
            "name": name,
            "last_name": last_name,
            "email": email,
            "password": hashed,
            "company": company,
            "role": role,
            "user_verified": False
        })

        token = ts.dumps(email, salt=email_salt)
        print("----------PRINTING URL FOR CONFIRMATION ACCOUNT------------")
        print(url_for('auth.confirm_account', token=token))
        activation_url = host_url + url_for('auth.confirm_account', token=token)
        executor = concurrent.futures.ThreadPoolExecutor()
        future = executor.submit(send_email, email, "Tanks Platform confirm email", f"Please click in this link {activation_url} to activate your account")
        future.result()
        return make_response(jsonify({"msg": "Succesfully added user"}), 200)

    except Exception as e:
        print(str(e))
        return make_response(jsonify({"msg": str(e)}), 500)


@auth_blueprint.route("/resend-confirmation-email", methods=["POST"])
def resend_confirmation_email():
    body_json = request.get_json()
    email = body_json['email']
    try:
        token = ts.dumps(email, salt=email_salt)
        print("----------PRINTING URL FOR CONFIRMATION ACCOUNT------------")
        print(url_for('auth.confirm_account', token=token))
        activation_url = host_url + url_for('auth.confirm_account', token=token)
        executor = concurrent.futures.ThreadPoolExecutor()
        future = executor.submit(send_email, email, "Tanks Platform confirm email", f"Please click in this link {activation_url} to activate your account")
        future.result()
        return make_response(jsonify({"msg": "Confirmation email successfully resent"}), 200)
    except Exception as e:
        print(str(e))
        return make_response(jsonify({"msg": str(e)}), 500)



@auth_blueprint.route("/confirm-account/<token>")
@mongodb_handler
def confirm_account(db, args, kwargs):
    token = kwargs['token']
    users_collection = db['users']
    print("----------PRINTING TOKEN-------")
    print(token)
    status_message = 'Success Activating account :)'
    try:
        email = ts.loads(token, salt=email_salt, max_age=86400)
        print(email)
    except:
        status_message = 'Invalid token!'
        return render_template('activation_status.html', account_status_message = status_message, front_url = front_url + '/log-in')
    
    try:
        #user_db = session.query(Users).filter_by(email=email).first()
        user_db = users_collection.find_one({"email": email})
        if not user_db['user_verified']:
            new_values = {
                "$set": {
                    "user_verified": True
                }
            }
            users_collection.update_one(user_db, new_values)
            for x in users_collection.find():
                print(x)
            return render_template('activation_status.html', account_status_message = status_message, front_url = front_url + '/log-in')
        
        status_message = "Account already activated :)"
        return render_template('activation_status.html', account_status_message = status_message, front_url = front_url + '/log-in')
    except Exception as e:
        print(str(e))
        return make_response(jsonify({"msg": str(e)}), 500)

# Create a route to authenticate your users and return JWTs. The
# create_access_token() function is used to actually generate the JWT.
@auth_blueprint.route("/login", methods=["POST"])
@mongodb_handler
def login(db, args, kwargs):
    print("json request")
    print(request.json)
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    users_collection = db['users']
    user_db = users_collection.find_one({"email": email})

    print("user db weee")
    print(user_db)
    #mail not found, meaning user does not exist
    if not user_db:
        return make_response(jsonify({"msg": "User not found"}), 404)

    if not user_db['user_verified']:
        return make_response(jsonify({"msg": "Account has not been activated, please check your email for confirming your account."}), 404)

    #password incorrect, notify user.
    if not bcrypt.checkpw(password.encode("utf-8"), user_db['password']):
        return make_response(jsonify({"msg": "Password incorrect"}), 200)

    user_claims = {
        "name": user_db['name'], 
        "last_name": user_db['last_name'], 
        "company": user_db['company'],
        "email": user_db['email'],
        "role": user_db['role']
    }
    access_token = create_access_token(identity=email, additional_claims=user_claims)
    refresh_token = create_refresh_token(identity=email, additional_claims=user_claims)
    return make_response(jsonify(msg="Succesfully authenticated",
                                 access_token=access_token, 
                                 refresh_token=refresh_token,
                                 user=user_claims), 200)


@auth_blueprint.route("/get-user", methods=["GET"])
@jwt_required()
def get_user():
    claims = get_jwt()
    print(claims["email"])
    return make_response(jsonify(msg="Succesfully authenticated",
                                 name=claims["name"],
                                 last_name=claims["last_name"],
                                 company=claims["company"],
                                 email=claims["email"],
                                 role=claims["role"]), 200)

# In a protected view, get the claims you added to the jwt with the
# get_jwt() method
@auth_blueprint.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    claims = get_jwt()
    return jsonify(user=claims["user"])

# We are using the `refresh=True` options in jwt_required to only allow
# refresh tokens to access this route.
@auth_blueprint.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    user = get_jwt_identity()
    print(user)
    user_claims = {"user": user}
    access_token = create_access_token(identity=user, additional_claims=user_claims)
    return jsonify(access_token=access_token)