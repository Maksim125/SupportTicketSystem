from tabnanny import check
from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

@auth.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        #query db and look for this login information
        user = User.query.filter_by(email = email).first()
        if user:
            if check_password_hash(user.password, password):
                flash("Logged in successfully!", category = "success")
                login_user(user, remember = True)
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
    return redirect(url_for('views.index'))

@auth.route("/sign-up", methods = ["GET", "POST"])
def sign_up():
    if request.method == "POST":
        email = request.form.get("email")
        first_name = request.form.get("firstName")
        password = request.form.get("password1")
        password2 = request.form.get("password2")

        user = User.query.filter_by(email = email).first()
        if user:
            flash("User already exists with this email", category = "error")
        elif len(email) < 4:
            flash("Email must be greater than 3 characters!", category="error")
        elif len(first_name) < 2:
            flash("First name must be greater than 1 character!", category="error")
        elif len(password) < 7:
            flash("Password must be greater than 7 characters!", category="error")
        elif password != password2:
            flash("Passwords don't match", category="error")
        else:
            #Create new user
            new_user = User(email = email, first_name = first_name, password = generate_password_hash(password, method = 'sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash("Account created!", category="success")
            login_user(user, remember = True)
            #Redirect user to home page
            return redirect(url_for('views.index'))
        
    
    return render_template("sign_up.html", user = current_user)