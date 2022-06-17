import re
from flask import Blueprint, jsonify, redirect, render_template, request, flash, url_for
from flask_login import login_required, current_user
from . import db
from .common_queries import read_users_groups, read_all_users_in_group, \
    read_all_groups_not_userin, read_rank, all_unrestickets_for_user, all_tickets_by_user
from .crud_operations import *
import json

views = Blueprint('views', __name__)

@views.route("/", methods = ["GET"])
@login_required
def index():
    ticket_user_priority_group = all_unrestickets_for_user(current_user.id)
    return render_template("home.html", user = current_user, ticket_user_priority_group = ticket_user_priority_group)
    
@views.route("/mytickets", methods = ["GET"])
@login_required
def my_tickets():
    ticket_user_priority_group = all_tickets_by_user(current_user.id)
    return render_template("mytickets.html", user = current_user, ticket_user_priority_group = ticket_user_priority_group)

@views.route("/newticket", methods = ["POST", "GET"])
@login_required
def new_ticket():
    if request.method == "POST":
        ticket_title = request.form.get("ticket_title")
        ticket_content = request.form.get("ticket_content")
        ticket_priority = int(request.form.get("priority"))
        ticket_group = request.form.get("group")
        if len(ticket_title) < 1:
            flash("Ticket must include a title", category="error")
        elif len(ticket_content) < 1:
            flash("You need to describe your issue", category = "error")
        else:
            if (ticket_group) != "universal":
                group = read_group(db, group_name = ticket_group)[0]
                ticket = create_ticket(db,title = ticket_title, content = ticket_content, priority = ticket_priority, user_id = current_user.id, group_id=group.id)
            else:
                ticket = create_ticket(db,title = ticket_title, content = ticket_content, priority = ticket_priority, user_id = current_user.id, group_id= None)
            flash("Ticket successfully added!", category = "success")
            return redirect(url_for("views.view_ticket", id = ticket.id))
    u_groups = read_user_group(db, user_id = current_user.id)
    group_names = [read_group(db, id = group.group_id).group_name for group in u_groups]
    return render_template("newticket.html", user=current_user, group_names = group_names)

@views.route("/groups", methods = ["POST", "GET"])
@login_required
def groups():
    if request.method == "POST":
        new_group_name = request.form.get("new_group_name")
        new_group_name = re.sub(r'[^A-Za-z0-9 ]+', '', new_group_name) #Strip all non alpha numeric characters to prevent injection
        if len(new_group_name) > 50:
            flash("Group name too long", category = "error")
            return redirect(url_for("views.groups"))
        elif len(new_group_name) == 0:
            flash("You must enter a group name", category = "error")
            return redirect(url_for("views.groups"))
        elif read_group(db, group_name = new_group_name):
            flash("Group with that name already exists, pick a unique one", category = "error")
            return redirect(url_for("views.groups"))
        else:
            new_group = create_group(db, group_name = new_group_name)
            create_user_group(db, user_id = current_user.id, group_id=new_group.id, rank_in_group=2)
            return redirect(url_for("views.groups"))
    groups = read_users_groups(current_user.id)
    out_groups = read_all_groups_not_userin(current_user.id)
    return render_template("groups.html", user = current_user, groups = groups, \
        read_all_users_in_group = read_all_users_in_group, read_rank = read_rank, out_groups = out_groups)

@views.route("/view-ticket", methods = ["GET", "POST"])
@login_required
def view_ticket():
    ticket_id = request.args.get("id")
    print(ticket_id)
    ticket = read_ticket(db, id = ticket_id)
    if ticket_id:
        priority_map = {0:"Whenever", 1:"Nice to Have", 2: "Important", 3 : "CRITICAL"}
        username_func = lambda x : read_user(db, user_id = x).username
        if ticket.group_id:
            admin_perms = int(read_rank(user_id = current_user.id, group_id = ticket.group_id).rank_in_group) >= 2
        else:
            admin_perms = True #anyone can modify tickets in the no-group section
        return render_template("viewticket.html", user = current_user, ticket = ticket, priority_map = priority_map, username_func = username_func, admin_perms = admin_perms)
    else:
        return render_template("viewticket.html", user = current_user)