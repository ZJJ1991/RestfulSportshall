import sqlite3, unittest

from .database_api_tests_common import BaseTestCase, db, db_path

class UserDbAPITestCase(BaseTestCase):

    #the strip function removes the tabs generated.
    user1_nickname = 'irtiza'
    user2_nickname = 'Li'
    user1_id = 2
    user2_id = 3
    user1 = {'public_profile':{'picture':'changed2.jpg',
                               'favoritesport':'golf2',
                               'nickname':'irti',
                               'email':'ihasan@ee.oulu.fi',
                               'registrationdate':12},
             'restricted_profile':{'mobile':'12457845', 'profession':'chnaged',
                                   'id':2,
                                   'skype':'ichanged'}
            }
            
    userCheck = {'id':'usr-2', 'username': user1_nickname,
                   'dateofbirth':'23-05-1990', 'email':'ihasan@ee.oulu.fi',
                }
    userCheck2 = {'id':'usr-3', 'username': user2_nickname,
                   'dateofbirth':'12-12-2000', 'email':'li@yahoo.com',
                }
    modified_user1 ={'public_profile':{'picture':'changed2as.jpg',
                               'favoritesport':'golf2as',
                               'nickname':'irti',
                               'email':'ihasan@ee.oulu.fi',
                               'registrationdate':12},
                    'restricted_profile':{'mobile':'1245784567', 'profession':'engineer',
                                   'id':2,
                                   'skype':'ichangedasd'}
                    }
    
    user2 = {'public_profile':{'picture':'Li.png',
                               'favoritesport':'Gym',
                               'nickname':'LiMontser',
                               'email':'li@yahoo.com',
                               'registrationdate':12},
             'restricted_profile':{'mobile':'46545', 'profession':'Student',
                                   'id':3,
                                   'skype':'li'}
            }
    new_user_nickname = 'sully'
    new_user = {'main_details':{'username':new_user_nickname,
                               'password':'adminssadjfh',
                               'dateofbirth':'6-5-2015',
                               'email':'liLa@yahoo.com',
                               'gender':'male',
                               'student_id':12}
                }
    no_user_nickname = 'Batty'
    initial_size = 3
 
    @classmethod
    def setUpClass(cls):
        print "Testing ", cls.__name__
 
    def test_users_table_created(self):
        '''
        Checks that the table initially contains 3 users (check 
        forum_data_dump.sql)
        '''
        print '('+self.test_users_table_created.__name__+')', \
              self.test_users_table_created.__doc__
        #Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query1 = 'SELECT * FROM users'
        query2 = 'SELECT * FROM usersProfile'
        #Connects to the database.
        con = sqlite3.connect(db_path)
        with con:
            #Cursor and row initialization
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            #Provide support for foreign keys
            cur.execute(keys_on)
            #Execute main SQL Statement        
            cur.execute(query1)
            users = cur.fetchall()
            #Assert
           
            self.assertEquals(len(users),self.initial_size)
            #Check the users_profile:
            cur.execute(query2)
            users = cur.fetchall()
            #Assert
            self.assertEquals(len(users),self.initial_size)
        if con:
            con.close()
            
  
    def test_create_user_object(self):
        '''
        Check that the method _create_one_user_list_object works return adequate values
        for the first database row.
        '''
        print '('+self.test_create_user_object.__name__+')', \
              self.test_create_user_object.__doc__
        #Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query = 'SELECT users.*, usersProfile.* FROM users, usersProfile \
                 WHERE users.id = usersProfile.id'
        #Connects to the database.
        con = sqlite3.connect(db_path)
        with con:
            #Cursor and row initialization
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            #Provide support for foreign keys
            cur.execute(keys_on)
            #Execute main SQL Statement        
            cur.execute(query)
            #Extrac the row
            row = cur.fetchone()
            #Test the method
            user = db._create_one_user_list_object(row)
            self.assertDictContainsSubset(user, self.user1)
            
    
    def test_get_user(self):
        '''
        Test get_user with id irtiza and Li
        '''
        print '('+self.test_get_user.__name__+')', \
              self.test_get_user.__doc__
        #Test with an existing user
        user = db.getUser(self.user1_nickname)
        self.assertDictContainsSubset(user, self.user1)
        user = db.getUser(self.user2_nickname)
        self.assertDictContainsSubset(user, self.user2)
        
   
    def test_get_user_noexistingid(self):
        '''
        Test get_user with  non existing username
        '''
        print '('+self.test_get_user_noexistingid.__name__+')', \
              self.test_get_user_noexistingid.__doc__
        #Test with an non-existing user
        user = db.getUser(self.no_user_nickname)
        self.assertIsNone(user)
   
    def test_get_users(self):
        '''
        Test that get_users work correctly and extract required user info
        '''
        print '('+self.test_get_users.__name__+')', \
              self.test_get_users.__doc__
        users = db.getUsers()
        #Check that the size is correct
        self.assertEquals(len(users), self.initial_size)
        #Iterate throug users and check if the users with user1_id and
        #user2_id are correct:
        for user in users:
            if user['username'] == self.user1_nickname:
                self.assertDictContainsSubset(user, self.userCheck)
            elif user['username'] == self.user2_nickname:
                self.assertDictContainsSubset(user, self.userCheck2)
  
    def test_delete_user(self):
        '''
        Test that the user irtiza is deleted
        '''
        print '('+self.test_delete_user.__name__+')', \
              self.test_delete_user.__doc__
        resp = db.delete_user(self.user1_nickname)
        self.assertTrue(resp)
        #Check that the users has been really deleted throug a get
        resp2 = db.getUser(self.user1_nickname)
        self.assertIsNone(resp2)
        #Check that the user does not have associated any message
       
    
    def test_delete_user_noexistingnickname(self):
        '''
        Test delete_user with  Batty (no-existing)
        '''
        print '('+self.test_delete_user_noexistingnickname.__name__+')', \
              self.test_delete_user_noexistingnickname.__doc__
        #Test with an existing user
        resp = db.delete_user(self.no_user_nickname)
        self.assertFalse(resp)
    
    def test_modify_user(self):
        '''
        Test that the user irtiza is modifed
        '''
        print '('+self.test_modify_user.__name__+')', \
              self.test_modify_user.__doc__
        #Get the modified user
        resp = db.modify_user(self.user1_nickname, self.modified_user1)
        self.assertEquals(resp, self.user1_nickname)
        #Check that the users has been really modified through a get
        resp2 = db.getUser(self.user1_nickname)
        resp_p_profile = resp2['public_profile']
        resp_r_profile = resp2['restricted_profile']
        #Check the expected values
        p_profile = self.modified_user1['public_profile']
        r_profile = self.modified_user1['restricted_profile']
        self.assertEquals(p_profile['email'], 
                          resp_p_profile['email']) 
        self.assertEquals(p_profile['registrationdate'], resp_p_profile['registrationdate']) 
        self.assertEquals(p_profile['nickname'], resp_p_profile['nickname'])
        self.assertEquals(p_profile['picture'], resp_p_profile['picture'])
        self.assertEquals(p_profile['favoritesport'], resp_p_profile['favoritesport'])
        self.assertEquals(r_profile['id'], resp_r_profile['id'])
        self.assertEquals(r_profile['profession'], resp_r_profile['profession'])
        self.assertEquals(r_profile['mobile'], resp_r_profile['mobile']) 
        self.assertEquals(r_profile['skype'], resp_r_profile['skype'])
        self.assertDictContainsSubset(resp2, self.modified_user1)
   
    def test_modify_user_noexistingnickname(self):
        '''
        Test modify_user with  user Batty (no-existing)
        '''
        print '('+self.test_modify_user_noexistingnickname.__name__+')', \
              self.test_modify_user_noexistingnickname.__doc__
        #Test with an existing user
        resp = db.modify_user(self.no_user_nickname, self.user1)
        self.assertIsNone(resp)
    
    def test_append_user(self):
        '''
        Test that I can add new users
        '''
        print '('+self.test_append_user.__name__+')', \
              self.test_append_user.__doc__
        nickname = db.append_user(self.new_user_nickname, self.new_user)
        self.assertIsNotNone(nickname)
        self.assertEquals(nickname, self.new_user_nickname)
        #Check that the messages has been really modified through a get
      
  
    def test_append_existing_user(self):
        '''
        Test that I cannot add two users with the same name
        '''
        print '('+self.test_append_existing_user.__name__+')', \
              self.test_append_existing_user.__doc__
        nickname = db.append_user(self.user1_nickname, self.new_user)
        self.assertIsNone(nickname)
    
    def test_get_user_id(self):
        '''
        Test that get_user_id returns the right value given a nickname
        '''
        print '('+self.test_get_user_id.__name__+')', \
              self.test_get_user_id.__doc__
        id = db.get_user_id(self.user1_nickname)
        self.assertEquals(self.user1_id, id)        
        id = db.get_user_id(self.user2_nickname)
        self.assertEquals(self.user2_id, id)
  
    def test_get_user_id_unknown_user(self):
        '''
        Test that get_user_id returns None when the nickname does not exist
        '''
        print '('+self.test_get_user_id.__name__+')', \
              self.test_get_user_id.__doc__
        id = db.get_user_id(self.no_user_nickname)
        self.assertIsNone(id) 
    
    def test_not_contains_user(self):
        '''
        Check if the database does not contain users with id Batty
        '''
        print '('+self.test_contains_user.__name__+')', \
              self.test_contains_user.__doc__
        self.assertFalse(db.contains_user(self.no_user_nickname))
   
    def test_contains_user(self):
        '''
        Check if the database contains users with nickname irtiza and Li

        '''
        print '('+self.test_contains_user.__name__+')', \
              self.test_contains_user.__doc__
        self.assertTrue(db.contains_user(self.user1_nickname))
        self.assertTrue(db.contains_user(self.user2_nickname))       
        

if __name__ == '__main__':
    print 'Start running tests'
    unittest.main()
