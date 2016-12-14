from flask import Flask, request, render_template, make_response, redirect, url_for, session, flash
from flask_restful import Resource, Api, reqparse
from flask.ext.mysql import MySQL
from oauth2client import client
import traceback
from werkzeug.utils import secure_filename
import os

class Event:
    def __init__(self, name, date, time, location, org_name):
        self.name = name
        self.date = date
        self.time = time
        self.location = location
        self.org_name = org_name

class Setup:

    def __init__(self, event_name, setter_upper, attendee, status, member):
        self.event_name = event_name
        self.setter_upper = setter_upper
        self.attendee = attendee
        self.status = status
        self.member = member

class Friend:
    def __init__(self, netid, name):
        self.name = name
        self.netid = netid

class Match:
    #other_netid is either the person who set you up or the netid of the person you set up,
    #depending on what kind of Match it is
    def __init__(self, match_netid, match_name, event, other_name, dorm):
        self.match_netid = match_netid
        self.match_name = match_name
        self.event = event
        self.other_name = other_name
        self.dorm = dorm

class User:
    def __init__(self, netid, name, year, bio, hometown, gender, interested_in, dorm, major):
        self.netid = netid
        self.name = name
        self.year = year
        self.bio = bio
        self.hometown = hometown
        self.gender = gender
        self.interested_in = interested_in
        self.dorm = dorm
        self.major = major


mysql = MySQL()
app = Flask(__name__)
api = Api(app)

app.config['MYSQL_DATABASE_USER'] = 'mconnol6'
app.config['MYSQL_DATABASE_PASSWORD'] = 'grouppw'
app.config['MYSQL_DATABASE_DB'] = 'mconnol6'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_PORT'] = 3306
app.config['SECRET_KEY'] = 'this should be changed'
app.config['UPLOAD_FOLDER'] = './static'

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

mysql.init_app(app)

def get_all_interests():
    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute('select name from interest;')

    data = cursor.fetchall()

    interests = []
    for d in data:
        interests.append(d[0])

    return interests

def get_all_dorms():
    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute('select name from dorm;')

    data = cursor.fetchall()

    dorms = []

    for d in data:
        dorms.append(d[0])

    return dorms

def get_match(setter_upper, attendee, event):
    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.callproc('GetPotentialMatchList', (event, setter_upper, attendee))

    data = cursor.fetchall()

    if len(data) == 0:
        return False

    #0 - event
    #1 - setter upper
    #2 - attendee
    #3 - status
    #4 - member
    #5 - attendee (again)
    #6 - name
    #7 - year
    #8 - bio
    #9 - hometown
    #10 - gender
    #11 - interested in
    #12 - number
    #13 - robot
    #14 - dorm
    #15 - major

    #create user object

    other_attendee = data[0][5]

    year = ""
    bio = ""
    hometown = ""
    dorm = ""
    major = ""

    name = data[0][6]

    if data[0][7] is not None:
        year = 'Class of ' + str(data[0][7])

    if data[0][8] is not None:
        bio = data[0][8]

    if data[0][9] is not None:
        hometown = data[0][9]

    if data[0][14] is not None:
        dorm = data[0][14]

    if data[0][15] is not None:
        major = data[0][15]
    
    gender = data[0][10]
    interested_in = data[0][11]

    user = User(other_attendee, name, year, bio, hometown, gender, interested_in, dorm, major)

    member = "No"

    if data[0][4] == 1:
        member = "Yes"

    conn.commit()
    conn.close()

    return { 'user': user, 'setter_upper': data[0][1], 'member': member }

def get_interests(netid):
    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT interest_name from user_interest where user_netid='{}'".format(netid))

    data = cursor.fetchall()

    conn.commit()
    conn.close()
    
    interests = []
    for d in data:
        interests.append(d[0])

    return interests

def create_setup(setter_upper, attendee, event):
    #first need to find out if the attendee is a member of the dorm
    user = get_user_info(attendee)
    event_dorm = get_event_dorm(event)

    member = 0

    if user.dorm == event_dorm:
        member = 1

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.callproc('CreateSetup', (event, setter_upper, attendee, member))
    conn.commit()
    conn.close()

def setup_exists(setter_upper, attendee, event):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) from setup where setter_upper='{}' and attendee='{}' and event_name='{}'".format(setter_upper, attendee, event))

    data = cursor.fetchall()

    if data[0][0] == 0:
        return False
    else:
        return True

def get_event_dorm(event):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT org_name FROM event where name='{}'".format(event))

    data = cursor.fetchall()

    if len(data) is not 0:
        return data[0][0]
    else:
        return ""

def get_user_info(netid):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.callproc('GetUser', (netid,))
    data = cursor.fetchall()

    if len(data) == 0:
        return False

    user = data[0]
    name = ""
    year = ""
    
    if user[1]:
        name = user[1]

    year = user[2]
    bio = user[3]
    hometown = user[4]
    gender = user[5]
    interested_in = user[6]
    dorm = user[9]
    major = user[10]

    u = User(netid, name, year, bio, hometown, gender, interested_in, dorm, major)

    conn.commit()
    conn.close()
    return u

def get_event_info(event_name):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM event where name='{}'".format(event_name))
    data = cursor.fetchall()

    if len(data) == 0:
        return False

    event = data[0]

    date = event[1]
    time = event[2]
    location = event[3]
    org_name = event[4]

    e = Event(event_name, date, time, location, org_name)

    conn.commit()
    conn.close()
    return e
    
    
def get_my_matches(netid):

    conn = mysql.connect()
    cursor = conn.cursor()
    
    #member attendances
    cursor.execute("SELECT nonmem_attendee, event_name, mem_setter_upper from potential_matches where mem_attendee='{}' and member_status='Yes' and nonmember_status = 'Yes' order by event_name".format(netid))

    data = cursor.fetchall()

    matches = []

    for m in data:
        #get name and dorm of match
        cursor.execute("SELECT name, dorm from users where netid='{}'".format(m[0]))
        d2 = cursor.fetchall()

        #get name of setter_upper
        cursor.execute("SELECT name from users where netid='{}'".format(m[2]))
        d3 = cursor.fetchall()

        match_name = ""
        setter_upper = ""
        dorm = ""

        if len(d2) != 0:
            match_name = d2[0][0]
            dorm = d2[0][1]

        if len(d3) != 0:
            setter_upper = d3[0][0]

        match = Match(m[0], match_name, m[1], setter_upper, dorm)
        matches.append(match)
    
    #nonmember attendances
    cursor.execute("SELECT mem_attendee, event_name, nonmem_setter_upper from potential_matches where nonmem_attendee='{}' and member_status='Yes' and nonmember_status = 'Yes' order by event_name".format(netid))

    data = cursor.fetchall()
    
    for m in data:
        #get name and dorm of match
        cursor.execute("SELECT name, dorm from users where netid='{}'".format(m[0]))
        d2 = cursor.fetchall()

        #get name of setter_upper
        cursor.execute("SELECT name from users where netid='{}'".format(m[2]))
        d3 = cursor.fetchall()

        match_name = ""
        setter_upper = ""
        dorm = ""

        if len(d2) != 0:
            match_name = d2[0][0]
            dorm = d2[0][1]

        if len(d3) != 0:
            setter_upper = d3[0][0]

        match = Match(m[0], match_name, m[1], setter_upper, dorm)
        matches.append(match)

    conn.commit()
    conn.close()

    return matches

def get_events():

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT name from event;")

    data = cursor.fetchall()

    events = []
    for e in data:
        events.append(e[0])

    conn.commit()
    conn.close()

    return events

def get_friends_query(netid):
    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT friend FROM friends WHERE netid = '{}'".format(session['username']))

    data = cursor.fetchall()
    
    friends = []
    for f in data:
        cursor.execute("SELECT name FROM users WHERE netid = '{}'".format(f[0]))
        data = cursor.fetchall()
        if len(data) > 0:
            friends.append(Friend(f[0], data[0][0]))

    conn.commit()
    conn.close()

    return friends

#gets list of matches for netid
#member is a boolean value
def get_matches_query(attendee, setter_upper, event, member):
        conn = mysql.connect()
        cursor = conn.cursor()

        #get name of attendee
        cursor.execute("SELECT name FROM users WHERE netid='{}'".format(attendee))
        data = cursor.fetchall()

        if len(data) == 0:
            return []

        attendee_name = data[0][0]

        if (member == 1):
            sql_stmt = "SELECT nonmem_attendee FROM potential_matches WHERE mem_attendee='{}' and mem_setter_upper='{}' and event_name='{}' and member_status= 'Yes' and nonmember_status='Yes'".format(attendee, setter_upper, event)
        else:
            sql_stmt = "SELECT mem_attendee FROM potential_matches WHERE nonmem_attendee='{}' and nonmem_setter_upper='{}' and event_name='{}' and member_status= 'Yes' and nonmember_status='Yes'".format(attendee, setter_upper, event)

        cursor.execute(sql_stmt)

        data = cursor.fetchall()

        matches = []
        for m in data:
            name = ""
            dorm = ""

            cursor.execute("SELECT name, dorm FROM users WHERE netid='{}'".format(m[0]))
            d2 = cursor.fetchall()
            if len(d2) != 0:
                name = d2[0][0]
                dorm = d2[0][1]
            
            match = Match(m[0], name, event, attendee_name, dorm)
            matches.append(match)

        conn.commit()
        conn.close()
        return matches

def get_setups(netid, status):
    conn = mysql.connect()
    cursor = conn.cursor()
    sql_stmt = "SELECT event_name, attendee, member from setup where setup.setter_upper = '{}' and status= '{}'".format(netid, status)
    cursor.execute(sql_stmt)
    data = cursor.fetchall()

    setups = []
    for s in data:
        setup = Setup(s[0], session['username'], s[1], "", s[2])
        setups.append(setup)

    conn.commit()
    conn.close()
    return setups

class start_swiping(Resource):
    def get(self):
        if 'username' not in session:
            return redirect(url_for('login'))

        if 'attendee_netid' not in session or 'event' not in session:
            flash('Select a friend and an event!');
            return redirect(url_for('index'))

        attendee_netid = session['attendee_netid']
        event = session['event']
        attendee = get_user_info(attendee_netid)
        user = get_user_info(session['username'])

        e = get_event_info(event)

        #find out if this setup already exists
        #if it doesn't, need to create setup
        if not setup_exists(session['username'], attendee_netid, event):
            create_setup(session['username'], attendee_netid, event)

        match_info = get_match(session['username'], attendee_netid, event)

        headers = {'Content-Type': 'text/html'}

        if not match_info:
            return make_response(render_template('no_new_matches.html'))

        if os.path.isfile('./static/' + session['username']):
            pic = './static/' + session['username']
        else:
            pic = '/static/default-pro-pic.png'

        if os.path.isfile('./static/' + match_info['user'].netid):
            match_pic = './static/' + match_info['user'].netid
        else:
            match_pic = '/static/default-pro-pic.png'

        interests = get_interests(match_info['user'].netid)
        
        return make_response(render_template('madelyn/SYRinfo.html', interests=interests, pic=pic, match_pic = match_pic, match=match_info['user'], attendee=attendee, user=user, event=e, other_setter_upper = match_info['setter_upper'], member = match_info['member']), 200, headers)

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('attendee_netid')
        parser.add_argument('event')
        args = parser.parse_args()

        if args['attendee_netid'] is not None:
            session['attendee_netid'] = args['attendee_netid']

        if args['event'] is not None:
            session['event'] = args['event']

        headers = {'Content-Type': 'text/html'}
        return redirect(url_for("start_swiping"))

#class signup(Resource):
#    def post(self):
#        try:
#            parser = reqparse.RequestParser()
#            parser.add_argument('netid', type=str)
#            parser.add_argument('name', type=str)
#            parser.add_argument('year', type=int)
#            parser.add_argument('bio', type=str)
#            parser.add_argument('hometown', type=str)
#            parser.add_argument('gender', type=str)
#            parser.add_argument('interested_in', type=str)
#            parser.add_argument('dorm', type=str)
#            parser.add_argument('major', type=str)
#            parser.add_argument('interest')
#            args = parser.parse_args()
#
#            print args['interest']
#
#            n_netid = args['netid']
#            n_name = args['name']
#            n_year = args['year']
#            n_bio = args['bio']
#            n_hometown = args['hometown']
#            n_gender = args['gender']
#            n_interested_in = args['interested_in']
#            n_dorm = args['dorm']
#            n_major = args['major']
#
#            conn = mysql.connect()
#            cursor = conn.cursor()
#            sql_stmt = "INSERT INTO users (netid, name, year, bio, hometown, gender, interested_in, robot, dorm, major) VALUES (%(netid)s, %(name)s, %(year)s, %(bio)s, %(hometown)s, %(gender)s, %(interested_in)s, %(robot)s, %(dorm)s, %(major)s);"
#
#            cursor.execute(sql_stmt, {'netid': n_netid, 'name': n_name, 'year': n_year, 'bio': n_bio, 'hometown': n_hometown, 'gender': n_gender, 'interested_in': n_interested_in, 'robot': 0, 'dorm': n_dorm, 'major': n_major });
#            data = cursor.fetchall()
#
#            conn.commit()
#            conn.close()
#            session['username'] = n_netid
#            return redirect(url_for('index'))

#        except Exception as e:
#            traceback.print_exc()
#            return {'error' : str(e)}

class create_friend_profile(Resource):
    def post(self):
        if 'username' not in session:
            return redirect(url_for('login'))

        try:
            parser = reqparse.RequestParser()
            parser.add_argument('netid', type=str)
            parser.add_argument('name', type=str)
            parser.add_argument('year', type=int)
            parser.add_argument('bio', type=str)
            parser.add_argument('hometown', type=str)
            parser.add_argument('gender', type=str)
            parser.add_argument('interested_in', type=str)
            parser.add_argument('number', type=str)
            parser.add_argument('dorm', type=str)
            parser.add_argument('major', type=str)
            args = parser.parse_args()

            n_netid = args['netid']
            n_name = args['name']
            n_year = args['year']
            n_bio = args['bio']
            n_hometown = args['hometown']
            n_gender = args['gender']
            n_interested_in = args['interested_in']
            n_number = args['number']
            n_dorm = args['dorm']
            n_major = args['major']

            conn = mysql.connect()
            cursor = conn.cursor()
            sql_stmt = "INSERT INTO users (netid, name, year, bio, hometown, gender, interested_in, robot, dorm, major) VALUES (%(netid)s, %(name)s, %(year)s, %(bio)s, %(hometown)s, %(gender)s, %(interested_in)s, %(robot)s, %(dorm)s, %(major)s);"

            cursor.execute(sql_stmt, {'netid': n_netid, 'name': n_name, 'year': n_year, 'bio': n_bio, 'hometown': n_hometown, 'gender': n_gender, 'interested_in': n_interested_in, 'robot': 0, 'dorm': n_dorm, 'major': n_major });
            data = cursor.fetchall()
            
            insert_stmt = "INSERT INTO friends VALUES ( %(netid)s, %(friend)s);"
            cursor.execute(insert_stmt, { 'netid': session['username'], 'friend': n_netid})

            conn.commit()
            conn.close()

            return redirect(url_for('index'))

        except Exception as e:
            return {'error' : str(e)}

class get_matches(Resource):
    def post(self):
        if 'username' not in session:
            return redirect(url_for('login'))

        try:
            parser = reqparse.RequestParser()
            parser.add_argument('netid')
            parser.add_argument('member')
            parser.add_argument('event')
            args = parser.parse_args()

            friends = get_matches_query(args['netid'], session['username'], args['event'], args['member'])
            headers = {'Content-Type': 'text/html'}
            return make_response(render_template('get_matches.html', friends=friends), 200, headers)

        except Exception as e:
            return {'error': str(e) }

class add_friend(Resource):
    def post(self):
        if 'username' not in session:
            return redirect(url_for('login'))
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('friend', type=str)
            args = parser.parse_args()

            conn = mysql.connect()
            cursor = conn.cursor()

            #check that the user exists
            user = get_user_info(args['friend'])

            if user == False:
                flash('This user does not exist.')
                return redirect(url_for('index'))

            #check that the friendship does not already exit
            cursor.execute("SELECT count(*) FROM friends WHERE netid='{}' and friend='{}'".format(session['username'], args['friend']))
            data = cursor.fetchall()

            if (data[0][0] != 0):
                flash('You are already friends with this user!')
                return redirect(url_for('index'))

            insert_stmt = "INSERT INTO friends VALUES ( %(netid)s, %(friend)s);"
            cursor.execute(insert_stmt, { 'netid': session['username'], 'friend': args['friend'] })

            conn.commit()
            conn.close()
            return redirect(url_for('index'))

        except Exception as e:
            return {'error' : str(e)}

class edit_user(Resource):
    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('name', type=str)
            parser.add_argument('year', type=int)
            parser.add_argument('bio', type=str)
            parser.add_argument('hometown', type=str)
            parser.add_argument('gender', type=str)
            parser.add_argument('interested_in', type=str)
            parser.add_argument('major', type=str)
            parser.add_argument('dorm', type=str)
            args = parser.parse_args()

            n_netid = session['username']
            n_name = args['name']
            n_year = args['year']
            n_bio = args['bio']
            n_hometown = args['hometown']
            n_gender = args['gender']
            n_interested_in = args['interested_in']
            n_major = args['major']
            n_dorm = args['dorm']
            n_number = ""

            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('UpdateUser', (n_netid, n_name, n_year, n_bio, n_hometown, n_gender, n_interested_in, n_number, n_dorm, n_major,))
            data = cursor.fetchall()

            conn.commit()
            conn.close()
            return redirect(url_for('index'))

        except Exception as e:
            return {'error' : str(e)}

class index(Resource):
    def get(self):
        try:
            if 'username' not in session:
                return redirect(url_for('login'))
        
            session.pop('attendee_netid', None)
            session.pop('event', None)

            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT name from users where netid='{}';".format(session['username']))
            data = cursor.fetchall()
            conn.commit()
            conn.close()

            if (len(data) != 0):
                name = data[0][0]
            
                current_setups = get_setups(session['username'], "Searching")
                #past_setups = get_setups(session['username'], "Not Searching")
                friends = get_friends_query(session['username'])
                events = get_events()
                my_matches = get_my_matches(session['username'])
                user = get_user_info(session['username'])

                friend_matches = []

                #get matches for each setup
                for s in current_setups:
                    #get matches for this setup
                    matches = get_matches_query(s.attendee, s.setter_upper, s.event_name, s.member)
                    for m in matches:
                        friend_matches.append(m)

                friend_event_matches = {}
                for match in friend_matches:
                    if match.event not in friend_event_matches:
                        friend_event_matches[match.event] = []

                    friend_event_matches[match.event].append(match)

                my_event_matches = {}
                for match in my_matches:
                    if match.event not in my_event_matches:
                        my_event_matches[match.event] = []

                    my_event_matches[match.event].append(match)

                if os.path.isfile('./static/' + session['username']):
                    pic = './static/' + session['username']
                else:
                    pic = '/static/default-pro-pic.png'

                dorms = get_all_dorms()

                headers = {'Content-Type': 'text/html'}
                return make_response(render_template('madelyn/init.html', dorms=dorms,pic = pic, name=name, events=events, friends=friends, friend_event_matches = friend_event_matches, my_event_matches=my_event_matches, user=user),200,headers)
            else:
                return redirect(url_for('login'))
        
        except Exception as e:
            traceback.print_exc()
            return {'error': str(e) }

class login(Resource):
    def get(self):
        headers = {'Content-Type': 'text/html'}
        #return make_response(render_template('login.html'),200,headers)
        interests = get_all_interests()
        return make_response(render_template('madelyn/index.html', interests=interests), 200, headers)

    def post(self):
        try:
	    for key in request.form:
	        email = key
            email_list = email.split('@')

            netid = email_list[0]


            #parser = reqparse.RequestParser()
            #parser.add_argument('netid', type=str)
            #args = parser.parse_args()

            #netid = args['netid']

            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('GetUser', (netid,))
            data = cursor.fetchall()
            conn.commit()
            conn.close()

            if len(data) != 0:
                session['username'] = netid
                return 'yes'

            else:
                session['potential_username'] = netid
                return 'no'

        except Exception as e:
            return {'error': str(e)}

class delete_account(Resource):
    def post(self):
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('DeleteUser', (session['username'],))
        data = cursor.fetchall()
        conn.commit()
        conn.close()
        session.pop('username', None)
        return redirect(url_for('login'))


class logout(Resource):
    def post(self):
        if 'username' in session:
            session.pop('username', None)
        return redirect(url_for('login'))

class create_setup1(Resource):
    def get(self):
        if 'username' not in session:
            return redirect(url_for('login'))
        
        conn = mysql.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT friend FROM friends WHERE netid = '{}'".format(session['username']))

        data = cursor.fetchall()
        
        friends = []
        for f in data:
            cursor.execute("SELECT name FROM users WHERE netid = '{}'".format(f[0]))
            data = cursor.fetchall()
            if len(data) > 0:
                friends.append(Friend(f[0], data[0][0]))

        cursor.execute("SELECT name FROM event")
        data = cursor.fetchall()

        events = []
        for e in data:
            events.append(e[0])

        conn.commit()
        conn.close()


        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('create_setup.html', friends=friends, events=events),200,headers)

    def post(self):
        if 'username' not in session:
            return redirect(url_for('login'))

        parser = reqparse.RequestParser()
        parser.add_argument('attendee_netid', type=str)
        parser.add_argument('member', type=str)
        parser.add_argument('event', type=str)
        args = parser.parse_args()

        setter_upper_netid = session['username']
        attendee_netid = args['attendee_netid']
        event_name = args['event']
        if args['member'] == "yes":
            member = 1
        else:
            member = 0

        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('CreateSetup', (event_name, setter_upper_netid, attendee_netid, member))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))

class update_setup_status(Resource):
    def post(self):
        if 'username' not in session:
            return redirect(url_for('login'))

        try:
            parser = reqparse.RequestParser()
            parser.add_argument('attendee', type=str)
            parser.add_argument('event', type=str)
            parser.add_argument('status', type=str)

            args = parser.parse_args()

            conn = mysql.connect()
            cursor = conn.cursor()
            mysql_stmt = "UPDATE setup SET status = '{}' WHERE event_name = '{}' and setter_upper = '{}' and attendee = '{}'".format(args['status'], args['event'], session['username'], args['attendee'])
            cursor.execute(mysql_stmt)
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

        except Exception as e:
            return {'error' : str(e)}

class update_potential_match_status(Resource):
    def post(self):
        if 'username' not in session:
            return redirect(url_for('login'))

        parser = reqparse.RequestParser()
        parser.add_argument('status', type=str)
        parser.add_argument('other_setter_upper', type=str)
        parser.add_argument('other_attendee', type=str)
        parser.add_argument('attendee', type=str)
        parser.add_argument('event', type=str)
        parser.add_argument('member', type=str)
        args = parser.parse_args()

        attendee = args['attendee']
        member = args['member']
        event = args['event']
        status = args['status']

        if member == "No":
            member = 1
            nonmem_setter_upper = args['other_setter_upper']
            nonmem_attendee = args['other_attendee']
            mem_setter_upper = session['username']
            mem_attendee = args['attendee']
        else:
            member = 0
            mem_setter_upper = args['other_setter_upper']
            mem_attendee = args['other_attendee']
            nonmem_setter_upper = session['username']
            nonmem_attendee = args['attendee']

        conn = mysql.connect()
        cursor = conn.cursor()

        #need to check if match already exists; if not, create it
        cursor.callproc('GetPotentialMatch', (mem_setter_upper, nonmem_setter_upper, mem_attendee, nonmem_attendee, event,))
        
        data = cursor.fetchall()

        if len(data) == 0:
            cursor.callproc('CreatePotentialMatch', (mem_setter_upper, nonmem_setter_upper, mem_attendee, nonmem_attendee, event,))

        cursor.callproc('UpdatePotentialMatchStatus', (mem_setter_upper, nonmem_setter_upper, mem_attendee, nonmem_attendee, event, status, member,))

        conn.commit()
        conn.close()

        return redirect(url_for('start_swiping'), code=307)

class get_potential_match(Resource):
    def post(self):
        if 'username' not in session:
            return redirect(url_for('login'))

        parser = reqparse.RequestParser()
        parser.add_argument('attendee', type=str)
        parser.add_argument('event', type=str)
        args = parser.parse_args()

        event=args['event']
        attendee=args['attendee']

        conn = mysql.connect()
        cursor = conn.cursor()

        cursor.callproc('GetPotentialMatchList', (event, session['username'], attendee))

        data = cursor.fetchall()

        headers = {'Content-Type': 'text/html'}
        if len(data) == 0:
            return (render_template('no_new_matches.html'), 200, headers)

        #0 - event
        #1 - setter upper
        #2 - attendee
        #3 - status
        #4 - member
        #5 - attendee (again)
        #6 - name
        #7 - year
        #8 - bio
        #9 - hometown
        #10 - gender
        #11 - interested in
        #12 - number
        #13 - robot

        name = data[0][6]
        year = data[0][7]
        bio = data[0][8]
        hometown = data[0][9]

        event = data[0][0]
        other_setter_upper = data[0][1]
        other_attendee = data[0][2]
        if data[0][4] == True:
            member = "Yes"
        else:
            member = "No"

        conn.commit()
        conn.close()

        return make_response(render_template('get_potential_match.html', name=name, year=year, bio=bio, hometown=hometown, other_setter_upper=other_setter_upper,other_attendee=other_attendee, attendee=attendee, event=event, member=member),200,headers)

@app.route('/')
def goto_index():
    return redirect(url_for('index'))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload_picture', methods=['POST'])
def upload_picture():
    if 'file' in request.files:
        file = request.files['file']
        if file.filename != '':
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], session['username']))
    return redirect(url_for('index'))

@app.route('/signup_form', methods=['GET'])
def signup_form():
    if 'potential_username' not in session or 'username' in session:
        return redirect(url_for('index'))
    interests = get_all_interests()
    dorms = get_all_dorms()
    headers = {'Content-Type': 'text/html'}
    return make_response(render_template('madelyn/signup.html', interests=interests, dorms=dorms))

@app.route('/signup', methods=['POST'])
def signup():
    if request.method == 'POST':
        if 'potential_username' not in session:
            return redirect(url_for('login'))

        n_name = request.form.get('name')
        n_year = request.form.get('year')
        n_bio = request.form.get('bio')
        n_hometown = request.form.get('hometown')
        n_gender = request.form.get('gender')
        n_interested_in = request.form.get('interested_in')
        n_dorm = request.form.get('dorm')
        n_major = request.form.get('major')
        n_netid = session['potential_username']

        conn = mysql.connect()
        cursor = conn.cursor()
        sql_stmt = "INSERT INTO users (netid, name, year, bio, hometown, gender, interested_in, robot, dorm, major) VALUES (%(netid)s, %(name)s, %(year)s, %(bio)s, %(hometown)s, %(gender)s, %(interested_in)s, %(robot)s, %(dorm)s, %(major)s);"

        cursor.execute(sql_stmt, {'netid': session['potential_username'], 'name': n_name, 'year': n_year, 'bio': n_bio, 'hometown': n_hometown, 'gender': n_gender, 'interested_in': n_interested_in, 'robot': 0, 'dorm': n_dorm, 'major': n_major });
        data = cursor.fetchall()

        #add interests
        interests = request.form.getlist('interest')
        for i in interests:
            cursor.execute("INSERT INTO user_interest VALUES('{}', '{}')".format(n_netid, i))

        conn.commit()
        conn.close()
        session['username'] = n_netid
        session.pop('potential_username')

        return redirect(url_for('index'))

#api.add_resource(signup, '/signup')
api.add_resource(login, '/login')
api.add_resource(index, '/index')
api.add_resource(logout, '/logout')
api.add_resource(edit_user, '/edit_user')
api.add_resource(delete_account, '/delete_account')
api.add_resource(create_setup1, '/create_setup')
api.add_resource(get_potential_match, '/get_potential_match')
api.add_resource(update_potential_match_status, '/update_potential_match_status')
api.add_resource(add_friend, '/add_friend')
api.add_resource(get_matches, '/get_matches')
api.add_resource(update_setup_status, '/update_setup_status')
api.add_resource(create_friend_profile, '/create_friend_profile')
api.add_resource(start_swiping, '/start_swiping')

if __name__ == '__main__':
    app.run()
