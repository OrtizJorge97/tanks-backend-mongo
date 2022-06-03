from pickletools import read_uint1
from flask import Flask, request, Blueprint, jsonify, make_response
from flask_cors import CORS
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt
from flask_socketio import emit
from bson import ObjectId

import concurrent.futures

#from . import main
from . import api_blueprint
from .models import *
from .. import socketio
from .utilities import constants
from .utilities.convertions import *
from app.main.Services.database import mongodb_handler
from app.main.Services.database import AsyncDataBaseManager

@api_blueprint.route("/", methods=["GET"])
def index():
    return make_response(jsonify(msg="Success fetching!"), 200)

@api_blueprint.route("/fetch-tanks", methods=["GET"])
@jwt_required()
@mongodb_handler
def fetch_tanks(db, args, kwargs):
    claims = get_jwt()
    tanks_collection = db['tanks']

    tanks_db = tanks_collection.find({"company": claims["company"]})
    print("PRINTING TANKS DB")
    print(tanks_db)
    constants.tanks_company["tanks"] = []
    constants.tanks_company["tanks"] = [tank_db['tank_name'] for tank_db in tanks_db]
    print(constants.tanks_company["tanks"])
    """company = session.query(Companies).filter_by(company=claims["company"]).first()
    print("ID OF COMPANY: " + str(company.id))
    tanks_company_db = session.query(Tanks.tank_name, Companies.company).select_from(Tanks)\
        .join(Companies, Tanks.company_id == Companies.id)\
        .filter(Companies.id == company.id).all()

    constants.tanks_company["tanks"] = []
    print("------------------------RESULTS OF JOIN QUERY---------------------------")
    for tank_company in tanks_company_db:
        constants.tanks_company["tanks"].append(tank_company[0])

    print(constants.tanks_company["tanks"])
    return make_response(jsonify(
        msg="Success fetching",
        tanks=constants.tanks_company["tanks"],
        email=claims['email'],
        company=claims['company']), 200)"""
    return make_response(jsonify(
        msg="Success fetching",
        tanks=constants.tanks_company["tanks"],
        email=claims['email'],
        company=claims['company']), 200) 


@api_blueprint.route("/add-tank", methods=["POST"])
@jwt_required()
@mongodb_handler
def add_tank(db, args, kwargs):
    try:
        tank = request.get_json()
        print(tank)
        users_collection = db['users']
        tanks_collection = db['tanks']
        user_db = users_collection.find_one({"company": tank['company']})
        tank_db = tanks_collection.find_one({"tank_name": tank['tankId']})
        #company = session.query(Companies).filter_by(company=tank['company']).first()
        #tank_db = session.query(Tanks).filter_by(tank_name=tank['tankId']).first()
        print("-------PRINTING COMPANY DB------")
        print(user_db)
        print("-------PRINTING TANK DB------")
        print(tank_db)
        if tank_db:
            return make_response(jsonify(msg="Tank already added, please modify or delete."), 200)

        tank_id = tanks_collection.insert_one({
            "tank_name": tank['tankId'],
            "company": tank['company'],
            "WtrLvl": {
                "tank_min_value": tank['WtrLvlMin'],
                "tank_max_value": tank['WtrLvlMax']
            },
            "OxygenPercentage": {
                "tank_min_value": tank['OxygenPercentageMin'],
                "tank_max_value": tank['OxygenPercentageMax']
            },
            "Ph": {
                "tank_min_value": tank['PhMin'],
                "tank_max_value": tank['PhMax'] 
            }
        })
        print("PRINTING TANK ID WHEN INSERTING")
        print(tank_id)
        return make_response(jsonify(msg="Success adding"), 200)

    except Exception as e:
        return make_response(jsonify(msg=str(e)), 500)


@api_blueprint.route("/fetch-tank", methods=["GET"])
@jwt_required()
@mongodb_handler
def fetch_tank(db, args, kwargs):
    try:
        tankId = request.args.get("tankId")
        tanks_collection = db['tanks']
        tank_db = tanks_collection.find_one({"tank_name": tankId})
        print("fetching tank")
        print(tank_db)
        """executor = concurrent.futures.ThreadPoolExecutor()
        future = executor.submit(AsyncDataBaseManager.get_tank_parameters, tankId)
        future_result = future.result()"""
        
        tank_parameters = convert_tank_parameters()
        tank_parameters = [{
            "tankId": tank_db['tank_name'],
            "parameter": parameter_name,
            "tankMinValue": tank_db[parameter_name]['tank_min_value'],
            "tankMaxValue": tank_db[parameter_name]['tank_max_value'],
        } for parameter_name in ("WtrLvl", "OxygenPercentage", "Ph")]

        return make_response(jsonify(msg="Successfully fetched",
                                     parameters=tank_parameters,
                                     tankId=tankId), 200)
    except Exception as e:
        return make_response(jsonify(msg=str(e)), 500)


@api_blueprint.route("/update-tank", methods=["POST"])
@jwt_required()
@mongodb_handler
def update_tank(db, args, kwargs):
    try:
        tank_new_values = request.get_json()
        print("-------TANK ID NEW VALUES----------")
        del tank_new_values['accessToken']
        print(tank_new_values)
        tanks_collection = db['tanks']

        query = {"tank_name": tank_new_values['tankId']}
        new_values = {
            "$set": {
                "WtrLvl": {
                    "tank_min_value": tank_new_values['WtrLvlMin'],
                    "tank_max_value": tank_new_values['WtrLvlMax']
                },
                "OxygenPercentage": {
                    "tank_min_value": tank_new_values['OxygenPercentageMin'],
                    "tank_max_value": tank_new_values['OxygenPercentageMax']
                },
                "Ph": {
                    "tank_min_value": tank_new_values['PhMin'],
                    "tank_max_value": tank_new_values['PhMax']
                }
            }
        }
        tanks_collection.update_one(query, new_values)
        
        """executor = concurrent.futures.ThreadPoolExecutor(max_workers=6)
        future = executor.submit(AsyncDataBaseManager.update_tank_parameters, tank_new_values)
        future.result()"""

        return make_response(jsonify(msg="Succesfully updated"), 200)
    except Exception as e:
        return make_response(jsonify(msg=str(e)), 500)


@api_blueprint.route("/delete-tank", methods=["DELETE"])
@jwt_required()
@mongodb_handler
def delete_tank(db, args, kwargs):
    try:
        tank = request.get_json()
        del tank['accessToken']
        print("------------TANK NAME TO DELETE-----------")
        print(tank)
        tanks_collection = db['tanks']
        tanks_collection.delete_one({"tank_name": tank['tankId']})

        """executor = concurrent.futures.ThreadPoolExecutor()
        future = executor.submit(AsyncDataBaseManager.delete_tank, tank['tankId'])
        future.result()"""

        return make_response(jsonify(msg="Operation Succeded"), 200)
    except Exception as e:
        return make_response(jsonify(msg=str(e)), 500)


@api_blueprint.route("/fetch-historic", methods=["GET"])
@jwt_required()
@mongodb_handler
def fetch_historic(db, args, kwargs):
    company = request.args.get("company")
    print("---------PRINTING COMPANY----------")
    print(company)
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=6)
    get_historic_task = executor.submit(AsyncDataBaseManager.get_historic, db, company)
    historic_data = get_historic_task.result()

    return make_response(jsonify(msg="Successfully fetched", data=historic_data), 200)


@api_blueprint.route("/fetch-users", methods=["GET"])
@jwt_required()
@mongodb_handler
def fetch_users(db, args, kwargs):
    try:
        company = request.args.get("company")
        users_collection = db['users']

        users_db = [{
            "name": user_db['name'],
            "lastName": user_db['last_name'],
            "email": user_db['email'],
            "role": user_db['role']
        } for user_db in users_collection.find({"company": company})]
        print(users_db)
        
        """executor = concurrent.futures.ThreadPoolExecutor()
        future = executor.submit(AsyncDataBaseManager.get_users, company)
        users = future.result()
        print(users)"""

        return make_response(jsonify(msg="Success Fetching", users=users_db), 200)
    except Exception as e:
        return make_response(jsonify(msg=str(e)), 200)


@api_blueprint.route("/fetch-user", methods=["GET"])
@jwt_required()
@mongodb_handler
def fetch_user(db, args, kwargs):
    try:
        email = request.args.get("email")
        users_collection = db['users']

        user_db = users_collection.find_one({"email": email})
        user_db = {
            "id": str(user_db['_id']),
            "name": user_db['name'],
            "lastName": user_db['last_name'],
            "email": user_db['email'],
            "role": user_db['role']
        }
        print(user_db)
        """executor = concurrent.futures.ThreadPoolExecutor()
        future = executor.submit(AsyncDataBaseManager.get_user, email)"""
        return make_response(jsonify(msg="Succesfully fetched", user=user_db), 200)
    except Exception as e:
        return make_response(jsonify(msg=str(e)), 200)


@api_blueprint.route("/update-user", methods=["PUT"])
@jwt_required()
@mongodb_handler
def update_user(db, args, kwargs):
    try:
        new_user = request.get_json()
        del new_user['accessToken']

        new_user = new_user['user']
        print(new_user)

        users_collection = db['users']

        query = {"_id": ObjectId(new_user['id'])}
        new_values = {
            "$set": {
                "name": new_user['name'],
                "last_name": new_user['lastName'],
                "email": new_user['email'],
                "role": new_user['role'],
            }
        }
        user_updated_result = users_collection.update_one(query, new_values)
        user_updated = users_collection.find_one(query)
        print("UPDATE RESULT")
        print(user_updated)

        user_updated = {
            "id": str(user_updated['_id']),
            "name": user_updated['name'],
            "lastName": user_updated['last_name'],
            "email": user_updated['email'],
            "role": user_updated['role']
        }

        """executor = concurrent.futures.ThreadPoolExecutor()
        future = executor.submit(
            AsyncDataBaseManager.update_user_by_id, new_user['user'])
        updated_user = future.result()"""
        return make_response(jsonify(msg="Succesfully updated", user=user_updated), 200)
    except Exception as e:
        print(e)
        return make_response(jsonify(msg=str(e)), 500)


@api_blueprint.route("/delete-user", methods=["DELETE"])
@jwt_required()
@mongodb_handler
def delete_user(db, args, kwargs):
    try:
        body_json = request.get_json() 
        print(request.get_json())
        email = body_json.get("email", None)

        users_collection = db['users']
        users_collection.delete_one({"email": email})

        """executor = concurrent.futures.ThreadPoolExecutor()
        future = executor.submit(
            AsyncDataBaseManager.delete_user,
            email
        )
        result = future.result()"""

        return make_response(jsonify(msg="Operation Succeded"), 200)
    except Exception as e:
        return make_response(jsonify(msg=str(e)), 500)
