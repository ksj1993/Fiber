#!/usr/bin/env python2.7
import os, json
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
        if 'username' in session:
            print 'Username: ' + str(session['username'])
        else:
            print 'Unknown user'
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

@app.route('/org', methods=["POST", "GET"])
def org():
    
    return render_template("org.html")

@app.route('/', methods=["POST", "GET"])
def index():
    return render_template("index.html")

@app.route('/upload', methods=["POST", "GET"])
def upload():
    form = UploadForm()

    if request.method == 'POST':
        if form.validate() == False:
            return render_template('upload.html', form=form)
        else:
            oid = form.oid.data
            name = form.name.data
            poddate = form.poddate.data
            descr = form.descr.data
            oid.encode('ascii', 'replace')
            name.encode('ascii', 'replace')
            poddate.encode('ascii', 'replace')
            descr.encode('ascii', 'replace')
            q = "INSERT INTO podcasts(oid, name, date, descr) values (%s,%s,%s,%s);"
            cursor = g.conn.execute(q,(oid, name, poddate, descr,))
            cursor.close()
            print "New podcast inserted"
            return redirect(url_for('upload'))
    elif request.method == 'GET':
        return render_template('upload.html', form=form)

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
            username = form.username.data
            email = form.email.data
            password = form.password.data
            username.encode('ascii', 'replace')
            email.encode('ascii', 'replace')
            password.encode('ascii', 'replace')
            
            q = "INSERT INTO Users(username, pwd, email) VALUES (%s,%s,%s);" 
            cursor = g.conn.execute(q,(username, password, email,))
            cursor.close()
            session['username'] =username 
            return redirect(url_for('profile'))

    elif request.method == 'GET':
        return render_template('signup.html', form=form)

@app.route('/profile', methods=["POST", "GET"])
def profile():
    if 'username' not in session:
        return redirect(url_for('signin'))
    
    username = session['username'] 
    n = "SELECT u.uid FROM users as u WHERE u.username=%s;"
    cursor = g.conn.execute(n, (username,))
    uids = cursor.fetchone()
    uid = uids['uid'].encode('ascii', 'replace')
    cursor.close()
 
    if request.method == 'POST':
        tags = json.loads(request.form['tag'])

        for tag in tags:
            tag.encode('ascii', 'replace')
            
            n = "SELECT t.tid FROM tags as t WHERE t.name = %s;"
            cursor = g.conn.execute(n,(tag,))
            tids = cursor.fetchone()
            tid = tids['tid'].encode('ascii','replace')
            cursor.close()

            q = "INSERT INTO chooses(uid, tid) values(%s,%s);"
            cursor = g.conn.execute(q, (uid, tag,))
            cursor.close()

        return ('', 204)

    elif request.method == 'GET':
       
        # Give back all_tags and user_tags

        all_tags = []
        p = "SELECT t.name FROM tags AS t;"
        cursor = g.conn.execute(p)
        for result in cursor:
            all_tags.append(result['name'])
        cursor.close()

        q = "SELECT t.name FROM tags as t INNER JOIN chooses as c ON c.tid = t.tid WHERE c.uid = %s;" 

        my_tags = []
        cursor = g.conn.execute(q, (username,)) 
        for result in cursor:
            my_tags.append(result['name'])
        cursor.close()
        print my_tags
        return render_template('profile.html', all_tags=all_tags, my_tags=my_tags)

@app.route('/play')
def play():
   
    if 'username' not in session:
        return redirect(url_for('signin'))
     
    username = session['username']
    
    q = "SELECT p.name FROM users as u \
        INNER JOIN chooses as c ON u.uid = c.uid \
        INNER JOIN tags as t ON c.tid = t.tid \
        INNER JOIN described_by as d ON t.tid = d.tid \
        INNER JOIN podcasts as p ON d.pid = p.pid \
        WHERE u.username = %s AND p.pid NOT IN \
        (SELECT r.pid FROM records as r \
        INNER JOIN users as u ON r.uid = u.uid \
        WHERE u.username =  %s) LIMIT 1;" 

    cursor = g.conn.execute(q, (username,username,))
    podcasts = cursor.fetchone()
    podcast = podcasts['name'].encode('ascii', 'replace')
    cursor.close()


    n = "SELECT p.pid FROM podcasts as p WHERE p.name=%s;"
    cursor = g.conn.execute(n, (podcast,))
    pids = cursor.fetchone()
    pid = pids['pid']
    cursor.close()
    
    n = "SELECT u.uid FROM users as u WHERE u.username=%s;"
    cursor = g.conn.execute(n, (username,))
    uids = cursor.fetchone()
    uid = uids['uid']
    cursor.close()
    
    p = "INSERT INTO records(pid, uid) values (%s,%s)"
    cursor = g.conn.execute(p, (pid, uid,))
    cursor.close()
    print "Inserted record into records table"
    return render_template('play.html', podcast = podcast)

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
