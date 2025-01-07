# COMP2001-REPORT-Project
Introduction:
This is a Trail micro-service application that exposes api endpoints that allow systems to retrieve hiking trail data stored in a SQL 
This repository contains the source code for a Trail micro-service application that exposes API endpoints that allow various systems to receive hiking trail data that is stored in a SQL server database.

Features:
Trails can be viewed, created, updated, deleted. Creation, updating and deletion are done by Admins. Normal users can view the trails but not all the information. 

Admins can view, create, update and delete user accounts. 

Authentication process with JWT tokens.

RESTful app design.

How to run the app:
Once you run the docker image, head over to the swagger UI.

    "username": "Grace Hopper",
    "email": "grace@plymouth.ac.uk",
    "password": "ISAD123!",
    "role": "admin"
    
    "username": "Tim Berners-Lee",
    "email": "tim@plymouth.ac.uk",
    "password": "COMP2001!",
    "role": "user"

    "username": "Ada Lovelace",
    "email": "ada@plymouth.ac.uk",
    "password": "insecurePassword",
    "role": "admin"
These are some of the accounts on the SQL server database. I've set two of the users to be admins and one to be a user.
There is a login process in the User section of the swagger UI. There it gives you an authentication token that you have to enter at the top right on the swagger UI where it says "Authenticate". Enter the token in the format "Bearer [token]"
