from flask import Flask, request, render_template, make_response, redirect, url_for, session
from flask_restful import Resource, Api, reqparse
from flask.ext.mysql import MySQL

class Setup:

    def __init__(self, event_name, setter_upper, attendee, status, member):
        self.event_name = event_name
        self.setter_upper = setter_upper
        self.attendee = attendee
        self.status = status
        self.member = member

mysql = MySQL()
app = Flask(__name__)
api = Api(app)

app.config['MYSQL_DATABASE_USER'] = 'mconnol6'
app.config['MYSQL_DATABASE_PASSWORD'] = 'grouppw'
app.config['MYSQL_DATABASE_DB'] = 'mconnol6'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_PORT'] = 3306
app.config['SECRET_KEY'] = 'this should be changed'

mysql.init_app(app)

class signup(Resource):
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('signup.html'),200,headers)

    def post(self):
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
            args = parser.parse_args()

            n_netid = args['netid']
            n_name = args['name']
            n_year = args['year']
            n_bio = args['bio']
            n_hometown = args['hometown']
            n_gender = args['gender']
            n_interested_in = args['interested_in']
            n_number = args['number']

            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('AddUser', (n_netid, n_name, n_year, n_bio, n_hometown, n_gender, n_interested_in, n_number, 0))
            data = cursor.fetchall()

            conn.commit()
            return redirect(url_for('index'))

        except Exception as e:
            return {'error' : str(e)}

class edit_user(Resource):
    def get(self):
        if 'username' not in session:
            return redirect(url_for('login'))
        try:
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('GetUser', (session['username'],))
            data = cursor.fetchall()

            user = data[0]
            
            name = user[1]
            year = user[2]
            bio = user[3]
            hometown = user[4]
            gender = user[5]
            interested_in = user[6]
            number = user[7]

            conn.commit()
            
            headers = {'Content-Type': 'text/html'}
            return make_response(render_template('edit_user.html', netid=session['username'], name=name, year=year, bio=bio, hometown=hometown, gender=gender, interested_in=interested_in, number=number),200,headers)

        except Exception as e:
            return {'error' : str(e)}

    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('name', type=str)
            parser.add_argument('year', type=int)
            parser.add_argument('bio', type=str)
            parser.add_argument('hometown', type=str)
            parser.add_argument('gender', type=str)
            parser.add_argument('interested_in', type=str)
            parser.add_argument('number', type=str)
            args = parser.parse_args()

            n_netid = session['username']
            n_name = args['name']
            n_year = args['year']
            n_bio = args['bio']
            n_hometown = args['hometown']
            n_gender = args['gender']
            n_interested_in = args['interested_in']
            n_number = args['number']

            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('UpdateUser', (n_netid, n_name, n_year, n_bio, n_hometown, n_gender, n_interested_in, n_number,))
            data = cursor.fetchall()

            conn.commit()
            return redirect(url_for('index'))

        except Exception as e:
            return {'error' : str(e)}

class index(Resource):
    def get(self):
        if 'username' not in session:
            return redirect(url_for('login'))

        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('GetSetups', (session['username'],))
        data = cursor.fetchall()

        setups = []
        for s in data:
            setup = Setup(s[0], session['username'], s[1], "", s[2])
            setups.append(setup)

        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('index.html', name=session['username'], setups=setups),200,headers)

class login(Resource):
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('login.html'),200,headers)

    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('netid', type=str)
            args = parser.parse_args()

            netid = args['netid']

            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('GetUser', (netid,))
            data = cursor.fetchall()
            conn.commit()

            if len(data) != 0:
                session['username'] = netid
                return redirect(url_for('index'))

            else:
                headers = {'Content-Type': 'text/html'}
                return redirect(url_for('login'))

        except Exception as e:
            return {'error': str(e)}

class delete_account(Resource):
    def post(self):
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('DeleteUser', (session['username'],))
        data = cursor.fetchall()
        conn.commit()
        session.pop('username', None)
        return redirect(url_for('login'))


class logout(Resource):
    def post(self):
        if 'username' in session:
            session.pop('username', None)
        return redirect(url_for('login'))

class create_setup(Resource):
    def get(self):
        if 'username' not in session:
            return redirect(url_for('login'))

        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('create_setup.html'),200,headers)

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

        return redirect(url_for('index'))

class get_potential_matches(Resource):
    def get(self):
        if 'username' not in session:
            return redirect(url_for('login'))

        attendee = request.args.get('attendee')
        event = request.args.get('event')

@app.route('/')
def goto_index():
    return redirect(url_for('index'))

api.add_resource(signup, '/signup')
api.add_resource(login, '/login')
api.add_resource(index, '/index')
api.add_resource(logout, '/logout')
api.add_resource(edit_user, '/edit_user')
api.add_resource(delete_account, '/delete_account')
api.add_resource(create_setup, '/create_setup')
api.add_resource(get_potential_matches, '/get_potential_matches')

if __name__ == '__main__':
    app.run()
