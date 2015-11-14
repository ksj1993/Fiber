from flask.ext.wtf import Form 
from wtforms import TextField, TextAreaField, SubmitField, PasswordField, validators
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from app import app
from flask import g

# Form to upload information about podcasts 
class UploadForm(Form):
    # podcasts are associated with orgs. User enters name, date, and descr
    oid = TextField("oid",  [validators.Required("Please enter oid")])
    name = TextField("name",  [validators.Required("Please podcast name")])
    poddate = TextField('poddate', [validators.Required("Please enter podcast date")])
    descr = TextField('descr', [validators.Required("Please enter podcast descr")])
    submit = SubmitField("Upload podcast")
    
    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
   
    # validate form
    def validate(self):
        if not Form.validate(self):
            return False
        return True

# User signup form.
class SignupForm(Form):
    # Users have usernames, emails and passwords
    username = TextField("Username",  [validators.Required("Please enter your last name.")])
    email = TextField("Email",  [validators.Required("Please enter your email address."), validators.Email("Please enter a valid email address.")])
    password = PasswordField('Password', [validators.Required("Please enter a password.")])
    submit = SubmitField("Create account")
    
    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
   
    # validate form
    def validate(self):
        if not Form.validate(self):
            return False

        # users must have unique email addresses
        q = "SELECT  FROM Users WHERE email = %s"        
        cursor = g.conn.execute(q, (self.email.data.lower(),))
        if cursor.fetchone():
            print "Email is taken"
            cursor.close()
            
            # Return false if email is taken
            return False

        cursor.close()
        return True

# Signin form for organizations
class OrgSigninForm(Form):
    # organizations have usernames and passwords (no email address)
    username = TextField("Username", [validators.Required("Please enter your username")])
    password = PasswordField('Password', [validators.Required("Please enter a password")])
    submit = SubmitField("Sign In")

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    # validate form using default
    def validate(self):
        if not Form.validate(self):
            return False

        # retrieve organization user from orgs table
        q = "SELECT * FROM orgs WHERE usr = %s"
        cursor = g.conn.execute(q, (self.username.data,))
        user = cursor.fetchone()
        cursor.close() 
        
        # check user object for password
        if user and user['pwd'] == self.password.data: 
            return True
        else:
            self.username.errors.append("Invalid username or password")
            return False

# Signin form for application users
class SigninForm(Form):
    # users sign in with username and passwords
    username = TextField("Username", [validators.Required("Please enter your username")])
    password = PasswordField('Password', [validators.Required("Please enter a password")])
    submit = SubmitField("Sign In")

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    # validate form (correct user credentials)
    def validate(self):
        if not Form.validate(self):
            return False

        # Retrieve user from users table
        q = "SELECT * FROM Users WHERE username = %s"
        cursor = g.conn.execute(q, (self.username.data,))
        user = cursor.fetchone()
        cursor.close() 
        
        # check user credentials
        if user and user['pwd'] == self.password.data: 
            return True
        else:
            self.username.errors.append("Invalid username or password")
            return False

