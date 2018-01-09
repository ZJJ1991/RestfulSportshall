database API guideline

db folder is to store database
while forum folder is to store API and API testing file

1). All dependencies (external libraries).
python 2.7, sqlite3£¬ flask

2). Setup the database framework. 
open terminal window, run python
then input sentences below:
import forum.database as database
engine = database.Engine()
con = engine.connect()
con.check_foreign_keys_status()
con.set_foreign_keys_support()
con.check_foreign_keys_status()

3). Instructions on how to setup and populate the database.
create user table by inputting this sentence:
engine.create_user_table()
change user into user_profile, friends, sports, orders to create each table

4). Instruction on how to run the tests of your database.
test each API by inputting this sentence:
con.get_user()
change get_users() into get_user() and other APIs to test each API

5). RESTful API test
1. Go to the root of the repository in your cmd terminal
2. To set local server run the following code:
   python -m test.resources_api_tests.py
3. To see the testing results in terminal

6). How to use our application
1. go to whole-project folder in cmd teminal 
2. run "python forum.py"
3. browse localhost:5000/forum_admin/login.html
4. Do everything as you like
