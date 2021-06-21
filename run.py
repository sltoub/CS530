#Steven Toub
#CS530-900
#Semester Project

from flask import Flask, render_template, send_file, g, request, jsonify, session, redirect
import os
import json
import sqlite3
from passlib.hash import pbkdf2_sha256
import datetime

app = Flask(__name__, static_folder='public', static_url_path='')
app.secret_key = b'l,djk3435*HS-wjsdJDJSM\j\hf]]e'
DB_PATH = './engines.db'

#routing for logins
@app.route('/<name>')
def generic(name):
    if 'user' in session:
        return render_template('index.html')
    else:
        return redirect('/login')

#routing for validating user authentication on login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    
    message = None

    if request.method == 'POST':

        username = request.form['username']
        enteredPassword = request.form['password']

        if username and enteredPassword:
            user = get_database().get_user(username)
            if user:

                if pbkdf2_sha256.verify(enteredPassword, user['encrypted_password']):
                    session['user'] = user
                    return redirect('/index')
                else:
                    message = "Invalid password!"
            else:
                message = "Invalid username!"
        elif username and not enteredPassword:
            message = "No password entered..."
        elif not username and enteredPassword:
            message = "No username entered..."
    return render_template('login.html',  message=message)

#handles logouts
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')
    
# Handle the index (home) page
@app.route('/')
def initial():
   return render_template('login.html')

#home page routing
@app.route('/index')
def index():
    if 'user' in session:
        return render_template('index.html')
    else:
        return redirect('/login')

#route for accountability template
@app.route('/accountability')
def accountability():
    if 'user' in session:
        return render_template('accountability.html')
    else:
        return redirect('/login')

#routing for the engine listings
@app.route('/engines')
def engines():
    if 'user' in session:
        return render_template('engines.html')
    else:
        return redirect('/login')

#about page routing
@app.route('/about')
def about():
    return render_template('about.html')

#serves any files that begin with /exitLibs
@app.route('/extLibs/<path:path>')
def base_static(path):
    return send_file(os.path.join(app.root_path, 'extLibs', path))

#serves files from the public directory
@app.route('/public/<path:path>')
def img_static(path):
    return send_file(os.path.join(app.root_path, 'public', path))

#database routing
def get_database():
    db = getattr(g, '_database', None)
    if db is None:
        db = Database()
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

#returns json of engines table from database
@app.route('/api/engines')
def api_engines():
    if 'user' in session:
        n = request.args.get('n', default=99999)
        offset = request.args.get('offset', default=0)
        engines = get_database().get_engineData(n, offset)
        return jsonify(engines)
    else:
        return jsonify('Account not authenticated!')

#returns json of access data
@app.route('/api/access')
def api_access():
    if 'user' in session:
        n = request.args.get('n', default=99999)
        access = get_database().get_accessData()
        return jsonify(access)
    else:
        return jsonify('Account not authenticated!')

#adds a row to engines table in database
@app.route('/api/add')
def api_add():
    eid = request.args.get('eid', type=int)
    name = request.args.get('name')
    date = request.args.get('date')
    status = request.args.get('status')
    quantity = request.args.get('quantity', type=int)
    get_database().add_Item(eid,name,date,status,quantity)

    accessName = session['user']['name']
    accessDate = datetime.date.today()
    accessItem = str(eid) + '=' + name + '=' + date + '=' + status + '=' + str(quantity)

    #create access log
    if(status == '0'):
        get_database().add_Access_Log(accessName,accessDate,accessItem,'added engine')
    
    else:
        get_database().add_Access_Log(accessName,accessDate,accessItem,'added item')
    
    return api_engines()

#deletes an engine and all its items from engines table in database
@app.route('/api/deleteEngine')
def api_deleteEngine():
    eid = request.args.get('eid', type=int)
    get_database().delete_Engine(eid)

    accessName = session['user']['name']
    accessDate = datetime.date.today()
    accessItem = str(eid)

    #create access log
    get_database().add_Access_Log(accessName,accessDate,accessItem,'deleted engine')

    return api_engines()

#deletes a single item
@app.route('/api/deleteItem')
def api_deleteItem():
    eid = request.args.get('eid', type=int)
    name = request.args.get('name')
    date = request.args.get('date')
    status = request.args.get('status')
    quantity = request.args.get('quantity', type=int)
    get_database().delete_Item(eid,name,date,status,quantity)

    accessName = session['user']['name']
    accessDate = datetime.date.today()
    accessItem = str(eid) + '=' + name + '=' + date + '=' + status + '=' + str(quantity)

    #create access log
    get_database().add_Access_Log(accessName,accessDate,accessItem,'deleted item')

    return api_engines()
    

#modifies a single item
@app.route('/api/modifyItem')
def api_modifyItem():
    eid = request.args.get('eid', type=int)
    name = request.args.get('name')
    date = request.args.get('date')
    status = request.args.get('status')
    quantity = request.args.get('quantity', type=int)
    eidOld = request.args.get('eidOld', type=int)
    nameOld = request.args.get('nameOld')
    dateOld = request.args.get('dateOld')
    statusOld = request.args.get('statusOld')
    quantityOld = request.args.get('quantityOld', type=int)
    get_database().modify_Item(eid,name,date,status,quantity,eidOld,nameOld,dateOld,statusOld,quantityOld)

    accessName = session['user']['name']
    accessDate = datetime.date.today()
    accessItem = str(eid) + '=' + name + '=' + date + '=' + status + '=' + str(quantity) + '+' + str(eidOld) + '=' + nameOld + '=' + dateOld + '=' + statusOld + '=' + str(quantityOld)

    #create access log
    get_database().add_Access_Log(accessName,accessDate,accessItem,'modified item')
    
    return api_engines()

#--------------------DATABASE--------------------------------------------------------

class Database:

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)

    def execute(self, sql, parameters=[]):
        c = self.conn.cursor()
        c.execute(sql, parameters)
        return c.fetchall()
    
    def get_engineData(self, n, offset):
        data = self.execute(
            'SELECT * FROM engines ORDER BY eid ASC LIMIT ? OFFSET ?', [n, offset]
        )
        return [{
            'eid': d[0],
            'name': d[1],
            'date': d[2],
            'status': d[3],
            'quantity': d[4]
        } for d in data]
    
    def get_accessData(self):
        data = self.execute(
            'SELECT * FROM access'
        )
        return[{
            'name': d[0],
            'date': d[1],
            'item': d[2],
            'action': d[3]
        } for d in data]

    def add_Item(self, eid, name, date, status, quantity):
        self.execute('''INSERT INTO engines(eid,name,date,status,quantity) VALUES(?,?,?,?,?)''', [eid,name,date,status,quantity])
        self.conn.commit()

    def delete_Engine(self, eid):
        self.execute('''DELETE FROM engines WHERE eid=?''', [eid])
        self.conn.commit()

    def delete_Item(self, eid, name, date, status, quantity):
        self.execute('''DELETE FROM engines WHERE (eid=? AND name=? AND date=? AND status=? AND quantity=?)''', [eid,name,date,status,quantity])
        self.conn.commit()

    def modify_Item(self, eid, name, date, status, quantity, eidOld, nameOld, dateOld, statusOld, quantityOld):
        self.execute('''UPDATE engines SET eid=?, name=?, date=?, status=?, quantity=? WHERE eid=? AND name=? AND date=? AND status=? AND quantity=?;''', [eid,name,date,status,quantity,eidOld,nameOld,dateOld,statusOld,quantityOld])
        self.conn.commit()
    
    def add_Access_Log(self, name, date, item, action):
        self.execute('''INSERT INTO access(name,date,item,action) VALUES(?,?,?,?)''', [name,date,item,action])
        self.conn.commit()

    def get_user(self, username):
        data = self.execute('SELECT * FROM users WHERE username=?', [username])
        if data:
            d = data[0]
            return {
                'name': d[0],
                'username': d[1],
                'encrypted_password': d[2]
            }
        else:
            return None

    def close(self):
        self.conn.close()
#--------------------DATABASE--------------------------------------------------------

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080, debug=True)
