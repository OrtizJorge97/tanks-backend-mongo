from flask import Flask
from flask_socketio import SocketIO, send

import os
import sys

from app import app, socketio
from app.main import models

#from app import create_app, socketio

#app = create_app(debug=True)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
print(f"Project root: {ROOT_DIR}")
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

if __name__ == '__main__':
    print("Socket IO has started!")
    socketio.run(app)

"""

app = Flask(__name__)
app.config["SECRET_KEY"] = "mysecret"

socketio = SocketIO(app, cors_allowed_origins='*')

if __name__ == "__main__":
    socketio.run(app)
    print("Socket IO Server Started!")
"""