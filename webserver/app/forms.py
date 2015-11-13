from flask.ext.wtf import Form 
from wtforms import TextField, TextAreaField, SubmitField, PasswordField, validators
from models import db, User
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from app import app
from flask import g

 
class ContactForm(Form):
    name = TextField("Name", [validators.Required()])
    email = TextField("Email", [validators.Required(), validators.Email()])
    subject = TextField("Subject", [validators.Required()])
    message = TextAreaField("Message", [validators.Required()])
    submit = SubmitField("Send")

class UploadForm(Form):
    oid = TextField("oid",  [validators.Required("Please enter oid")])
    name = TextField("name",  [validators.Required("Please podcast name")])
    poddate = TextField('poddate', [validators.Required("Please enter podcast date")])
    descr = TextField('descr', [validators.Required("Please enter podcast descr")])

    submit = SubmitField("Upload podcast")
    
    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
    
    def validate(self):
        if not Form.validate(self):
            return False
        return True


class SignupForm(Form):
    username = TextField("Username",  [validators.Required("Please enter your last name.")])
    email = TextField("Email",  [validators.Required("Please enter your email address."), validators.Email("Please enter a valid email address.")])
    password = PasswordField('Password', [validators.Required("Please enter a password.")])
    submit = SubmitField("Create account")
    
    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
    
    def validate(self):
        if not Form.validate(self):
            return False
        q = "SELECT  FROM Users WHERE email = %s"        
        cursor = g.conn.execute(q, (self.email.data.lower(),))
        if cursor.fetchone():
            print "Email is taken"
            cursor.close()
            return False

#return False
        cursor.close()
        return True

class SigninForm(Form):
    username = TextField("Username", [validators.Required("Please enter your username")])
    password = PasswordField('Password', [validators.Required("Please enter a password")])
    submit = SubmitField("Sign In")

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        if not Form.validate(self):
            return False

        q = "SELECT * FROM Users WHERE username = %s"
        cursor = g.conn.execute(q, (self.username.data,))
        user = cursor.fetchone()
        
        # TODO implement password hashing via models?
        #user = User(user['username'], user['pwd'], user['email'])
        if user and user['pwd'] == self.password.data: 
            return True
        else:
            self.username.errors.append("Invalid username or password")
            return False

