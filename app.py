import os
import sqlite3
from flask import Flask, g, render_template, session, redirect, url_for, request
from dotenv import load_dotenv
from werkzeug.security import check_password_hash

load_dotenv()

app = Flask(__name__)
DATABASE = 'SecureProgramming.db'
app.secret_key = os.environ.get("SECRET_KEY")
app.debug = True

@app.after_request
def add_no_cache(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext 
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def base():
    # Check if user is logged in
    if 'ID' in session:
        role = session.get('role')
        if role == 'guest':
            return redirect(url_for('guest'))
        elif role == 'employee':
            return redirect(url_for('employee'))
        elif role == 'admin':
            return redirect(url_for('admin'))
        else: 
            return "Role not recognized"

    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'GET':
        return render_template("login.html")

    username = request.form['email']
    password = request.form['password']

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """SELECT ID, username, password, name, role
           FROM user
           WHERE username=?""",
        (username,)
    )

    user = cursor.fetchone()
    cursor.close()

    if user and check_password_hash(user[2], password):

        session['ID'] = user[0]
        session['username'] = user[1]
        session['name'] = user[3]
        session['role'] = user[4]

        if user[4] == 'guest':
            return redirect(url_for('guest'))

        elif user[4] == 'employee':
            return redirect(url_for('employee'))

        elif user[4] == 'admin':
            return redirect(url_for('admin'))

        else:
            return "Role not recognized."

    else:
        return "Invalid credentials. Please try again."

@app.route('/admin')
def admin():
    if 'ID' not in session:
        return redirect(url_for('login'))

    db=get_db()
    cursor = db.cursor()
    cursor.execute("select sum(current_capacity) from rooms")
    total_capacity = cursor.fetchone()[0]
    
    
    if session.get('role') != 'admin':
        return "Access denied. You do not have permission to access this page."
    
    else:
        return render_template("admin/dashboard.html", name= 'Admin', gallery_capacity = total_capacity)

@app.route('/employee')
def employee():
    if 'ID' not in session:
        return redirect(url_for('login'))

    if session.get('role') != 'employee':
            return "Access denied. You do not have permission to access this page."

    user_id = session['ID']

    db=get_db()
    cursor = db.cursor()
    cursor.execute("select name from user where ID = ?", (user_id,))
    result = cursor.fetchone()

    cursor.execute("select sum(current_capacity) from rooms")
    total_capacity = cursor.fetchone()[0]

    
    cursor.close()

    name = result[0]
    return render_template("employee/dashboard.html", name = name, gallery_capacity = total_capacity)
  

@app.route('/guest')
def guest():
    if 'ID' not in session:
        return redirect(url_for('login'))

    if session.get('role') != 'guest':
        return "Access denied. You do not have permission to access this page."

    user_id = session['ID']

    db=get_db()
    cursor = db.cursor()
    cursor.execute("select name from user where ID = ?", (user_id,))
    result = cursor.fetchone()

    cursor.execute("select sum(current_capacity) from rooms")
    total_capacity = cursor.fetchone()[0]


    cursor.close()

    name = result[0]
    return render_template("guest/dashboard.html", name = name, gallery_capacity = total_capacity)

@app.route('/room1')
def room1():
    if 'ID' not in session:
        return redirect(url_for('login'))

    user_id = session['ID']
    room_id = 1

    db=get_db()
    cursor = db.cursor()

    cursor.execute("select name from user where ID = ?", (user_id,))
    Nameresult = cursor.fetchone()
    name = Nameresult[0]

    cursor.execute("select room_name, max_capacity, current_capacity, description from rooms where room_id = ?", (room_id,))
    room_result = cursor.fetchone()
    room_name = room_result[0]
    room_Maxcapacity = room_result[1]
    room_current_capacity = room_result[2]
    room_description = room_result[3]

    cursor.close()
    return render_template("room1.html", name = name, room_name = room_name, 
                           room_Maxcapacity = room_Maxcapacity, room_current_capacity = room_current_capacity, 
                            room_description = room_description, role = session['role'])


@app.route('/room2')
def room2():
    if 'ID' not in session:
        return redirect(url_for('login'))

    user_id = session['ID']
    room_id = 2

    db=get_db()
    cursor = db.cursor()

    cursor.execute("select name from user where ID = ?", (user_id,))
    Nameresult = cursor.fetchone()
    name = Nameresult[0]

    cursor.execute("select room_name, max_capacity, current_capacity, description from rooms where room_id = ?", (room_id,))
    room_result = cursor.fetchone()
    room_name = room_result[0]
    room_Maxcapacity = room_result[1]
    room_current_capacity = room_result[2]
    room_description = room_result[3]

    cursor.close()
    return render_template("room2.html", name = name, room_name = room_name, 
                           room_Maxcapacity = room_Maxcapacity, room_current_capacity = room_current_capacity, 
                            room_description = room_description, role = session['role'])

@app.route('/room3')
def room3():
    if 'ID' not in session:
        return redirect(url_for('login'))

    user_id = session['ID']
    room_id = 3

    db=get_db()
    cursor = db.cursor()

    cursor.execute("select name from user where ID = ?", (user_id,))
    Nameresult = cursor.fetchone()
    name = Nameresult[0]

    cursor.execute("select room_name, max_capacity, current_capacity, description from rooms where room_id = ?", (room_id,))
    room_result = cursor.fetchone()
    room_name = room_result[0]
    room_Maxcapacity = room_result[1]
    room_current_capacity = room_result[2]
    room_description = room_result[3]

    cursor.close()
    return render_template("room3.html", name = name, room_name = room_name, 
                           room_Maxcapacity = room_Maxcapacity, room_current_capacity = room_current_capacity, 
                            room_description = room_description, role = session['role'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
