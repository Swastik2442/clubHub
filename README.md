# University's Club Hub & Event Calendar
### Problem Statement
A University has multiple clubs that serve various subjects of interest. Each club has its President, Vice-president, Faculty Mentor, Coordinators, Volunteers and Members.

The clubs organise multiple events of various categories like Cultural, Technical, Sports etc., either singularly or in collaboration with other clubs.
Each event has its core team and its operations team. The core team consists of Student Members and Mentor Members.

The Operations Team consists of various sub-teams based on the event type. Each sub-team consists of one Core Coordinator, multiple Coordinators, and multiple Volunteers.

Each event has Sub-Events which are handled by a Core Coordinator and a Coordinator.

Create a Database Management System that serves as an Event Calendar and a Member Info System for the University.

### Setup
1. `git clone https://github.com/Swastik2442/clubHub`
2. `python -venv env`
3. `env\Scripts\activate` or `env\Scripts\activate.bat`
4. `pip install -r ./clubHub/requirements.txt`
5. Create & Set the `.env` file according to `.envexample` file.
6. `cd ./clubHub/clubHub`
7. `python manage.py migrate`
8. `python manage.py createsuperuser`
9. Fill in the Details to make Application Admin User.
10. `python manage.py runserver`
11. Go to http://127.0.0.1:8000/admin/ and log in with the Application Admin User.
12. Create a Group `clubAdmin`.
13. Create Club Admin Users and add them to `clubAdmin` Group.

### Uses
* SQL Server/SQLite
* Django
* FullCalendar
* Bootstrap 5
* JQuery
* Waypoint

Made in Collaboration with [@SaurabhSaini04](https://github.com/SaurabhSaini04) and [@SourabhYadav](#).