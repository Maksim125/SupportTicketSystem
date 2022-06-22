# SupportTicketSystem

[Read about the build process](https://www.maxyarmak.tech/projects/support-ticket-system) <br>
[Check out the website](http://ma125.pythonanywhere.com/)

## About the project

This is a website built using the Flask framework, SQLAlchemy ORM, Python, and a PostgreSQL database on the backend, with vanilla Javascript, CSS, and HTML for the front end.

The website exists to be a place where you can issue and resolve support tickets for your organization or projects.

### Overview
- Authentication
  - Users can create accounts with an email, username, and password.
  - The password is encrypted in the database using the SHA-256 hashing algorithm.
- Groups
  - Users can create, join, and leave groups that are focused on a specific problem.
  - Within groups, users are ranked: General User, Authorized User, and Admin.
    - General users can resolve tickets, but are unable to delete other's comments or tickets in groups they are in.
    - Authorized users are able to resolve tickets, and delete tickets and comments.
    - Admins are able to do everything, and also re-rank users in their groups.
  - When creating a new group or joining an abandonded group you become its Admin. When joining a group with other users, you are a general user by default unless an admin re-ranks you.
- Tickets
  - A user can submit a ticket to the universal group- of which everyone has the privileges of an authorized user, and it will be visible to everyone until it is resolved or deleted.
  - A user can also submit tickets to any group that they happen to be in, where only the members of those groups will see the tickets.
  - A ticket has 4 priority ratings: Whenever, Nice to have, Important, and Critical. The rating is chosen by a user when the ticket is created.
    - These ratings are displayed on the ticket previews and will decide where in the feed the ticket appears for other users.
  - Tickets on the home page are ordered by:
    - Resolution: you only see unresolved tickets here
    - Priority: the most important tickets are first in your feed
    - Age: the oldest tickets are first in your feed
  - Tickets on your page are ordered by:
    - Resolution: Unresolved tickets appear first, resolved tickets are at the bottom of the page.
    - Age: Your most recent tickets appear first.
  - Tickets can be marked resolved, and will no longer appear in other's feeds.
- Comments
  - Attached to tickets, and allow users to ask questions or follow up on the ticket.
  - When a ticket is resolved, the resolver generates an identifying comment to show who resolved the ticket.

## Technologies Used

    Python
        Flask
        SQLAlchemy
        Pytest
        Werkzeug        
    Javascript
    HTML
    CSS
    PostgreSQL
    SQLite

<hr>

<i> The project in this repo uses a local SQLite database for your convenience. This avoids the hassle of authenticating access to the PostgreSQL database server that the live website [here](http://ma125.pythonanywhere.com/) uses for anyone who wants to try to run this locally on their machine. </i>

<hr>

## Setup




### Dependencies
    python 3.7
    pipenv

### Getting started
Running the website on local host is as simple as:

    pipenv --python 3.7
    pipenv install -r requirements.txt
    python setup.py

This will create a new virtual environment with python version 3.7, install all necessary packages, and run the website.
