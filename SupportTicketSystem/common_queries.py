from .models import *
from . import db
from .crud_operations import *

def ordered_ticket_display(base_query):
    '''
    Given a base query of tickets,
    returns a zip object of tickets, usernames of creators, and priority level

    Ordered by: Highest priority and age of ticket. The oldest high priority ticket is displayed at the top.
    '''
    universal_tickets = base_query.order_by(Ticket.priority.desc(),Ticket.time_posted.asc()).all()
    user_names = [User.query.filter_by(id = ticket.user_id).first().username for ticket in universal_tickets]
    priorities = [ticket_priority_map[ticket.priority] for ticket in universal_tickets]
    group_names = [Groups.query.get(ticket.group_id).group_name if ticket.group_id is not None else "No Group" for ticket in universal_tickets]
    ticket_user_priority_group = zip(universal_tickets, user_names, priorities, group_names)
    return ticket_user_priority_group

def read_users_groups(user_id):
    '''
    Returns all the groups that the given user belongs to
    '''
    all_groups = Groups.query.join(User_Groups, Groups.id == User_Groups.group_id).filter(User_Groups.user_id == user_id).order_by(Groups.group_name.asc()).all()
    return all_groups

def read_all_users_in_group(group_id):
    '''
    Returns all users that belong to this group
    '''
    all_users = User.query.join(User_Groups, User_Groups.group_id == group_id).filter(User_Groups.user_id == User.id).all()
    return all_users

def read_all_groups_not_userin(user_id):
    '''
    Returns all the groups that the user is not currently in
    '''
    all_users_groups = read_users_groups(user_id)
    out_groups = Groups.query.filter(Groups.id.not_in([group.id for group in all_users_groups]))
    return out_groups

def read_all_tickets_in_group(group_id):
    '''
    Returns all tickets that belong to this group
    '''
    return read_ticket(db, group_id= group_id)

def read_rank(user_id, group_id):
    '''
    Returns the user_group for this pair
    '''
    return read_user_group(db, user_id, group_id)

def all_unrestickets_for_user(user_id):
    '''
    Returns all tickets from all the groups that the user is currently in that they need to resolve
    '''
    q = Ticket.query.join(User_Groups, (Ticket.group_id == User_Groups.group_id)).\
        filter(User_Groups.user_id == user_id, Ticket.user_id != user_id, Ticket.resolved == False)\
            .union(Ticket.query.filter(Ticket.group_id == None, Ticket.user_id != user_id, Ticket.resolved == False))
    return ordered_ticket_display(q)

def all_unrestickets_by_user(user_id):
    '''
    Displayable format of all unresolved tickets by a user
    '''
    q = Ticket.query.filter(Ticket.user_id == user_id, Ticket.resolved == False)
    return ordered_ticket_display(q)

def all_tickets_by_user(user_id):
    '''
    Displayable format of all tickets by a user
    '''
    tickets = Ticket.query.filter(Ticket.user_id == user_id).order_by(Ticket.resolved.asc(), Ticket.time_posted.desc())
    user_names = [User.query.filter_by(id = ticket.user_id).first().username for ticket in tickets]
    priorities = [ticket_priority_map[ticket.priority] for ticket in tickets]
    group_names = [Groups.query.get(ticket.group_id).group_name if ticket.group_id is not None else "No Group" for ticket in tickets]
    ticket_user_priority_group = zip(tickets, user_names, priorities, group_names)
    return ticket_user_priority_group

# def all_comments_for_ticket(ticket_id):
#     q = Comment.query.order_by(Comment.time_posted).filter(Comment.ticket_id == ticket_id).all()
#     return q

def read_username(user_id):
    return read_user(db, user_id = user_id).username

