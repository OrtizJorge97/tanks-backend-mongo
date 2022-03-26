from flask import Blueprint
from flask_cors import CORS
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base
import os

main = Blueprint('main', __name__)
CORS(main, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

#ADD HERE DIFFERENTS BLUEPRINTS SO WE CAN MAKE THIS MODULAR - NOT TESTED YET
api_blueprint = Blueprint('api', __name__, url_prefix="/api")
CORS(api_blueprint, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

auth_blueprint = Blueprint('auth', __name__, url_prefix="/auth")
CORS(auth_blueprint, resources={r"/auth/*": {"origins": "*"}}, supports_credentials=True)

tank_api_blueprint = Blueprint('tank', __name__, url_prefix="/tank")
CORS(tank_api_blueprint, resources={r"/tank/*": {"origins": "*"}}, supports_credentials=True)

engine = create_engine(os.getenv('CONNECTION_STRING'), echo=True)
Session = sessionmaker(engine)
session = Session()
Base.metadata.create_all(engine)
print("tables created!")

from . import api, socket, auth, tanks_api