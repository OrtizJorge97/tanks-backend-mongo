from flask import request
from flask_socketio import join_room, leave_room, send, emit
from flask_jwt_extended import get_jwt

from .. import socketio
from . import auth_blueprint
from .models import *
from app.main.Services.database import mongodb_handler

sessionid_rooms = {}

@socketio.on('message', namespace="/private")
def message(data):
    print("message")

@socketio.on('connected', namespace="/private")
def connected(data):
    print("user has connected we")

@socketio.on('fromClient', namespace="/private")
def message(data):
    print(request.sid)
    #socketio.emit("fromflask", "Hola")
"""
@socketio.on('join', namespace="/private")
def on_join(data):
    username = data['username']
    session_id = request.sid
    room = data['room']
    sessionid_rooms[session_id] = room

    print(f"username(session id) {session_id} room {sessionid_rooms[session_id]}")
    
    join_room(room)
    emit('joined_room', username + ' has entered the room.', to=room)
"""

@socketio.on('send_message', namespace="/private")
def on_receive_message(data):
    username = data['username']
    message = data['message']
    room = sessionid_rooms[request.sid]
    print(f"username(session id) {username} is in room {request.sid}")

    emit('receive_message', message, to=room)

@socketio.on('leave', namespace="/private")
def on_leave(data):
    username = data['username']
    room = data['room']
    #leave_room(room)
    #send(username + ' has left the room.', to=room)

@socketio.on('join_user_sessionid', namespace="/private")
@mongodb_handler
def on_join(db, args, kwargs):
    print("PRINTING ARGS IN ON JOIN")
    print(args)
    print("PRINTING KWARGS IN ON JOIN")
    print(kwargs)
    print(request.sid)
    user = args[0]
    email = user["email"]
    company = user["company"] #this is used as the 'room' for private msgs
    session_id = request.sid

    user_collection = db['users']
    session_collection = db['sessions']
    session_db = session_collection.find_one({"session_token": session_id})
    user_db = user_collection.find_one({"email": email})

    if not session_db:
        session_collection.insert_one({
            "session_token": session_id,
            "user_id": user_db.get('_id', None)
        })

    join_room(company)
    print("user joined succesfully")
    emit('success_joinning', {"message": "Session succesfully joined"})





    """
    username = data['username']
    session_id = request.sid
    room = data['room']
    sessionid_rooms[session_id] = room

    print(f"username(session id) {session_id} room {sessionid_rooms[session_id]}")
    
    join_room(room)
    emit('joined_room', username + ' has entered the room.', to=room)
    """

"""
class Sessions(Base): #child table of users
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
    session_identifier = Column(Text)
    user_id = Column(Integer, ForeignKey('users.id'))
    """