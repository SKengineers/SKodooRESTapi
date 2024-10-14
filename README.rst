Odoo REST API
=============
* This module allow us to connect to database with REST API requests

Configuration
-----------
* Set up the config file ( db_filter = your database working with API )
* Authentication using Postman with login credentials
* API key generation
* Communicate with database using API requests


How to set up login API KEY
-----------
- Step 1: In header of API request, add "login" and "password" and "db" for create API-KEY for user.
- Step 2: After step 1, you will receive an API-KEY in response, then copy that and bring it into header with key = "api-key" and value = API-KEY in response.
- Step 3: Call to every API you want
