#!/usr/bin/env python2.7
import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, flash, session, url_for
from app import app
from forms import * 
from models import *

DATABASEURI = "sqlite:///test.db"

engine = create_engine(DATABASEURI)

engine.execute("""DROP TABLE IF EXISTS test;""")
engine.execute("""CREATE TABLE IF NOT EXISTS test (
    id serial,
    name text,
    email text
);""")
engine.execute("""CREATE TABLE IF NOT EXISTS Users (
    uid serial,
    firstname text,
    lastname text,
    email text,
    password text,
    PRIMARY KEY(uid)
);""")


@app.before_request
def before_request():
    try:
        g.conn = engine.connect()
    except:
        print "uh oh, problem connecting to database"
        import traceback; traceback.print_exc()
        g.conn = None

@app.teardown_request
def teardown_request(exception):
    try:
        g.conn.close()
    except Exception as e:
        pass


@app.route('/', methods=["POST", "GET"])
def index():
    print request.args
    cursor = g.conn.execute("SELECT name FROM test")
    names = []
    for result in cursor:
        names.append(result['name'])  # can also be accessed using result[0]
    cursor.close()
    context = dict( data = names )
    return render_template("index.html", **context)

# from tutorial http://code.tutsplus.com/tutorials/intro-to-flask-signing-in-and-out--net-29982
@app.route('/signup', methods=["POST", "GET"])
def signup():
    form = SignupForm()
    if request.method == 'POST':
        if form.validate() == False:
            return render_template('signup.html', form=form)
        else:
            firstname = str(form.firstname.data)
            lastname = str(form.lastname.data)
            email = str(form.email.data)
            password = str(form.password.data)
            
            q = "INSERT INTO Users(firstname, lastname, email, password) VALUES (?, ?, ?, ?);" 
            cursor = g.conn.execute(q,(firstname, lastname, email, password,))
            cursor.close()
            session['email'] = email
            return redirect(url_for('profile'))

    elif request.method == 'GET':
        return render_template('signup.html', form=form)

@app.route('/profile')
def profile():
    if 'email' not in session:
        return redirect(url_for('signin'))
        
    q = "SELECT email FROM Users WHERE email=?"
    email = session['email']
    cursor = g.conn.execute(q, (email,))
    user = cursor.fetchone()
    if user is None:
        return redirect(url_for('signin'))
    else:
        return render_template('profile.html')


@app.route('/contact')
def contact():
    form = ContactForm()
    if request.method == 'POST':
        if form.validate() == False:
            flash('All fields are required.')
            return render_template('contact.html', form=form)
        else:
            return "Form posted"

    elif request.method == 'GET':
        return render_template('contact.html', form=form)

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    form = SigninForm()
    
    if request.method == 'POST'
        if form.validate() == False
            return render_template('signin.html', form=form
        else:
            session['email'] = form.email.data
            return redirect(url_for('profile'))

    elif request.method == 'GET':
        return render_template('signin.html', form=form)

