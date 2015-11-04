from flask.ext.wtf import Form 
from wtforms import TextField, TextAreaField, SubmitField, PasswordField, validators
from models import db, User
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from app import app
from flask import g

DATABASEURI = "sqlite:///test.db"
engine = create_engine(DATABASEURI)
 
class ContactForm(Form):
    name = TextField("Name", [validators.Required()])
    email = TextField("Email", [validators.Required(), validators.Email()])
    subject = TextField("Subject", [validators.Required()])
    message = TextAreaField("Message", [validators.Required()])
    submit = SubmitField("Send")

class SignupForm(Form):
    firstname = TextField("First name",  [validators.Required("Please enter your first name.")])
    lastname = TextField("Last name",  [validators.Required("Please enter your last name.")])
    email = TextField("Email",  [validators.Required("Please enter your email address."), validators.Email("Please enter your email address.")])
    password = PasswordField('Password', [validators.Required("Please enter a password.")])
    submit = SubmitField("Create account")
    
    def __init__(self, *args, **kwards):
        Form.__init__(self, *args, **kwargs)
        g.conn = engine.connect()
    
    def validate(self):
        if not Form.validate(self):
            return False
        
        cursor = g.conn.execute("SELECT email FROM Users WHERE email = " + self.email.data.lower())
        if cursor[0]:
            self.email.errors.append("Email already taken")
            cursor.close()
#return False
        cursor.close()
        return True

            
    

