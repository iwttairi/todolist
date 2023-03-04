import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///final.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    tasks = db.execute("SELECT * FROM tasks WHERE user_id == ?", session["user_id"])
    count = db.execute("SELECT task FROM tasks WHERE user_id == ?", session["user_id"])
    done_num = db.execute("SELECT task FROM tasks WHERE user_id == ? and done == 1", session["user_id"])
    return render_template("todo.html", tasks = tasks, count = len(count), done_num = len(done_num))

@app.route('/add', methods=["POST"])
def add():
    db.execute("insert into tasks (user_id, task, done) values(?, ?, 0)", session["user_id"], request.form["task"])
    count = db.execute("select task from tasks where user_id == ?", session["user_id"])
    db.execute("update users set count = ? where id == ?", len(count), session["user_id"])
    return redirect("/")

@app.route('/completion/<int:id>')
def completion(id):
    db.execute("update tasks set done = ? where user_id == ? and task_id == ?", 1, session["user_id"], id)
    done_num = db.execute("select task from tasks where done == 1 and user_id == ?", session["user_id"])
    db.execute("update users set done_num = ? where id == ?", len(done_num), session["user_id"])
    return redirect("/")

@app.route('/undo/<int:id>')
def undo(id):
    db.execute("update tasks set done = ? where user_id == ? and task_id == ?", 0, session["user_id"], id)
    done_num = db.execute("select task from tasks where done == 1 and user_id == ?", session["user_id"])
    db.execute("update users set done_num = ? where id == ?", len(done_num), session["user_id"])
    return redirect("/")

@app.route('/delete/<int:id>')
def delete(id):
    db.execute("delete from tasks where task_id == ?", id)
    #count = db.execute("select task from tasks where and user_id == ?", session["user_id"])
    #done_num = db.execute("select task from tasks where done == 1 and user_id == ?", session["user_id"])
    #db.execute("update users set count = ?, done_num = ? where id == ?",len(count), len(done_num), session["user_id"])
    return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
        #if not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        elif not request.form.get("confirmation"):
            return apology("provide confirmation", 400)

        elif request.form.get("confirmation") != request.form.get("password"):
            return apology("must match password", 400)


        rows_num = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        if len(rows_num) != 0:
            return apology("invalid username and/or password", 400)

        user_id = db.execute("INSERT into users (username, hash) VALUES (?, ?)", request.form.get("username"), generate_password_hash(request.form.get("password")))
        session["user_id"] = user_id
        return redirect("/")

    else:
        return render_template("register.html")

