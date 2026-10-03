import os
import sqlite3
from flask import Flask, g, render_template, session, redirect, url_for, request
from dotenv import load_dotenv

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
    if 'user_id' in session:
        role = session.get('role')
        if role == 'guest':
            return redirect(url_for('guest'))
        elif role == 'employee':
            return redirect(url_for('associate'))
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

    if user and user[2] == password:

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
    
    if session.get('role') != 'admin':
        return "Access denied. You do not have permission to access this page."
    
    else:
        return render_template("admin/dashboard.html", name= 'Admin')

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
    cursor.close()

    name = result[0]
    return render_template("employee/dashboard.html", name = name)
  

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
    cursor.close()

    name = result[0]
    return render_template("guest/dashboard.html", name = name)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)