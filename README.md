Provides the database API explaination.

@author: chenhaoyu

db is to store database
forum is to store API

1. All dependencies (external libraries).
python 2.7, sqlite3

2. Setup the database framework. 
open terminal window, run python
then input sentences below:
import forum.database as database
engine = database.Engine()
con = engine.connect()
con.check_foreign_keys_status()
con.set_foreign_keys_support()
con.check_foreign_keys_status()

3. Instructions on how to setup and populate the database.
create user table by inputting this sentence:
engine.create_user_table()
change user into user_profile, friends, sports, orders to create each table

4. Instruction on how to run the tests of your database.
test each API by inputting this sentence:
con.get_user()
change get_users() into get_user() and other APIs to test each API