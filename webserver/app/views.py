#!/usr/bin/env python2.7
import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, flash
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
engine.execute("""DROP TABLE IF EXISTS Users;""")
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
            return "[1] Create a new user [2] sign in the user [3] redirect to the user's profile"
    elif request.method == 'GET':
        return render_template('signup.html', form=form)

@app.route('/contact')
def contact():
    form = ContactForm()
    if request.method == 'POST':
        return 'Form posted.'

    elif request.method == 'GET':
        return render_template('contact.html', form=form)

