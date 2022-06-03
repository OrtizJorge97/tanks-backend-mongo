from flask import Flask
from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager
from itsdangerous import URLSafeTimedSerializer

from datetime import timedelta
import os

from dotenv import load_dotenv

load_dotenv()

front_url = os.getenv('FRONT_URL')
host_url = os.getenv('HOST_URL')
email_salt = os.getenv('EMAIL_SALT_TOKEN')
mail_user = os.getenv('MAIL_USER')
mail_password = os.getenv('MAIL_PASSWORD')
smtp_server_string = os.getenv('SMTP_SERVER')
port = os.getenv('SSL_PORT')

socketio = SocketIO(cors_allowed_origins='*')
app = Flask(__name__)
app.debug = True

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config["JWT_SECRET_KEY"] = os.getenv('JWT_SECRET_KEY')
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=2) #normal token expires
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(hours=24) #refresh token expire time
#refresh token is for using when you want to refresh the normal token.
#this refresh token also expires, but can be renew by logging in again, this must have a 
#longer time than normal token

ts = URLSafeTimedSerializer(app.config["SECRET_KEY"])

from .main import main
app.register_blueprint(main)

from .main import api_blueprint
app.register_blueprint(api_blueprint)

from .main import auth_blueprint
app.register_blueprint(auth_blueprint)

from .main import tank_api_blueprint
app.register_blueprint(tank_api_blueprint)

jwt = JWTManager(app)
socketio.init_app(app)

"""
def create_app(debug=False):
    app = Flask(__name__)
    app.debug = debug
    app.config['SECRET_KEY'] = 'gjr39dkjn344_!67#'

    from .main import main
    app.register_blueprint(main)

    from .main import api_blueprint
    app.register_blueprint(api_blueprint)

    from .main import models
    print("1")
    engine = create_engine('mysql://flask:flask_password@localhost/tanks_db', echo=True)
    Session = sessionmaker(engine)
    session = Session()
    print("2")
    models.Base.metadata.create_all(engine)
    print("tables created!")

    socketio.init_app(app)
    return app
"""