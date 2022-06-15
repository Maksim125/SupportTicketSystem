from enum import unique
from sqlalchemy import ForeignKey
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime


class User(db.Model, UserMixin):
    '''
    User schema
    '''
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(150), unique = True, nullable = False)
    password = db.Column(db.String(100), unique = True, nullable = False)
    username = db.Column(db.String(50))

    tickets = db.relationship("Ticket", backref = "author", lazy = True) #tickets made by the user
    comments = db.relationship("Comment", backref = "author") #comments made by the user


class Ticket(db.Model):
    '''
    Ticket Schema
    '''
    id = db.Column(db.Integer, primary_key = True)

    time_posted = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    time_resolved = db.Column(db.DateTime, nullable = True) #Null if not yet resolved

    title = db.Column(db.String(120), nullable = False)
    content = db.Column(db.Text, nullable = False)

    resolved = db.Column(db.Boolean, nullable = False, default = False)
    priority = db.Column(db.Integer, nullable = False, default = 0) #Default low priority

    comments = db.relationship("Comment", backref = "ticket", lazy = True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable = False) #id of author
    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"), nullable = True) #group the ticket belongs to


class Comment(db.Model):
    '''
    Comment schema
    '''
    id = db.Column(db.Integer, primary_key = True)
    time_posted = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    content = db.Column(db.Text, nullable = False)
    ticket_id = db.Column(db.Integer, db.ForeignKey("ticket.id"), nullable = False) #id of ticket the comment is for
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable = False) #id of the user who made the comment


class Groups(db.Model):
    '''
    Groups schema
    '''
    id = db.Column(db.Integer, primary_key = True)
    group_name = db.Column(db.String(100), unique = True)


class User_Groups(db.Model):
    '''
    User groups schema
    '''
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key = True)
    group_id = db.Column(db.String(50), db.ForeignKey("user.id"), primary_key = True)
    rank_in_group = db.Column(db.Integer, nullable = False, default = 0)