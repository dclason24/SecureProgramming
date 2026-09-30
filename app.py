import sqlite3
from flask import Flask, g, render_template

app = Flask(__name__)
DATABASE = 'SecureProgramming.db'
app.debug = True

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
def show_users():
    db = get_db()
    cursor = db.cursor()
    
    # 1. Fetching multiple rows
    cursor.execute("SELECT * FROM test")
    users = cursor.fetchall()
    return render_template('index.html', users=users)

if __name__ == '__main__':
    app.run(debug=True)