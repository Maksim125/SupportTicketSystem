from SupportTicketSystem.models import User
from werkzeug.security import check_password_hash
from SupportTicketSystem.models import User, Groups, User_Groups, Ticket, Comment

'''
Make sure models are being created as intended with the appropriate parameters assigned
'''
def test_new_user():
    new_user = User(email = "email@place.com", password = "password", username = "username")
    assert new_user.password != "password" #make sure the actual password is not stored
    assert check_password_hash(new_user.password, "password")
    assert new_user.email == "email@place.com" 
    assert new_user.username == "username"

def test_new_group():
    new_group = Groups(group_name = "new_group")
    assert new_group.group_name == "new_group"

def test_new_user_group():
    new_user_group = User_Groups(rank_in_group = 2)
    assert new_user_group.rank_in_group == 2

def test_new_ticket(time_posted, time_resolved):
    new_ticket = Ticket(title = "TicketTitle", content = "TicketContent", resolved = True, priority = 2, time_posted = time_posted, time_resolved = time_resolved)
    assert new_ticket.title == "TicketTitle"
    assert new_ticket.content == "TicketContent"
    assert new_ticket.resolved == True
    assert new_ticket.priority == 2
    assert new_ticket.time_posted == time_posted
    assert new_ticket.time_resolved == time_resolved

def test_new_comment(time_posted):
    new_comment = Comment(time_posted = time_posted, content = "commentContent")
    assert new_comment.time_posted == time_posted
    assert new_comment.content == "commentContent"

