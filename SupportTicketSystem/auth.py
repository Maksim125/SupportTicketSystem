from flask import Blueprint, render_template, request, flash, redirect, url_for
from . import db
from werkzeug.security import check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from .crud_operations import *

auth = Blueprint('auth', __name__)

@auth.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        remember = True if request.form.get("checkbox") else False
        #query db and look for this login information
        user = read_user(db, email = email)
        if user:
            if check_password_hash(user.password, password):
                flash("Logged in successfully!", category = "success")
                login_user(user, remember = remember)
                return redirect(url_for("views.index"))
            else:
                flash("Password is incorrect", category = "error")
        else:
            flash("User does not exist", category = "error")
    return render_template("login.html", user = current_user)

@auth.route("/logout", methods = ["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect("/login")

@auth.route("/sign-up", methods = ["GET", "POST"])
def sign_up():
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password1")
        password2 = request.form.get("password2")
        remember = True if request.form.get("checkbox") else False

        user = read_user(db, email = email)
        if user:
            flash("User already exists with this email", category = "error")
        elif password != password2:
            flash("Passwords don't match!", category = "error")
        else:
            try:
                new_user = create_user(db, email = email, password = password, username = username)
                login_user(new_user, remember = remember)
                flash("Account created!", category="success")
                return redirect(url_for("views.index"))
            except ValueError as e:
                flash(str(e), category="error")
    return render_template("sign_up.html", user = current_user)