from .models import *
import re
from werkzeug.security import generate_password_hash

'''
CREATE
'''
def create_user(db, email, password, username):
    '''
    Will create a user and commit them to the database. 
    Throws an ValueError if email, password, or username is invalid.

    Parameters
    ----------
    email : the user's email address. UNIQUE NOT NULL
    password : the user's password. NOT NULL
    username : the user's username. NOT NULL

    Returns
    -------
    User : The created user object
    '''
    if (email is None or password is None or username is None):
        raise ValueError("Email, password, and username must be provided to create a user")
    if not (re.fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email)):
        raise ValueError("Email must be of the format: address@host.ext")
    if len(password) < 7:
        raise ValueError("Password is too short")
    if len(username) < 1:
        raise ValueError("Username can not be an empty string")
    user = User(email = email, password = password, username = username)
    db.session.add(user)
    db.session.commit()
    return user

def create_comment(db, user_id, ticket_id, content, time_posted = None):
    '''
    Will create a comment and commit them to the database.
    Throws an argument error if any entry is None.
    
    Parameters
    ----------
    user_id : the id of the user the comment belongs to
    ticket_id : the id of the ticket the comment belongs to
    content : The comment's content
    time_posted : The timestamp for the comment, if not input, one will be generated for you

    Returns
    -------
    comment : the comment created
    '''
    if (user_id is None or ticket_id is None or content is None):
        raise ValueError("User id, ticket id, and content must be provided for the comment to be made")
    if time_posted is not None:
        comment = Comment(user_id = user_id, ticket_id = ticket_id, content = content, time_posted = time_posted)
    else:
        comment = Comment(user_id = user_id, ticket_id = ticket_id, content = content)
    db.session.add(comment)
    db.session.commit()
    return comment

def create_group(db, group_name):
    '''
    Will create a group and commit it to the database.
    Throws an argument error if the group name is None, or already exists.

    Parameters
    ----------
    group_name : the name of the group. UNIQUE NOT NULL

    Returns
    -------
    group : the group created
    '''
    if group_name is None:
        raise ValueError("Group name can not be None")
    if db.session.query(Groups).filter(Groups.group_name == group_name).count() > 0:
        raise ValueError("Group names must be unique!")
    group = Groups(group_name = group_name)
    db.session.add(group)
    db.session.commit()
    return group

def create_ticket(db, user_id, group_id, title, content, resolved = False, priority = 0, time_posted = None):
    '''
    Will create a ticket and commit it to the database.

    Parameters
    ----------
    title : the ticket's title. NOT NULL
    content : the ticket's content.
    priority : the tickets priority. 0, 1, 2
    user_id : the user the ticket belongs to. NOT NULL
    group_id : the group the ticket belongs to. NOT NULL

    Returns
    -------
    ticket : the created ticket

    '''
    if (user_id is None or title is None or content is None):
        raise ValueError("One or more necessary inputs is null")
    if not time_posted:
        ticket = Ticket(user_id = user_id, group_id = group_id, title = title, content = content, resolved = resolved)
    else:
        ticket = Ticket(user_id = user_id, group_id = group_id, title = title, content = content, resolved = resolved, time_posted = time_posted)
    db.session.add(ticket)
    db.session.commit()
    return ticket

def create_user_group(db, user_id, group_id, rank_in_group = 0):
    '''
    Creates an entry in the User Groups table.

    Parameters
    ----------
    user_id : the id of the user in this group
    group_id : the id of the group the user will be in
    rank_in_group : the user's rank in this group. Must be an element of {0,1,2}

    Returns
    -------
    user_groups : the created user group
    '''
    if rank_in_group not in [0,1,2]:
        raise ValueError("Rank must be an element of {0,1,2}, provided rank: {rank_in_group} is invalid.")
    if (user_id is None or group_id is None):
        raise ValueError("Both user id and group id must be provided")
    user_group = User_Groups(user_id = user_id, group_id = group_id, rank_in_group = rank_in_group)
    db.session.add(user_group)
    db.session.commit()
    return user_group

'''
READ
'''

def read_user(db, user_id = None, email = None, username = None):
    '''
    Will attempt to query users by the specified parameters.
    If no parameters are passed, it will return ALL users in the database.
    

    Parameters
    ----------
    id : the user's unique id in the database.
    email : the user's email address.
    username : the user's username.
    
    Returns
    -------
    User(s) : User(s) that match the specified parameters
    '''
    if (user_id is None and email is None and username is None):
        return db.session.query(User).all()
    query = db.session.query(User)
    if user_id is not None:
        query = query.filter(User.id == user_id)
    if email is not None:
        query = query.filter(User.email == email)
    if username is not None:
        query = query.filter(User.username == username)
    if query.all() and len(query.all()) == 1:
        return query.first()
    else:
        return query.all()

def read_comment(db, id = None, time_posted = None, content = None, ticket_id = None, user_id = None):
    '''
    Will attempt to query comments by the specified parameters.
    If no parameters are passed, it will return ALL comments in the database.

    Parameters
    ----------
    id : the comment's id in the database
    time_posted : Length 2 indexable. Will include all tickets posted in the time between entry 0 and 1 inclusive.
    content : String of ticket content, will find all comments that contain that string
    ticket_id : the id of the ticket in the database
    user_id : the id of the user in the database

    Returns
    -------
    comment(s) : all comment(s) that match the specified search criteria
    '''
    if (id is None and time_posted is None and content is None and ticket_id is None and user_id is None):
        return db.session.query(Comment).all()
    if id is not None:
        return db.session.query(Comment).get(id)
    query = db.session.query(Comment)
    if time_posted is not None:
        if len(time_posted) != 2:
            raise ValueError("Time posted must be given as an indexable data structure with 2 entries where the element at 0 is the minimum time, and the element at 1 is the maximum time")
        else:
            query = query.filter(Comment.time_posted >= time_posted[0]).filter(Comment.time_posted <= time_posted[1])
    if content is not None:
        query = query.filter(Comment.content.ilike(f"%{content}%"))
    if ticket_id is not None:
        query = query.filter(Comment.ticket_id == ticket_id)
    if user_id is not None:
        query = query.filter(Comment.user_id == user_id)
    return query.all()

def read_group(db, id = None, group_name = None, approximate_match = False):
    '''
    Will attempt to query groups by the specified parameters
    If no parameters are passed, it will return ALL groups in the database.

    Parameters
    ----------
    group_name : the name of the group
    approximate_search : whether to conduct an ILIKE query. By default looks for an exact match. 

    Returns
    -------
    group(s) : all groups that match the search parameters
    '''
    if id is None and group_name is None:
        return db.session.query(Groups).all()
    elif id is not None:
        return db.session.query(Groups).get(id)
    elif not approximate_match:
        return db.session.query(Groups).filter(Groups.group_name == group_name).all()
    else:
        return db.session.query(Groups).filter(Groups.group_name.ilike(f"%{group_name}%")).all()

def read_ticket(db, id = None, time_posted = None, time_resolved = None, title = None, content = None, resolved = None, priority = None, user_id = None, group_id = None):
    '''
    Will attempt to find all tickets matching the input criteria

    Parameters
    ----------
    id : ticket id
    time_posted : indexable length-2 structure that specifies a time range of when tickets were posted. (inclusive)
    time_resolved : indexable length-2 structure that specifies a time range of when tickets were resolved. (inclusive)
    title : string to search for in the titles, does an approximate match. (not case sensitive)
    content : string to search for in the contnet, does an approximate match. (not case sensitive)
    resolved : filter by whether tickets were resolved or not
    priority : filter by the priority rank of the tickets. DOES NOT check for valid priority range, if invalid the results will simply be empty.
    user_id : filter tickets by the id of the user who made them
    group_id : filter tickets by the id of the group they belong to
    
    Returns
    -------
    ticket(s) : all ticket(s) matching search criteria
    '''
    if id is None and time_posted is None and time_resolved is None and title is None and content is None and resolved is None and priority is None\
        and user_id is None and group_id is None:
        return db.session.query(Ticket).all()
    if id is not None:
        return db.session.query(Ticket).get(id)
    query = db.session.query(Ticket)
    if time_posted is not None:
        if len(time_posted) != 2:
            raise ValueError("time posted must be a valid time range, or contain 2 entries of the same time")
        else:
            query = query.filter(Ticket.time_posted >= time_posted[0]).filter(Ticket.time_posted <= time_posted[1])
    if time_resolved is not None:
        if len(time_resolved) != 2:
            raise ValueError("Time resolved must be a valid 2 entry time range, or contain 2 entries of the same time")
        else:
            query = query.filter(Ticket.time_resolved >= time_resolved[0]).filter(Ticket.time_resolved <= time_resolved[1])
    if title is not None:
        query = query.filter(Ticket.title.ilike(f"%{title}%"))
    if content is not None:
        query = query.filter(Ticket.content.ilike(f"%{content}%"))
    if resolved is not None:
        query = query.filter(Ticket.resolved == resolved)
    if priority is not None:
        query = query.filter(Ticket.priority == priority)
    if user_id is not None:
        query = query.filter(Ticket.user_id == user_id)
    if group_id is not None:
        query = query.filter(Ticket.group_id == group_id)
    return query.all()

def read_user_group(db, user_id = None, group_id = None, rank_in_group = None):
    '''
    Will attempt to search for all user groups matching the specified critera.

    Parameters
    ----------
    user_id : the user id for this assignment
    group_id : the group id for this assignment
    rank_in_group : the rank of the user in this group
    '''
    if user_id is None and group_id is None and rank_in_group is None:
        return db.session.query(User_Groups).all()
    if user_id is not None and group_id is not None:
        return db.session.query(User_Groups).get((user_id, group_id)) #the 2 ids are the primary keys
    query = db.session.query(User_Groups)
    if user_id is not None:
        query = query.filter(User_Groups.user_id == user_id)
    if group_id is not None:
        query = query.filter(User_Groups.group_id == group_id)
    if rank_in_group is not None:
        query = query.filter(User_Groups.rank_in_group == rank_in_group)
    return query.all()

'''
UPDATE 
Must specify id of the exact entry you are updating, no wide-sweeping updates are allowed.
'''

def update_user(db, id, email = None, password = None, username = None):
    '''
    Will update a user's attributes at a specified ID.

    Parameters
    ----------
    id : the unique id of the user that will be updated.
    email : what the user's email should now be.
    password : what the user's password should now be.
    username : what the user's username should now be.

    Returns
    -------
    User : the updated user
    '''
    user = db.session.query(User).get(id)
    if user is None:
        raise ValueError("ID did not uniquely identify a user in the database")
    if email is None and password is None and username is None:
        return user
    if email is not None:
        if not (re.fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email)):
            raise ValueError("Updated email is not valid")
        else:
            user.email = email
    if password is not None:
        if len(password) < 7:
            raise ValueError("New password is too short")
        else:
            user.password = generate_password_hash(password)
    if username is not None:
        if len(username) < 1:
            raise ValueError("Username must contain at least 1 character")
        else:
            user.username = username
    db.session.commit()
    return user
    

def update_comment(db, id, time_posted = None, content = None, ticket_id = None, user_id = None):
    '''
    Will update the specific comment's attributes

    Parameters
    ----------
    id : the id of the comment
    time_posted : datetime of when the comment was made
    content : the body of the comment
    ticket_id : the ticket this comment belongs to
    user_id : the user who made this commment

    Returns
    -------
    comment : the updated comment

    '''
    if id is None:
        raise ValueError("ID of the comment must be provided")
    comment = read_comment(db, id = id)
    if comment is None:
        raise ValueError("ID does not belong to a commment in the database")
    if time_posted is None and content is None and ticket_id is None and user_id is None:
        return comment
    if time_posted is not None:
        comment.time_posted = time_posted
    if content is not None:
        comment.content = content
    if ticket_id is not None:
        comment.ticket_id = ticket_id
    if user_id is not None:
        comment.user_id = user_id
    db.session.commit()
    return comment

def update_group(db, id, group_name = None):
    '''
    Will update the group's data in the database

    Parameters
    ----------
    id : the group's id
    group_name : the group's name

    Returns
    -------
    group : the updated group
    '''
    group = read_group(db, id = id)
    if group is None:
        raise ValueError("The ID entered does not correspond to a group in the database")
    if group_name is None:
        return group
    else:
        group.group_name = group_name
    db.session.commit()
    return group

def update_ticket(db, id, time_posted = None, time_resolved = None, title = None, content = None,\
     resolved = None, priority = None, user_id = None, group_id = None, nullgroup = False):
    '''
    Will update the ticket's entries to the given inputs

    Parameters
    ----------
    id : the id of the ticket to update
    time_posted : the datetime of when the ticket was posted
    time_resolved : the datetime of when the ticket was resolved
    title : the title of the ticket
    content : the body of the ticket
    resolved : whether the ticket was resolved or not
    priority : The priority level of the ticket [0,1,2,3]
    user_id : The creator of the ticket
    group_id : The group that this ticket belongs to. (NULLABLE)
    nullgroup : Whether to move this ticket to the null group.

    Returns
    -------
    ticket : the updated ticket
    '''
    ticket = read_ticket(db, id = id)
    if ticket is None:
        raise ValueError("ID provided does not correspond to a ticket in the database")
    if time_posted is not None:
        ticket.time_posted = time_posted
    if time_resolved is not None:
        ticket.time_resolved = time_resolved
    if title is not None:
        ticket.title = title
    if content is not None:
        ticket.content = content
    if resolved is not None:
        ticket.resolved = resolved
    if priority is not None:
        if priority in [0,1,2,3]:
            ticket.priority = priority
        else:
            raise ValueError("Priority must be 0,1,2 or 3. Entered value: {priority} is invalid")
    if user_id is not None:
        ticket.user_id = user_id
    if group_id is not None:
        ticket.group_id = group_id
    if nullgroup:
        ticket.group_id = None
    db.session.commit()
    return ticket
    

def update_user_group(db, user_id, group_id, rank_in_group = None):
    '''
    Will update the given user-group. The user's and group's ids are both primary keys for this table, so both
    are required to uniquely identify the specific usergroup. These ids are not supposed to change, so to move a user to
    a different group or vice versa, you must delete or create rows instead.

    Parameters
    ----------
    user_id : the user's id
    group_id : the group's id
    rank_in_group : this user's rank in this group

    Returns
    -------
    user_group : updated user group
    '''
    user_group = db.session.query(User_Groups).get((user_id, group_id))
    if user_group is None:
        raise ValueError(f"User group with user_id: {user_id} and group_id: {group_id} was not found in the database")
    if rank_in_group is not None:
        if rank_in_group not in [0,1,2]:
            raise ValueError("Attempting to rerank user to an invalid rating")
        else:
            user_group.rank_in_group = rank_in_group
    db.session.commit()
    return user_group

'''
DELETE
Must specify the id of the exact item you are deleting. No wide-sweeping deletions of data allowed.
'''

def delete_user(db, id):
    '''
    Will delete a user given the user's id in the database

    Parameters
    ----------
    id : the id of the user

    Returns
    -------
    None : user deleted, null value output
    '''
    if id is not None:
        db.session.query(User).filter(User.id == id).delete()
        db.session.commit()
        return None
    else:
        raise ValueError("ID is not defined")

def delete_comment(db, id):
    '''
    Will delete a comment with the given id

    Parameters
    ----------
    id : the comment's id - if provided, it will ONLY delete this comment

    Returns
    -------
    None : comment deleted
    '''
    if id is not None:
        db.session.query(Comment).filter(Comment.id == id).delete()
        db.session.commit()
        return None
    else:
        raise ValueError("ID is not defined")

def delete_group(db, id):
    '''
    Will delete group with the given id

    Parameters
    ----------
    id : the id of the group

    Returns
    -------
    None : group has been deleted
    '''
    if id is not None:
        db.session.query(Groups).filter(Groups.id == id).delete()
        db.session.commit()
        return None
    else:
        raise ValueError("ID is not defined")

def delete_ticket(db, id):
    '''
    Will delete ticket with the given id

    Parameters
    ----------
    id : the id of the ticket

    Returns
    -------
    None : ticket has been deleted
    '''
    if id is not None:
        db.session.query(Ticket).filter(Ticket.id == id).delete()
        db.session.commit()
        return None
    else:
        raise ValueError("ID is not defined")

def delete_user_group(db, user_id, group_id):
    '''
    Will delete user_group with the given id

    Parameters
    ----------
    user_id : the id of the user for the group
    group_id : the id of the group the user is in

    Returns
    -------
    None : user_group has been deleted
    '''
    if id is not None:
        db.session.query(User_Groups).filter(User_Groups.user_id == user_id).filter(User_Groups.group_id == group_id).delete()
        db.session.commit()
        return None
    else:
        raise ValueError("ID is not defined")