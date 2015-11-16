#!/usr/bin/env python2.7
import os, json, eyed3
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, flash, session, url_for
from app import app
from forms import * 

# create postgres engine
DATABASEURI = "postgresql://ksj2114:833@w4111db1.cloudapp.net:5432/proj1part2"
engine = create_engine(DATABASEURI)

# connect to engine before every request
@app.before_request
def before_request():
    try:
        #connect to engine
        g.conn = engine.connect()
#       if 'username' in session:
#            # print username info for debugging
#            print 'Username: ' + str(session['username'])
#        else:
#            print 'Unknown user'
    # print errors if cannot connect to DB
    except:
        print "uh oh, problem connecting to database"
        import traceback; traceback.print_exc()
        g.conn = None

# close connection after page request finished
@app.teardown_request
def teardown_request(exception):
    try:
        g.conn.close()
    except Exception as e:
        pass

# home page
@app.route('/', methods=["POST", "GET"])
def index():
    return render_template("index.html")

# page to upload podcast information
@app.route('/upload', methods=["POST", "GET"])
def upload():

    # create new uploadform
    form = UploadForm()

    # extract form info if 'POST'
    if request.method == 'POST':

        if form.validate() == False:
            return render_template('upload.html', form=form)
        else:

            # extract form data
            oid = form.oid.data
            name = form.name.data
            poddate = form.poddate.data
            descr = form.descr.data
            oid.encode('ascii', 'replace')
            name.encode('ascii', 'replace')
            poddate.encode('ascii', 'replace')
            descr.encode('ascii', 'replace')

            # insert podcast information into podcasts table
            q = "INSERT INTO podcasts(oid, name, date, descr) values (%s,%s,%s,%s);"
            cursor = g.conn.execute(q,(oid, name, poddate, descr,))
            cursor.close()
            print "New podcast inserted"

            # return upload.html
            return redirect(url_for('upload'))

    elif request.method == 'GET':
        return render_template('upload.html', form=form)

# signup page
@app.route('/signup', methods=["POST", "GET"])
def signup():

    # create signup form
    form = SignupForm()

    # if username is already logged in, return profile page
    if 'username' in session:
        return redirect(url_for('profile'))

    # if 'POST', extract form data
    if request.method == 'POST':
        if form.validate() == False:
            return render_template('signup.html', form=form)
        else:
            # extract form data
            username = form.username.data
            email = form.email.data
            password = form.password.data
            username.encode('ascii', 'replace')
            email.encode('ascii', 'replace')
            password.encode('ascii', 'replace')
           
            # insert user information into users table
            q = "INSERT INTO Users(username, pwd, email) VALUES (%s,%s,%s);" 
            cursor = g.conn.execute(q,(username, password, email,))
            cursor.close()
            session['username'] =username 

            # return profile page
            return redirect(url_for('profile'))

    elif request.method == 'GET':
        return render_template('signup.html', form=form)

# profile page
@app.route('/profile', methods=["POST", "GET"])
def profile():

    # if user is not signed in, return signin page
    if 'username' not in session:
        return redirect(url_for('signin'))
   
    # fetch user id
    username = session['username'] 
    n = "SELECT u.uid FROM users as u WHERE u.username=%s;"
    cursor = g.conn.execute(n, (username,))
    uids = cursor.fetchone()
    uid = uids['uid']
    cursor.close()

    # 'POST' requests are used to send tags 
    if request.method == 'POST':

        # delete all tags for this user 
        r = "DELETE FROM chooses as c WHERE c.uid = %s;"
        g.conn.execute(r, (uid,));

        # insert user-selected tags into database
        tags = json.loads(request.form['tag'])
        for tag in tags:
            tag.encode('ascii', 'replace')
           
            # retrieve tag id
            n = "SELECT t.tid FROM tags as t WHERE t.name = %s;"
            cursor = g.conn.execute(n,(tag,))
            tids = cursor.fetchone()
            tid = tids['tid']
            cursor.close()

            # insert uid, tid pair into chooses table
            q = "INSERT INTO chooses(uid, tid) values(%s,%s);"
            cursor = g.conn.execute(q, (uid, tid,))
            cursor.close()

        return ('', 204)

    elif request.method == 'GET':
       
        # Send all tags
        all_tags = []
        p = "SELECT t.name FROM tags AS t;"
        cursor = g.conn.execute(p)
        for result in cursor:
            all_tags.append(result['name'])
        cursor.close()

        # send tags for this user
        my_tags = []
        q = "SELECT t.name FROM tags as t INNER JOIN chooses as c ON c.tid = t.tid WHERE c.uid = %s;" 
        cursor = g.conn.execute(q, (uid,)) 
        for result in cursor:
            my_tags.append(result['name'])
        cursor.close()
        return render_template('profile.html', all_tags=all_tags, my_tags=my_tags)

# The play page is the page that plays podcasts
@app.route('/play')
def play():

    # if user is not signed in, return signin page
    if 'username' not in session:
        return redirect(url_for('signin'))
     
    username = session['username']
   
    # Query returns one podcast that hasn't been listened
    # to by the user, that matches a selected tag
    q = "SELECT p.name, p.date, p.descr, p.pid FROM users as u \
        INNER JOIN chooses as c ON u.uid = c.uid \
        INNER JOIN tags as t ON c.tid = t.tid \
        INNER JOIN described_by as d ON t.tid = d.tid \
        INNER JOIN podcasts as p ON d.pid = p.pid \
        WHERE u.username = %s AND p.pid NOT IN \
        (SELECT r.pid FROM records as r \
        INNER JOIN users as u ON r.uid = u.uid \
        WHERE u.username =  %s) LIMIT 1;" 

    # extract podcast information
    cursor = g.conn.execute(q, (username,username,))
    podcasts = cursor.fetchone()
    if podcasts is None:
        return redirect(url_for('profile')) 

    podcast_name = podcasts['name'].encode('ascii', 'replace')
    podcast_descr = podcasts['descr'].encode('ascii', 'replace')
    pid = podcasts['pid']
    cursor.close()


    q = "SELECT u.uid FROM users as u WHERE u.username=%s;"
    cursor = g.conn.execute(q, (username,))
    uids = cursor.fetchone()
    uid = uids['uid']
    cursor.close()
   
    # insert podcast info into the records table
    q = "INSERT INTO records(pid, uid) values (%s,%s)"
    cursor = g.conn.execute(q, (pid, uid,))
    cursor.close()
   
    # update the playcount for the podcast
    q = "UPDATE podcasts SET playcount = playcount + 1 WHERE pid =%s"
    cursor = g.conn.execute(q, (pid,))
    cursor.close()
    
    dir = os.path.dirname(__file__)
    tag = eyed3.load(os.path.join(dir, 'static/assets/test.mp3')).tag
    
    metadata = {"descr": podcast_descr}
    metadata['artist'] = tag.artist
    metadata['album'] = tag.album
    metadata['title'] = tag.title

    print podcast_descr
    return render_template('play.html', podcast = podcast_name, metadata = metadata)

@app.route('/about')
def about():
   return render_template('about.html')

# org page displays analytics
@app.route('/org', methods=['GET', 'POST'])
def org():

    # return orgsignin if org is not in session
    if 'orguser' not in session:
        return redirect(url_for('orgsignin'))
     
    usr = session['orguser']
    podcast_info={}

    # retrieve podcast playcount into from podcasts table
    q = "SELECT p.name, p.playcount FROM podcasts as p INNER JOIN orgs as o ON p.oid = o.oid WHERE o.usr =%s"
    cursor = g.conn.execute(q,(usr,))

    # add playcount info to dict 
    for result in cursor:
        podcast_info[result['name']] = result['playcount']

    return render_template('org.html', info = podcast_info)

# orgsignin page
@app.route('/orgsignin', methods=['GET', 'POST'])
def orgsignin():
    form = OrgSigninForm()

    # if orguser is already signed in, return org page
    if 'orguser' in session:
        return redirect(url_for('org'))

    if request.method == 'POST':

        # validate form
        if form.validate == False:
            return render_template('orgsignin.html', form=form)
        else:
            session['orguser'] = form.username.data
            return redirect(url_for('org'))
    elif request.method == 'GET':
        return render_template('orgsignin.html', form=form)

# signin page
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    form = SigninForm()
  
    # if user is already signed in
    if 'username' in session:
        return redirect(url_for('profile'))

    if request.method == 'POST':

        # validate form
        if form.validate() == False:
            return render_template('signin.html', form=form)
        else:
            session['username'] = form.username.data
            return redirect(url_for('profile'))

    elif request.method == 'GET':
        return render_template('signin.html', form=form)

# user signout
@app.route('/signout')
def signout():
    if 'username' not in session:
        return redirect(url_for('signin'))

    session.pop('username', None)
    return redirect(url_for('signin'))

# orguser signout
@app.route('/orgsignout')
def orgsignout():
    if 'orguser' not in session:
        return redirect(url_for('orgsignin'))

    session.pop('orguser', None)
    return redirect(url_for('signin'))

    return redirect(url_for('index'))
