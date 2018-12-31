from flask import Flask
import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

DEBUG = os.environ.get("DEBUG")
DATABASE_URL = os.environ.get("DATABASE_URL")
SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get(
    "SQLALCHEMY_TRACK_MODIFICATIONS")
SECRET_KEY = os.environ.get("SECRET_KEY")
PORT = int(os.environ.get("PORT", 5000))

print('this is the port', PORT)
print('this is the debug', DEBUG)

# app = Flask(__name__)
# app.config['DEBUG'] = DEBUG
# app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
# app.config['SECRET_KEY'] = SECRET_KEY
