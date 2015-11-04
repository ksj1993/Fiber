from flask import Flask
import os
from flask.ext.login import LoginManager
from flask.ext.openid import OpenID

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.config.from_object('config')
app.secret_key = 'development key'

from app import views
