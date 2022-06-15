from datetime import date
from multiprocessing.sharedctypes import Value
from sqlalchemy import null
from werkzeug.security import check_password_hash
from conftest import db
from SupportTicketSystem.crud_operations import *
from SupportTicketSystem.models import *
import pytest


'''
The fixtures create a clean database in memory for every test method call. It contains no entries except for 1 authenticated test user. (see ../conftest.py for details)

Tests more or less follow the following pattern:
    1. Valid input --> query database to assert that you get the expected results
        a. Valid input where you go one by one with each optionally specified parameter
        b. Valid input without specifying optional parameters
        c. Valid input with all optional parameters
    2. Invalid input --> make sure the expected errors occur
'''

'''CREATE'''
def test_create_user(client, init_database):
    with client as test_client:
        user = create_user(db, email = "new_user@old.com", password =  "new_password", username = "nameOfUser")
        assert db.session.query(User).get(user.id) #User is created
        assert db.session.query(User).get(user.id).email == "new_user@old.com"
        assert db.session.query(User).get(user.id).username == "nameOfUser"

def test_create_comment(client, init_database, time_posted):
    with client as test_client:
        comment = create_comment(db, user_id = 1, ticket_id = 1, content = "comment content",
        time_posted = time_posted)
        assert db.session.query(Comment).get(comment.id)
        assert db.session.query(Comment).get(comment.id).content == "comment content"
        assert db.session.query(Comment).get(comment.id).user_id == 1
        assert db.session.query(Comment).get(comment.id).ticket_id == 1
        assert db.session.query(Comment).get(comment.id).time_posted == time_posted
        with pytest.raises(ValueError):
            create_comment(db, None, None, None)

def test_create_group(client, init_database):
    with client as test_client:
        group = create_group(db, "my new group")
        assert db.session.query(Groups).get(group.id)
        assert db.session.query(Groups).get(group.id).group_name == "my new group"
        group2 = create_group(db, "my other group")
        assert db.session.query(Groups).get(group2.id)
        assert db.session.query(Groups).get(group2.id).group_name == "my other group"
        with pytest.raises(ValueError):
            create_group(db, "my new group")
        with pytest.raises(ValueError):
            create_group(db, None)

def test_create_ticket(client, init_database, time_posted):
    with client as test_client:
        ticket = create_ticket(db, user_id = 1, group_id = 2, \
            title = "my ticket title", content = "my ticket content")
        assert db.session.query(Ticket).get(ticket.id)
        assert db.session.query(Ticket).get(ticket.id).user_id == 1
        assert db.session.query(Ticket).get(ticket.id).group_id == 2
        assert db.session.query(Ticket).get(ticket.id).title == "my ticket title"
        assert db.session.query(Ticket).get(ticket.id).content == "my ticket content"
        assert db.session.query(Ticket).get(ticket.id).resolved == False
        assert db.session.query(Ticket).get(ticket.id).priority == 0
        ticket2 = create_ticket(db, user_id = 1, group_id = 2, \
            title = "my ticket title", content = "my ticket content", time_posted = time_posted)
        assert db.session.query(Ticket).get(ticket2.id).time_posted == time_posted
        with pytest.raises(ValueError):
            create_ticket(db, None, None, None, None)
            
def test_create_user_group(client, init_database):
    with client as test_client:
        ugroup = create_user_group(db, user_id = 1, group_id = 2, rank_in_group = 1)
        assert db.session.query(User_Groups).get((ugroup.user_id,ugroup.group_id))
        assert db.session.query(User_Groups).get((ugroup.user_id,ugroup.group_id)).rank_in_group == 1
        with pytest.raises(ValueError):
            create_user_group(db, 1,2,10)
        with pytest.raises(ValueError):
            create_user_group(db, 1,2, 1.4)
        with pytest.raises(ValueError):
            create_user_group(db, None, None)

'''READ'''

def test_read_user(client, init_database):
    with client as test_client:
        num_fixture_users = len(db.session.query(User).all())
        user = create_user(db, email = "my_user@gmail.com", password = "password", username = "myusername")
        user_read = read_user(db, user_id = user.id)
        assert user.id == user_read.id
        user_second = create_user(db, email = "my_second_user@gmail.com", password = "password", username = "myusername2")
        create_user(db, email = "my_third_user@gmail.com", password = "password", username = "myusername2")
        all_users = read_user(db)
        assert len(all_users) == 3 + num_fixture_users
        read_u2 = read_user(db, email = "my_second_user@gmail.com")
        assert read_u2
        assert read_u2.id == user_second.id
        read_u3 = read_user(db, username = "myusername2")
        assert read_u3
        assert len(read_u3) == 2
        read_u4 = read_user(db, email = "my_second_user@gmail.com", username = "myusername")
        assert not read_u4

def test_read_comment(client, init_database):
    with client as test_client:
        t1 = create_comment(db, user_id = 1, ticket_id = 1, content = "alphabet soup", time_posted = datetime(year = 2000, month = 1, day = 1))
        t2 = create_comment(db, user_id = 2, ticket_id = 2, content = "alphabet factory", time_posted = datetime(year = 2000, month = 1, day = 7))
        t3 = create_comment(db, user_id = 1, ticket_id = 2, content = "soup factory", time_posted = datetime(year = 2000, month = 1, day = 8))

        assert read_comment(db) #comments exist
        assert len(read_comment(db)) == 3 #there are 3 of them
        assert read_comment(db, id = t1.id).id == t1.id
        assert read_comment(db, id = t2.id).id != t1.id
        assert read_comment(db, id = t2.id).id == t2.id
        assert read_comment(db, time_posted = [datetime(year= 2000, month = 1, day = 1), datetime(year = 2000, month = 1, day = 7)])
        assert len(read_comment(db, time_posted = [datetime(year= 2000, month = 1, day = 1), datetime(year = 2000, month = 1, day = 7)])) == 2
        assert not read_comment(db, time_posted= [datetime(year= 2001, month = 1, day = 1), datetime(year = 2002, month = 1, day = 7)])
        assert read_comment(db, content = "alphabet")
        assert len(read_comment(db, content = "alphabet")) == 2
        assert len(read_comment(db, content = "alphabet factory")) == 1
        assert not read_comment(db, content = "Blueberries")
        assert read_comment(db, user_id = 1)
        assert len(read_comment(db, user_id = 1)) == 2
        assert len(read_comment(db, user_id = 2)) == 1
        assert not read_comment(db, user_id = 0)
        assert read_comment(db, ticket_id = 1)
        assert not read_comment(db, ticket_id = 0)
        assert len(read_comment(db, user_id = 1, ticket_id = 1)) == 1

def test_read_group(client, init_database):
    with client as test_client:
        assert not read_group(db)
        g1 = create_group(db, "Avocado factory")
        g2 = create_group(db, "Factory avocado")
        g3 = create_group(db, "California Avocados")
        assert read_group(db)
        assert read_group(db, id = g1.id).id == g1.id
        assert read_group(db, id = g2.id).id == g2.id
        assert read_group(db, id = g3.id).id == g3.id
        assert not read_group(db, group_name = "avocado factory")
        assert read_group(db, group_name = "Avocado factory")
        assert len(read_group(db, group_name= "avocado", approximate_match=True)) == 3
        assert len(read_group(db, group_name= "factory", approximate_match=True)) == 2
        assert len(read_group(db, group_name= "california", approximate_match=True)) == 1

def test_read_ticket(client, init_database):
    with client as test_client:
        assert not read_ticket(db)
        t1 = create_ticket(db, 1, 1, title = "ticket title1",content = "ticket content 1", resolved = False, priority = 0, time_posted = datetime(year = 2000, month = 1, day = 1))
        t2 = create_ticket(db, 1, 2, title = "ticket title2",content = "ticket content 2", resolved = True, priority = 1, time_posted = datetime(year = 2000, month = 1, day = 2))
        t3 = create_ticket(db, 2, 1, title = "ticket title3",content = "ticket content 3", resolved = True, priority = 2, time_posted = datetime(year = 2000, month = 1, day = 3))
        assert read_ticket(db)
        assert read_ticket(db, id = t1.id).id == t1.id
        print(read_ticket(db, time_posted = [datetime(year = 2000, month = 1, day = 1), datetime(year = 2000, month = 1, day = 2)]))
        assert len(read_ticket(db, time_posted = [datetime(year = 2000, month = 1, day = 1), datetime(year = 2000, month = 1, day = 2)])) == 2
        assert not read_ticket(db, time_posted = [datetime(year = 2000, month = 2, day = 1), datetime(year = 2000, month = 1, day = 2)])
        with pytest.raises(ValueError):
            read_ticket(db, time_posted = [1,2,3])
        with pytest.raises(ValueError):
            read_ticket(db, time_resolved = [1,2,3])
        assert len(read_ticket(db, resolved = False)) == 1
        assert len(read_ticket(db, resolved = True)) == 2
        assert read_ticket(db, priority = 0)[0].id == t1.id
        assert len(read_ticket(db, content = "ticket")) == 3
        assert len(read_ticket(db, content = "2")) == 1
        assert len(read_ticket(db, content = "ticket content 3")) == 1
        assert not read_ticket(db, content = "Blueberries")
        assert len(read_ticket(db, title = "title")) == 3
        assert len(read_ticket(db, title = "le2")) == 1
        assert read_ticket(db, title = "ticket title2")[0].id == t2.id
        assert len(read_ticket(db, user_id = 1)) == 2
        assert len(read_ticket(db, group_id = 2)) == 1
        assert not read_ticket(db, user_id = 0)
        assert not read_ticket(db, group_id = 0)

def test_read_user_group(client, init_database):
    with client as test_client:
        ug1 = create_user_group(db, user_id=1,group_id=1, rank_in_group= 0)
        ug2 = create_user_group(db, user_id=2,group_id=1, rank_in_group= 1)
        ug3 = create_user_group(db, user_id=3,group_id=2, rank_in_group= 2)
        create_user_group(db, user_id=3,group_id=1, rank_in_group= 2)
        assert read_user_group(db)
        assert len(read_user_group(db)) == 4
        assert read_user_group(db, user_id=1, group_id=1).rank_in_group == ug1.rank_in_group
        assert read_user_group(db, user_id=2, group_id=1).rank_in_group == ug2.rank_in_group
        assert read_user_group(db, user_id=3, group_id=2).rank_in_group == ug3.rank_in_group
        assert read_user_group(db, rank_in_group=1)
        assert len(read_user_group(db, rank_in_group=1)) == 1
        assert len(read_user_group(db, rank_in_group=2)) == 2
        assert read_user_group(db, rank_in_group=1)[0].group_id == ug2.group_id
        assert len(read_user_group(db, group_id = 1)) == 3
        assert len(read_user_group(db, user_id = 3)) == 2
    
'''UPDATE'''
def test_update_user(client, init_database):
    with client as test_client:
        the_user = create_user(db, email = "myuser@email.com", password = "password123", username = "theusername")
        updated = update_user(db, the_user.id)
        assert the_user.id == updated.id
        assert the_user.email == updated.email
        assert the_user.password == updated.password
        assert the_user.username == updated.username
        update_user(db, the_user.id, email = "mynewuser@gmail.com")
        assert the_user.id == the_user.id
        assert the_user.email == "mynewuser@gmail.com"
        assert the_user.email != "myuser@gmail.com"
        update_user(db, the_user.id, password = "myNewPasswordIsThis")
        assert check_password_hash(the_user.password,"myNewPasswordIsThis")
        assert not check_password_hash(the_user.password, "password123")
        update_user(db, the_user.id, username = "theNewUserName")
        assert the_user.username == "theNewUserName"
        assert the_user.username != "theusername"
        user2 = create_user(db, email = "changingEverything@email.com", password = "thisWillChangeSoon", username = "temporaryAtBest")
        update_user(db, user2.id, email = "myDifferentEmail@email.com", password = "myDifferentPassword", username = "myDifferentUsername")
        assert user2
        assert user2.email == "myDifferentEmail@email.com"
        assert user2.email != "changingEverything@email.com"
        assert not check_password_hash(user2.password,"thisWillChangeSoon")
        assert check_password_hash(user2.password, "myDifferentPassword")
        assert user2.username == "myDifferentUsername"
        assert user2.username != "temporaryAtBest"

def test_update_comment(client, init_database, time_posted):
    with client as test_client:
        comment = create_comment(db,user_id=1, ticket_id = 2, content = "oldContent", time_posted=time_posted)
        assert comment
        with pytest.raises(ValueError):
            update_comment(db, id = "adas")
        update_comment(db, id = comment.id)
        assert comment.user_id == 1
        assert comment.ticket_id == 2
        assert comment.content == "oldContent"
        assert comment.time_posted == time_posted

        update_comment(db, id = comment.id, time_posted = datetime(year = 2000, month = 1, day = 1))
        assert comment.user_id == 1
        assert comment.ticket_id == 2
        assert comment.content == "oldContent"
        assert comment.time_posted == datetime(year = 2000, month = 1, day = 1)

        update_comment(db, id = comment.id, user_id = 2)
        assert comment.user_id == 2
        assert comment.ticket_id == 2
        assert comment.content == "oldContent"
        assert comment.time_posted == datetime(year = 2000, month = 1, day = 1)

        update_comment(db, id = comment.id, ticket_id = 1)
        assert comment.user_id == 2
        assert comment.ticket_id == 1
        assert comment.content == "oldContent"
        assert comment.time_posted == datetime(year = 2000, month = 1, day = 1)

        update_comment(db, id = comment.id, content = "newContent")
        assert comment.user_id == 2
        assert comment.ticket_id == 1
        assert comment.content == "newContent"
        assert comment.time_posted == datetime(year = 2000, month = 1, day = 1)

        update_comment(db, id = comment.id, time_posted = datetime(year = 2001, month = 2, day = 2), user_id = 3, ticket_id = 4, content = "newestContent")
        assert comment.user_id == 3
        assert comment.ticket_id == 4
        assert comment.content == "newestContent"
        assert comment.time_posted == datetime(year = 2001, month = 2, day = 2)

def test_update_group(client, init_database):
    with client as test_client:
        group = create_group(db, "new group")
        update_group(db, group.id)
        assert group.group_name == "new group"
        update_group(db, group.id, group_name="other group")
        assert group.group_name == "other group"
        with pytest.raises(ValueError):
            update_group(db, id = "ASDASDAS")

def test_update_ticket(client, init_database, time_posted):
    with client as test_client:
        ticket = create_ticket(db, user_id = 1, group_id = 1, title = "title", content = "content", resolved = False, priority = 0,
        time_posted = time_posted)
        with pytest.raises(ValueError):
            update_ticket(db, ticket.id, priority = "foo")
        update_ticket(db, id = ticket.id, time_posted = datetime(year=200,month=2,day=17), time_resolved= datetime(year=200,month=9,day=9), title = "newTitle",\
            content = "newContent", resolved=True, priority = 2, user_id = 7, group_id = 8)
        assert ticket.time_posted == datetime(year=200,month=2,day=17)
        assert ticket.time_resolved == datetime(year=200,month=9,day=9)
        assert ticket.title == "newTitle"
        assert ticket.content == "newContent"
        assert ticket.resolved == True
        assert ticket.priority == 2
        assert ticket.user_id == 7
        assert ticket.group_id == 8
        update_ticket(db, id = ticket.id, nullgroup = True)
        assert ticket.group_id == None

def test_update_user_group(client, init_database):
    with client as test_client:
        user_group = create_user_group(db, user_id = 1, group_id = 2, rank_in_group = 0)

        assert user_group
        with pytest.raises(ValueError):
            update_user_group(db, user_group.user_id, user_group.group_id, rank_in_group="Fooo")
        update_user_group(db, user_group.user_id, user_group.group_id, rank_in_group=2)
        assert user_group.rank_in_group == 2

'''DELETE'''
def test_delete_user(client, init_database):
    with client as test_client:
        original_count = db.session.query(User).count()
        user = create_user(db, email = "newuser@email.com", password = "password", username = "newuser")
        assert user
        assert db.session.query(User).count() == original_count + 1
        delete_user(db, user.id)
        assert db.session.query(User).count() == original_count
        with pytest.raises(ValueError):
            delete_user(db, None)

def test_delete_comment(client, init_database):
    with client as test_client:
        db.create_all()
        t1 = create_comment(db, user_id = 1, ticket_id = 1, content = "alphabet soup", time_posted = datetime(year = 2000, month = 1, day = 1))
        t2 = create_comment(db, user_id = 2, ticket_id = 2, content = "alphabet factory", time_posted = datetime(year = 2000, month = 1, day = 7))
        t3 = create_comment(db, user_id = 1, ticket_id = 2, content = "soup factory", time_posted = datetime(year = 2000, month = 1, day = 8))
        assert len(read_comment(db)) == 3
        delete_comment(db, id = t1.id)
        assert len(read_comment(db)) == 2
        assert read_comment(db, t2.id).id == t2.id
        assert read_comment(db, t3.id).id == t3.id
        assert read_comment(db, t1.id) is None
        with pytest.raises(ValueError):
            delete_comment(db, None)

def test_delete_group(client, init_database):
    with client as test_client:
        g1 = create_group(db, "Avocado factory")
        g2 = create_group(db, "Factory avocado")
        g3 = create_group(db, "California Avocados")
        assert len(read_group(db)) == 3
        delete_group(db, g1.id)
        assert len(read_group(db)) == 2
        assert read_group(db, id = g2.id).id == g2.id
        assert read_group(db, id = g3.id).id == g3.id
        with pytest.raises(ValueError):
            delete_group(db, None)

def test_delete_ticket(client, init_database):
    with client as test_client:
        t1 = create_ticket(db, 1, 1, title = "ticket title1",content = "ticket content 1", resolved = False, priority = 0, time_posted = datetime(year = 2000, month = 1, day = 1))
        t2 = create_ticket(db, 1, 2, title = "ticket title2",content = "ticket content 2", resolved = True, priority = 1, time_posted = datetime(year = 2000, month = 1, day = 2))
        t3 = create_ticket(db, 2, 1, title = "ticket title3",content = "ticket content 3", resolved = True, priority = 2, time_posted = datetime(year = 2000, month = 1, day = 3))
        assert len(read_ticket(db)) == 3
        delete_ticket(db, id = t1.id)
        assert len(read_ticket(db)) == 2
        assert read_ticket(db, id = t2.id).id == t2.id
        assert read_ticket(db, id = t3.id).id == t3.id

def test_delete_user_group(client, init_database):
    with client as test_client:
        ug1 = create_user_group(db, user_id = 1, group_id = 2, rank_in_group = 0)
        ug2 = create_user_group(db, user_id = 1, group_id = 3, rank_in_group = 2)
        assert len(read_user_group(db)) == 2
        delete_user_group(db, ug1.user_id, ug1.group_id)
        assert len(read_user_group(db)) == 1
        assert read_user_group(db, ug2.user_id, ug2.group_id).user_id == ug2.user_id
        assert read_user_group(db, ug2.user_id, ug2.group_id).group_id == ug2.group_id
        assert read_user_group(db, ug2.user_id, ug2.group_id).rank_in_group == ug2.rank_in_group