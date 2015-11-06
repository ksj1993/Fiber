#!/usr/bin/env python2.7
import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, flash, session, url_for
from app import app
from forms import * 
from models import *

DATABASEURI = "postgresql://ksj2114:833@w4111db1.cloudapp.net:5432/proj1part2"
engine = create_engine(DATABASEURI)

music_dir = '/home/azureuser/Fiber/webserver/static'

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
    return render_template("index.html")

# from tutorial http://code.tutsplus.com/tutorials/intro-to-flask-signing-in-and-out--net-29982
@app.route('/signup', methods=["POST", "GET"])
def signup():
    form = SignupForm()

    if 'username' in session:
        return redirect(url_for('profile'))
    if request.method == 'POST':
        if form.validate() == False:
            return render_template('signup.html', form=form)
        else:
            username = str(form.username.data)
            email = str(form.email.data)
            password = str(form.password.data)
            
            q = "INSERT INTO Users(username, password, email) VALUES (%s,%s,%s);" 
            cursor = g.conn.execute(q,(username, pwd, email,))
            cursor.close()
            session['username'] =username 
            return redirect(url_for('profile'))

    elif request.method == 'GET':
        return render_template('signup.html', form=form)

@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('signin'))
        
    q = "SELECT username FROM Users WHERE username=%s"
    username = session['username']
    cursor = g.conn.execute(q, (username,))
    user = cursor.fetchone()
    cursor.close()
    if user is None:
        return redirect(url_for('signin'))
    else:
        tags = []
        q = "SELECT t.name as name FROM users as u INNER JOIN chooses as c \
            ON u.uid = c.uid INNER JOIN tags as t ON c.tid = t.tid WHERE u.username = %s" 
        cursor = g.conn.execute(q, (username,)) 
        for result in cursor:
            tags.append(result['name'])
        cursor.close()

        podcasts = []
        q = "SELECT p.name as name FROM users as u INNER JOIN chooses as c ON u.uid = c.uid \
             INNER JOIN tags as t ON c.tid = t.tid INNER JOIN described_by as d  \
             ON t.tid = d.tid INNER JOIN podcasts as p ON d.pid = p.pid WHERE u.username = %s"
        cursor = g.conn.execute(q, (username,))
        for result in cursor:
            podcasts.append(result['name'])
        cursor.close()
        return render_template('profile.html', tags=tags, podcasts=podcasts)

@app.route('/static/<filename>')
def play(filename):
    return render_template('play.html', music_file=filename)

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
   
    if 'username' in session:
        return redirect(url_for('profile'))

    if request.method == 'POST':
        if form.validate() == False:
            return render_template('signin.html', form=form)
        else:
            session['username'] = form.username.data
            return redirect(url_for('profile'))

    elif request.method == 'GET':
        return render_template('signin.html', form=form)

@app.route('/signout')
def signout():
    if 'username' not in session:
        return redirect(url_for('signin'))

    session.pop('username', None)
    return redirect(url_for('index'))
