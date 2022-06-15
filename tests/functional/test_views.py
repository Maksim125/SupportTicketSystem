from flask import request

'''
All non-authenticated page view requests to anything except the login or signup page should redirect to the login page
'''
def test_home_page(client):
    with client as test_client:
        response = test_client.get("/", follow_redirects = True)
        assert response.status_code == 200
        assert request.path == "/login" #You should be redirected to the login page

def test_new_ticket(client):
    with client as test_client:
        response = test_client.get("/newticket", follow_redirects = True)
        assert response.status_code == 200
        assert request.path == "/login" #You should be redirected to the login page

def test_my_tickets(client):
    with client as test_client:
        response = test_client.get("/mytickets", follow_redirects = True)
        assert response.status_code == 200
        assert request.path == "/login" #You should be redirected to the login page

def test_groups(client):
    with client as test_client:
        response = test_client.get("/groups", follow_redirects = True)
        assert response.status_code == 200
        assert request.path == "/login" #You should be redirected to the login page

def test_view_ticket(client):
    with client as test_client:
        response = test_client.get("/view-ticket", follow_redirects = True)
        assert response.status_code == 200
        assert request.path == "/login" #You should be redirected to the login page

'''
Sign-up and login pages should not redirect
'''
def test_view_signup(client):
    with client as test_client:
        response = test_client.get("/sign-up", follow_redirects = False)
        assert response.status_code == 200
        assert request.path == "/sign-up" 

def test_view_login(client):
    with client as test_client:
        response = test_client.get("/login", follow_redirects = False)
        assert response.status_code == 200
        assert request.path == "/login" 

'''
User is authenticated, they should be able to get to each view
'''
def test_home_page_authed(client, init_database,login_default_user):
    with client as test_client:
        response = test_client.get("/", follow_redirects = False)
        assert response.status_code == 200
        assert request.path == "/"

def test_mytickets_authed(client, init_database,login_default_user):
    with client as test_client:
        response = test_client.get("/mytickets", follow_redirects = False)
        assert response.status_code == 200
        assert request.path == "/mytickets"

def test_newticket_authed(client, init_database,login_default_user):
    with client as test_client:
        response = test_client.get("/newticket", follow_redirects = False)
        assert response.status_code == 200
        assert request.path == "/newticket"

def test_groups_authed(client, init_database,login_default_user):
    with client as test_client:
        response = test_client.get("/groups", follow_redirects = False)
        assert response.status_code == 200
        assert request.path == "/groups"

def test_viewticket_authed(client, init_database,login_default_user):
    with client as test_client:
        response = test_client.get("/view-ticket", follow_redirects = False)
        assert response.status_code == 200