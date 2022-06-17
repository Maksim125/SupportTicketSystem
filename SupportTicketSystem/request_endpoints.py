from flask import Blueprint, request, flash, jsonify
from flask_login import login_required
import json
from . import db
from datetime import datetime

from . import crud_operations

request_endpoints = Blueprint('request_endpoints', __name__)

@request_endpoints.route("/post-comment", methods = ["POST"])
@login_required
def post_comment():
    data = json.loads(request.data)
    user_id = data["userID"]
    ticket_id = data["ticketID"]
    new_comment = data["commentContent"]
    crud_operations.create_comment(db, content = new_comment, ticket_id = ticket_id, user_id = user_id)
    return jsonify({}) #Return empty

@request_endpoints.route("/delete-comment", methods = ["DELETE"])
@login_required
def delete_comment():
    data = json.loads(request.data)
    comment_id = data["commentID"]
    crud_operations.delete_comment(db, id = comment_id)
    return jsonify({}) #Return empty

@request_endpoints.route("/delete-ticket", methods = ["DELETE"])
@login_required
def delete_ticket():
    data = json.loads(request.data)
    ticket_id = data["ticketID"]
    # First delete all the comments belonging to the ticket
    for comment in crud_operations.read_comment(db, ticket_id = ticket_id):
        crud_operations.delete_comment(db, id = comment.id)
    crud_operations.delete_ticket(db, id = ticket_id)
    return jsonify({}) #Return empty

@request_endpoints.route("/resolve-ticket", methods = ["PATCH"])
@login_required
def resolve_ticket():
    data = json.loads(request.data)
    ticket_id = data["ticketID"]
    ticket = crud_operations.read_ticket(db, id = ticket_id)
    crud_operations.update_ticket(db, id = ticket_id, resolved = not ticket.resolved, time_resolved = datetime.utcnow())
    flash("Successfully resolved the ticket!", category="success")
    return jsonify({}) #Return empty

@request_endpoints.route("/leave-group", methods = ["DELETE"])
@login_required
def leave_group():
    data = json.loads(request.data)
    user_id = data["userID"]
    group_id = data["groupID"]
    user_groups = crud_operations.read_user_group(db, group_id = group_id)
    #If you're leaving the group, and only 1 person will be left, promote them
    if (len(user_groups) == 2):
        for user_group in user_groups:
            if user_group.user_id != user_id:
                crud_operations.update_user_group(db, user_id = user_group.user_id, group_id = group_id, rank_in_group = 2)
    crud_operations.delete_user_group(db, user_id = user_id, group_id= group_id)
    return jsonify({}) #Return empty

@request_endpoints.route("/join-group", methods = ["POST"])
@login_required
def join_group():
    data = json.loads(request.data)
    user_id = data["userID"]
    group_id = data["groupID"]
    user_groups = crud_operations.read_user_group(db, group_id=group_id)
    if not user_groups: #If you're joining an empty group, become its admin
        crud_operations.create_user_group(db, user_id = user_id, group_id = group_id, rank_in_group= 2)
    else: #If you're joining a non-empty group, you will be the default rank
        crud_operations.create_user_group(db, user_id = user_id, group_id = group_id)
    return jsonify({}) #Return empty

@request_endpoints.route("/rerank-user", methods = ["PATCH"])
@login_required
def rerank_user():
    data = json.loads(request.data)
    user_id = data["userID"]
    group_id = data["groupID"]
    new_rank = data["newRank"]
    #Only rerank if it's a request for a new rank
    if (new_rank != crud_operations.read_user_group(db, user_id, group_id).rank_in_group):
        crud_operations.update_user_group(db, user_id, group_id, rank_in_group = new_rank)
    return jsonify({}) #Return empty

@request_endpoints.route("/kick-user", methods = ["DELETE"])
@login_required
def kick_user():
    data = json.loads(request.data)
    user_id = data["userID"]
    group_id = data["groupID"]
    crud_operations.delete_user_group(db, user_id = user_id, group_id = group_id)
    return jsonify({}) #Return empty

