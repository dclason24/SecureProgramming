import os
import sqlite3
import secrets
from flask import Flask, g, render_template, session, redirect, url_for, request, flash
from dotenv import load_dotenv
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()

app = Flask(__name__)
DATABASE = "SecureProgramming.db"
app.secret_key = os.environ.get("SECRET_KEY")
app.debug = True


@app.after_request
def add_no_cache(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def log_activity(action, outcome="success", person_id="None"):
    db = get_db()
    cursor = db.cursor()

    try:
        user_id = session.get("ID")

        cursor.execute(
            """
            INSERT INTO audit_logs
                (user_id, action,
                 outcome, ip_address, person_id)
            VALUES (?, ?, ?, ?, ?)
        """,
            (
                str(user_id) if user_id is not None else 0,
                action,
                outcome,
                request.remote_addr,
                person_id,
            ),
        )

        db.commit()

    except Exception as e:
        db.rollback()
        print("AUDIT LOG ERROR:", repr(e))
        raise

    finally:
        cursor.close()


@app.route("/logPageExit", methods=["POST"])
def logPageExit():
    log_activity("leaveRoom1")

    room_id = 1

    db = get_db()
    cursor = db.cursor()

    cursor.execute("select current_capacity FROM rooms where room_id = ?", (room_id,))
    room_result = cursor.fetchone()
    if room_result:
        room_current_capacity = room_result[0]

        if room_current_capacity > 0:
            room_current_capacity -= 1

            cursor.execute(
                "UPDATE rooms SET current_capacity = ? WHERE room_id = ?",
                (room_current_capacity, room_id),
            )
            log_activity("subtractingFromTotal1")
            db.commit()

    cursor.close()

    return "", 204


@app.route("/logPageExit2", methods=["POST"])
def logPageExit2():
    log_activity("leaveRoom2")

    room_id = 2

    db = get_db()
    cursor = db.cursor()

    cursor.execute("select current_capacity FROM rooms where room_id = ?", (room_id,))
    room_result = cursor.fetchone()
    if room_result:
        room_current_capacity = room_result[0]

    if room_current_capacity > 0:
        room_current_capacity -= 1

        cursor.execute(
            "UPDATE rooms SET current_capacity = ? WHERE room_id = ?",
            (room_current_capacity, room_id),
        )
        log_activity("subtractingFromTotal2")
        db.commit()

    cursor.close()

    return "", 204


@app.route("/logPageExit3", methods=["POST"])
def logPageExit3():
    log_activity("leaveRoom3")

    room_id = 3

    db = get_db()
    cursor = db.cursor()

    cursor.execute("select current_capacity FROM rooms where room_id = ?", (room_id,))
    room_result = cursor.fetchone()
    if room_result:
        room_current_capacity = room_result[0]

    if room_current_capacity > 0:
        room_current_capacity -= 1

        cursor.execute(
            "UPDATE rooms SET current_capacity = ? WHERE room_id = ?",
            (room_current_capacity, room_id),
        )
        log_activity("subtractingFromTotal3")
        db.commit()

    cursor.close()

    return "", 204


@app.route("/logPageExit4", methods=["POST"])
def logPageExit4():
    log_activity("leaveLogPage")

    return "", 204


@app.route("/")
def base():

    log_activity("webpageLoad", outcome="success")

    # Check if user is logged in
    if "ID" in session:
        role = session.get("role")
        if role == "guest":
            return redirect(url_for("guest"))
        elif role == "employee":
            return redirect(url_for("employee"))
        elif role == "admin":
            return redirect(url_for("admin"))
        else:
            return redirect(url_for("unsignedIn"))

    else:
        return redirect(url_for("unsignedIn"))


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        return render_template("login.html")

    username = request.form["email"]
    password = request.form["password"]

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """SELECT ID, username, password, name, role
           FROM user
           WHERE username=?""",
        (username,),
    )

    user = cursor.fetchone()
    cursor.close()

    if user and check_password_hash(user[2], password):

        session["ID"] = user[0]
        session["username"] = user[1]
        session["name"] = user[3]
        session["role"] = user[4]

        if user[4] == "guest":
            log_activity("login", outcome="success")
            return redirect(url_for("guest"))

        elif user[4] == "employee":
            log_activity("login", outcome="success")
            return redirect(url_for("employee"))

        elif user[4] == "admin":
            log_activity("login", outcome="success")
            return redirect(url_for("admin"))

        else:
            log_activity("unrecognizedRoleLogin", outcome="failed")
            return "Role not recognized."

    else:
        log_activity("loginFailed", outcome="failed")
        return "Invalid credentials. Please try again."


@app.route("/admin")
def admin():
    if "ID" not in session:
        log_activity("accessFailed", outcome="failed")
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        log_activity("accessFailed", outcome="failed")
        return "Access denied. You do not have permission to access this page."

    db = get_db()
    cursor = db.cursor()
    cursor.execute("select sum(current_capacity) from rooms")
    total_capacity = cursor.fetchone()[0]

    log_activity("loadAdminPage")

    return render_template("admin/dashboard.html", name="Admin", gallery_capacity=1)


@app.route("/employee")
def employee():
    if "ID" not in session:
        log_activity("accessFailed", outcome="failed")
        return redirect(url_for("login"))

    if session.get("role") != "employee":
        log_activity("accessFailed", outcome="failed")
        return "Access denied. You do not have permission to access this page."

    user_id = session["ID"]

    log_activity("loadEmployeePage")

    db = get_db()
    cursor = db.cursor()
    cursor.execute("select name from user where ID = ?", (user_id,))
    result = cursor.fetchone()

    cursor.execute("select sum(current_capacity) from rooms")
    total_capacity = cursor.fetchone()[0]

    cursor.close()

    name = result[0]
    return render_template("employee/dashboard.html", name=name, gallery_capacity=1)


@app.route("/guest")
def guest():
    if "ID" not in session:
        log_activity("accessFailed", outcome="failed")
        return redirect(url_for("login"))

    if session.get("role") != "guest":
        log_activity("accessFailed", outcome="failed")
        return "Access denied. You do not have permission to access this page."

    user_id = session["ID"]

    log_activity("loadGuestPage")

    db = get_db()
    cursor = db.cursor()
    cursor.execute("select name from user where ID = ?", (user_id,))
    result = cursor.fetchone()

    cursor.execute("select sum(current_capacity) from rooms")
    total_capacity = cursor.fetchone()[0]

    cursor.close()

    name = result[0]
    return render_template("guest/dashboard.html", name=name, gallery_capacity=1)


@app.route("/unsignedIn")
def unsignedIn():

    log_activity("WebpageAccessed-NotLoggedIn", outcome="success")

    db = get_db()
    cursor = db.cursor()
    cursor.execute("select sum(current_capacity) from rooms")
    total_capacity = cursor.fetchone()[0]
    cursor.close()

    return render_template("unsignedIn/dashboard.html", gallery_capacity=1)


@app.route("/createAccount", methods=["GET", "POST"])
def createAccount():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        name = request.form.get("name", "").strip()
        password = request.form.get("password", "")
        confirmPassword = request.form.get("confirmPassword", "")

        if not username or not name or not password:
            flash("Please fill in all fields.")
            return redirect(url_for("createAccount"))

        if password != confirmPassword:
            flash("Passwords do not match.")
            return redirect(url_for("createAccount"))

        if len(password) < 8:
            flash("Password must be at least 8 characters.")
            return redirect(url_for("createAccount"))

        db = get_db()
        cursor = db.cursor()

        try:
            cursor.execute("SELECT ID FROM user WHERE username = ?", (username,))

            if cursor.fetchone():
                flash("An account with this username already exists.")
                return redirect(url_for("createAccount"))

            hashed_password = generate_password_hash(password)

            cursor.execute(
                """
            INSERT INTO user (username, password, name, role)
            VALUES (?, ?, ?, ?)
            """,
                (username, hashed_password, name, "guest"),
            )

            db.commit()

            flash("Account created successfully! You can now sign in.")
            log_activity("loginCreated", outcome="success")
            return redirect(url_for("login"))

        finally:
            cursor.close()

    return render_template("createAccount.html")


@app.route("/room1")
def room1():
    if "ID" not in session:
        return redirect(url_for("login"))

    user_id = session["ID"]
    room_id = 1

    db = get_db()
    cursor = db.cursor()

    cursor.execute("select name from user where ID = ?", (user_id,))
    Nameresult = cursor.fetchone()
    name = Nameresult[0]

    cursor.execute(
        "select room_name, max_capacity, current_capacity, description from rooms where room_id = ?",
        (room_id,),
    )
    room_result = cursor.fetchone()
    room_name = room_result[0]
    room_Maxcapacity = room_result[1]
    room_current_capacity = room_result[2]
    room_description = room_result[3]

    log_activity("EnterRoom1", outcome="success")

    cursor.close()
    return render_template(
        "room1.html",
        name=name,
        room_name=room_name,
        room_Maxcapacity=room_Maxcapacity,
        room_current_capacity=room_current_capacity,
        room_description=room_description,
        role=session["role"],
    )


@app.route("/room2")
def room2():
    if "ID" not in session:
        return redirect(url_for("login"))

    user_id = session["ID"]
    room_id = 2

    db = get_db()
    cursor = db.cursor()

    cursor.execute("select name from user where ID = ?", (user_id,))
    Nameresult = cursor.fetchone()
    name = Nameresult[0]

    cursor.execute(
        "select room_name, max_capacity, current_capacity, description from rooms where room_id = ?",
        (room_id,),
    )
    room_result = cursor.fetchone()
    room_name = room_result[0]
    room_Maxcapacity = room_result[1]
    room_current_capacity = room_result[2]
    room_description = room_result[3]

    log_activity("EnterRoom2", outcome="success")

    cursor.close()
    return render_template(
        "room2.html",
        name=name,
        room_name=room_name,
        room_Maxcapacity=room_Maxcapacity,
        room_current_capacity=room_current_capacity,
        room_description=room_description,
        role=session["role"],
    )


@app.route("/room3")
def room3():
    if "ID" not in session:
        return redirect(url_for("login"))

    user_id = session["ID"]
    room_id = 3

    db = get_db()
    cursor = db.cursor()

    cursor.execute("select name from user where ID = ?", (user_id,))
    Nameresult = cursor.fetchone()
    name = Nameresult[0]

    cursor.execute(
        "select room_name, max_capacity, current_capacity, description from rooms where room_id = ?",
        (room_id,),
    )
    room_result = cursor.fetchone()
    room_name = room_result[0]
    room_Maxcapacity = room_result[1]
    room_current_capacity = room_result[2]
    room_description = room_result[3]

    log_activity("EnterRoom3", outcome="success")

    cursor.close()
    return render_template(
        "room3.html",
        name=name,
        room_name=room_name,
        room_Maxcapacity=room_Maxcapacity,
        room_current_capacity=room_current_capacity,
        room_description=room_description,
        role=session["role"],
    )


@app.route("/log")
def log():
    log_activity("EnterLog", outcome="success")

    user_id = session["ID"]

    db = get_db()
    cursor = db.cursor()

    cursor.execute("select name from user where ID = ?", (user_id,))
    Nameresult = cursor.fetchone()
    name = Nameresult[0]

    cursor.execute("""select * from audit_logs""")
    logs = cursor.fetchall()

    cursor.close()

    return render_template("log.html", logs=logs)


@app.route("/manageUsers", methods=["GET", "POST"])
def manage_users():
    if "ID" not in session:
        return redirect(url_for("login"))

    db = get_db()

    # Only current administrators can manage users
    admin = db.execute(
        "SELECT role FROM user WHERE ID = ?", (session["ID"],)
    ).fetchone()

    if not admin or admin[0] != "admin":
        return "Access denied", 403

    # Protect role changes from forged requests
    if "role_csrf_token" not in session:
        session["role_csrf_token"] = secrets.token_urlsafe(32)

    if request.method == "POST":
        token = request.form.get("csrf_token", "")

        if not secrets.compare_digest(token, session["role_csrf_token"]):
            return "Invalid request", 400

        user_id = request.form.get("user_id", type=int)
        new_role = request.form.get("role", "")

        if user_id is None or new_role not in ("guest", "employee", "admin"):
            flash("Invalid user or role.")
            return redirect(url_for("manage_users"))

        if user_id == int(session["ID"]):
            flash("You cannot change your own role.")
            return redirect(url_for("manage_users"))

        result = db.execute(
            "UPDATE user SET role = ? WHERE ID = ?", (new_role, user_id)
        )
        db.commit()

        if result.rowcount:
            log_activity(f"ChangedRoleOfUser{user_id}To{new_role}")
            flash("User role updated successfully!")
        else:
            flash("User not found.")

        return redirect(url_for("manage_users"))

    users = db.execute(
        "SELECT ID, username, name, role FROM user ORDER BY username"
    ).fetchall()

    return render_template(
        "admin/manage_users.html",
        users=users,
        csrf_token=session["role_csrf_token"],
        current_user_id=session["ID"],
    )


@app.route("/logout")
def logout():
    log_activity("logout", outcome="success")
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
