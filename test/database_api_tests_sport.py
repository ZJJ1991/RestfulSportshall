import sqlite3, unittest

from .database_api_tests_common import BaseTestCase, db, db_path

class SportDbAPITestCase(BaseTestCase):
 
    #the strip function removes the tabs generated.
    sport1 = {'sport_id':'sport-1', 'sportname':'Football' ,
                   'time':'9','hallnumber':2
             }
            
    sport2 = {'sport_id':'sport-3', 'sportname':'Gym' ,
                   'time':'13','hallnumber':1
             }
             
    user_name='irtiza'         
    


    sport1_name = 'Football'
    sport2_name = 'Gym'
    False_name = 'noName'
    user_name='irtiza' 
    sportUser = {'sport_id':'spt-1', 'sportname': sport1_name,
                   'timestamp':232323,'hallname':1, 'username':user_name,
                }
    

    initial_size = 5

    @classmethod
    def setUpClass(cls):
        print "Testing ", cls.__name__

    def test_sports_table_created(self):
        '''
        Checks that the sports table has 5 records.
        '''
        print '('+self.test_sports_table_created.__name__+')', \
               self.test_sports_table_created.__doc__
        #Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query = 'SELECT * FROM sports'
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
            users = cur.fetchall()
            #Assert
            self.assertEquals(len(users), self.initial_size)
        if con:
            con.close()
   
    def test__create_sport_list_object(self):
        '''
        Check that the method _create_sport_list_object works return adequate 
        values for the first database row.
        '''
        print '('+self.test__create_sport_list_object.__name__+')', \
               self.test__create_sport_list_object.__doc__
        #Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query = 'SELECT * FROM sports WHERE sport_id = 1'
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
            sport = db._create_sport_list_object(row)
            self.assertDictContainsSubset(sport, self.sport1)
   
    def test_get_sport(self):
        '''
        Test get_sport with with football and gym
        '''
        print '('+self.test_get_sport.__name__+')', \
              self.test_get_sport.__doc__
        #Test with an existing message
        message = db.getSport(self.sport1_name)
        self.assertDictContainsSubset(message, self.sport1)
        message = db.getSport(self.sport2_name)
        self.assertDictContainsSubset(message, self.sport2)

    def test_get_sport_falsename(self):
        '''
        Test get_sport with false sport name
        '''
        print '('+self.test_get_sport_falsename.__name__+')', \
              self.test_get_sport_falsename.__doc__
        #Test with an existing message
        sport = db.getSport(self.False_name)
        self.assertIsNone(sport)    

    def test_get_sports(self):
        '''
        Test that get_sports work correctly
        '''
        print '('+self.test_get_sports.__name__+')', self.test_get_sports.__doc__
        sports = db.getSports()
        #Check that the size is correct
        self.assertEquals(len(sports), self.initial_size)
        #Iterate throug messages and check if the messages with message1_id and
        #message2_id are correct:
        for sport in sports:
            if sport['sportname'] == self.sport1_name:
                self.assertDictContainsSubset(sport, self.sport1)
            elif sport['sportname'] == self.sport2_name:
                self.assertDictContainsSubset(sport, self.sport2)

    def test_get_sport_specific_user(self):
        '''
        Get all sports from specific user
        '''
        #Messages sent from Mystery are 13 and 14
        print '('+self.test_get_sport_specific_user.__name__+')', \
        self.test_get_sport_specific_user.__doc__
        userSports = db.getUserSport(self.user_name)
        
        for userSport in userSports:
            if userSport['username']==self.user_name:
                self.assertDictContainsSubset(userSport, self.sportUser)
  

if __name__ == '__main__':
    print 'Start running tests'
    unittest.main()

