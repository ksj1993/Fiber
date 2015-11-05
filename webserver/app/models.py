# Sample code from http://code.tutsplus.com/tutorials/intro-to-flask-signing-in-and-out--net-29982
from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'Users'
    uid = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String())
    email = db.Column(db.String())
    pwd = db.Column(db.String())

    def __init__(self, username, email, pwd):
        self.username = username 
        self.email = email.lower()
        self.set_password(pwd)
    
    def set_password(self, pwd):
        self.pwd = generate_password_hash(pwd)

    def check_password(self, pwd):
        return check_password_hash(self.pwd, pwd)
