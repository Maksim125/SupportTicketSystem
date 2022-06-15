from cgi import test
from venv import create
import pytest
from SupportTicketSystem import create_app, crud_operations, db
from SupportTicketSystem.models import User
from datetime import datetime

config = {
    "TESTING":True,
    "SECRET_KEY" : "TEST",
    "SQLALCHEMY_DATABASE_URI" : "sqlite:///",
    "SQLALCHEMY_TRACK_MODIFICATIONS" : False
}

@pytest.fixture(scope = "module")
def client():
    flask_app = create_app(config = config)
    testing_client = flask_app.test_client()
    ctx = flask_app.app_context()
    ctx.push()
    yield testing_client
    ctx.pop()

@pytest.fixture(scope = "function")
def init_database(client):
    db.create_all()
    db.session.add(User(email = "user@place.com", password = "password", username = "user_one"))
    db.session.commit()
    yield
    db.drop_all()

@pytest.fixture(scope = "function")
def login_default_user(client):
    client.post("/login", data = dict(email = "user@place.com", password = "password") ,
        follow_redirects = True)
    yield
    client.get("/logout", follow_redirects=True)

@pytest.fixture(scope = "function")
def init_large_database(client, time_posted):
    db.create_all()
    u1 = crud_operations.create_user(db, email = "user1@email.com", password = "password", username = "username1")
    u2 = crud_operations.create_user(db, email = "user2@email.com", password = "password", username = "username2")
    u3 = crud_operations.create_user(db, email = "user3@email.com", password = "password", username = "username3")
    u4 = crud_operations.create_user(db, email = "user4@email.com", password = "password", username = "username4")
    u5 = crud_operations.create_user(db, email = "user5@email.com", password = "password", username = "username5")
    u6 = crud_operations.create_user(db, email = "user6@email.com", password = "password", username = "username6")

    g1 = crud_operations.create_group(db, group_name = "group1")
    g2 = crud_operations.create_group(db, group_name = "group2")
    g3 = crud_operations.create_group(db, group_name = "group3")
    g4 = crud_operations.create_group(db, group_name = "group4")

    crud_operations.create_user_group(db, u1.id, g1.id, rank_in_group=2)
    crud_operations.create_user_group(db, u2.id, g1.id, rank_in_group=1)
    crud_operations.create_user_group(db, u3.id, g1.id)
    crud_operations.create_user_group(db, u4.id, g1.id)
    crud_operations.create_user_group(db, u5.id, g1.id)

    crud_operations.create_user_group(db, u2.id, g2.id, rank_in_group=2)
    crud_operations.create_user_group(db, u3.id, g2.id)
    crud_operations.create_user_group(db, u4.id, g2.id)

    crud_operations.create_user_group(db, u4.id, g3.id, rank_in_group=2)

    t1 = crud_operations.create_ticket(db, u1.id, g1.id, "ticket 1 title", content = "content 1", priority = 3, time_posted=time_posted)
    crud_operations.create_ticket(db, u2.id, g1.id, "ticket 2 title", content = "content 2", priority = 1, time_posted=time_posted)
    crud_operations.create_ticket(db, u1.id, g2.id, "ticket 3 title", content = "content 3", priority = 2, time_posted=time_posted)
    crud_operations.create_ticket(db, u2.id, g1.id, "ticket 4 title", content = "content 4", priority = 1, time_posted=time_posted, resolved=True)
    crud_operations.create_ticket(db, u1.id, g2.id, "ticket 5 title", content = "content 5", priority = 2, time_posted=time_posted, resolved=True)

    crud_operations.create_comment(db, u1.id, t1.id, "comment content", time_posted=time_posted)
    
    yield
    db.drop_all()


@pytest.fixture()
def time_posted():
    return datetime(year = 2000, month = 4, day = 10)

@pytest.fixture()
def time_resolved():
    return datetime(year= 2000, month =5, day= 9)