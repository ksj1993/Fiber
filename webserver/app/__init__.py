from flask import Flask
import os
from flask.ext.login import LoginManager
from flask.ext.openid import OpenID

app = Flask(__name__)
app.config.from_object('config')
app.secret_key = 'development key'

from app import views
