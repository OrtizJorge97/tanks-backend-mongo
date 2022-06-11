from flask import Flask, request, Blueprint, jsonify, make_response
import concurrent.futures
from flask_socketio import emit
import threading

from . import tank_api_blueprint
from .models import *
from .. import socketio
from .Services.database import AsyncDataBaseManager
from app.main.Services.notifications import send_tank_alert_mail
from app.main.Services.database import mongodb_handler

# DATA TO RECEIVE FROM TANKS AND TO SAVE IT INTO HISTORIC DATA


@tank_api_blueprint.route("/post-data", methods=["POST"])
@mongodb_handler
def post_data(db, args, kwargs):
    try:
        body_json = request.get_json()
        tanks_data = body_json['tanks_data']
        """tanks_data = [{
            "_id": str(tank_data['id'],
            "wtrLvlValue": tank_data["timestamp"],
            "oxygenPercentageValue": tank_data["timestamp"],
            "phValue": tank_data["timestamp"],
            "timestamp": tank_data["timestamp"],
            "company": tank_data["company"]
        } for tank_data in tanks_data]"""
        print("-----IN TANKS POST DATA-------")
        print(body_json)
        company = body_json['company']

        def update_dashboard():
            socketio.emit('tanks_data', tanks_data, namespace='/private', to=company)
            socketio.emit('get_tank_data', tanks_data, namespace='/private', to=company)
            socketio.emit('get_historic_data', tanks_data, namespace='/private', to=company)

        executor = concurrent.futures.ThreadPoolExecutor(max_workers=6) 
        dashboard_task = threading.Thread(target=update_dashboard, daemon=True)
        dashboard_task.start()
        #dashboard_tasks = [executor.submit(socketio.emit, destination, tanks_data, namespace='/private', to=company) for destination in ['tanks_data', 'get_tank_data', 'get_historic_data']]

        print("TANKS DATA WEE")
        print(tanks_data)
        store_measurements_task = executor.submit(AsyncDataBaseManager.store_measurements, db, tanks_data)
        company_staff_task = executor.submit(AsyncDataBaseManager.get_company_staff_emails, db, company) #get companies emails for administrators and supervisors
        tanks_parameters_task = executor.submit(AsyncDataBaseManager.get_company_tanks_parameters, db, company)
        
        store_measurements_task.result()
        email_results = company_staff_task.result()
        tanks_parameters_results = tanks_parameters_task.result()
        print("SENDING TANKS ALERT MESSAGE")
        send_tanks_alerts = executor.submit(send_tank_alert_mail, email_results, tanks_parameters_results, tanks_data)
        send_tanks_alerts.result()
        
        #dashboard_results = [dashboard_task.result() for dashboard_task in dashboard_tasks]


        #emit('tanks_data', payload, namespace='/private', to=company)
        for tank_data in tanks_data:
            tank_data['_id'] = str(tank_data['_id'])

        print("BEFORE SENDING DATA TO SOCKETS")
        print(tanks_data)
        #socketio.emit('tanks_data', tanks_data, namespace='/private', to=company)
        #socketio.emit('get_tank_data', tanks_data, namespace='/private', to=company)
        #socketio.emit('get_historic_data', tanks_data, namespace='/private', to=company)
        return make_response(jsonify(msg="Success"), 200)
    except Exception as e:
        print(str(e))
        return make_response(jsonify(msg=str(e)), 500)

# DATA TO RECEIVE FROM TANKS AND TO SAVE IT INTO HISTORIC DATA
@tank_api_blueprint.route("/fetch-tanks", methods=["GET"])
@mongodb_handler
def fetch_tanks(db, args, kwargs):
    print("sdsddddddd")
    try:
        company = request.args.get('company')

        executor = concurrent.futures.ThreadPoolExecutor()

        get_company_tanks_task = executor.submit(AsyncDataBaseManager.get_company_tanks, db, company) #get company tanks
        #get_tanks_parameters_task = executor.submit(AsyncDataBaseManager.get_tanks_parameters, company)

        tanks_parameters_list = get_company_tanks_task.result()
        #tanks_parameters = get_tanks_parameters_task.result()

        """tanks_parameters_list = []
        for tank_id in tanks_company:
            tank_parameters_dict = {
                'id': tank_id,
                "WtrLvlMin": None,
                "WtrLvlMax": None,
                "OxygenPercentageMin": None,
                "OxygenPercentageMax": None,
                "PhMin": None,
                "PhMax": None
            }
            for tank_parameter_tuple in tanks_parameters:
                if tank_parameter_tuple[0] == tank_id:
                    tank_parameters_dict[f"{tank_parameter_tuple[1]}Min"] = tank_parameter_tuple[2]
                    tank_parameters_dict[f"{tank_parameter_tuple[1]}Max"] = tank_parameter_tuple[3]
            tanks_parameters_list.append(tank_parameters_dict)
        print(tanks_parameters_list)"""

        return make_response(jsonify(msg="Success fetching", tanks=tanks_parameters_list), 200)
    except Exception as e:
        return make_response(jsonify(msg=str(e)), 500)


