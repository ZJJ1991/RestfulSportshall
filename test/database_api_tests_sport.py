'''
Created on 05.06.2016
Modified on 06.06.2016
Database interface testing for all sports related methods.

@author: chen haoyu
'''
import unittest, sqlite3
from forum import database

#Path to the database file, different from the deployment db
DB_PATH = 'db/forum_test.db'
ENGINE = database.Engine(DB_PATH)

#CONSTANTS DEFINING DIFFERENT SPORTS AND SPORT PROPERTIES
SPORT1_ID = 1
SPORTNAME1= 'run'
SPORTNOTE1 = "for 5 people"
SPORT1 = {'sport id': 1,
            'sport name': 'run',
            'sport time': "251",
            'sporthall number': 2,
            'note': "for 5 people"}
					
SPORT2_ID = 4
SPORTNAME2= 'basket'
SPORTNOTE2 = "for 10 people"
SPORT2 =  {'sport id': 4,
            'sport name': 'basket',
            'sport time': "21",
            'sporthall number': 3,
            'note': "for 10 people"}
			
NEW_SPORT_NAME= 'flying'

NEW_SPORT =  {'sport name': 'flying',
            'sport time': "0315",
            'sporthall number': 99,
            'note': "for 1 people"}			
			
WRONG_SPORT_NAME = 'sleeping'
INITIAL_SIZE = 4


class UserDBAPITestCase(unittest.TestCase):
    '''
    Test cases for the Users related methods.
    '''
    #INITIATION AND TEARDOWN METHODS
    @classmethod
    def setUpClass(cls):
        ''' Creates the database structure. Removes first any preexisting
            database file
        '''
        print "Testing ", cls.__name__
        ENGINE.remove_database()
        print "Testing dab remove ", cls.__name__
        ENGINE.create_tables()
        print "Testing createding dab", cls.__name__
		
    @classmethod	
    def tearDownClass(cls):
        '''Remove the testing database'''
        print "Testing ENDED for ", cls.__name__
        ENGINE.remove_database()   

    def setUp(self):
        '''
        Populates the database
        '''
        #This method load the initial values from forum_data_dump.sql
        ENGINE.populate_tables()
        #Creates a Connection instance to use the API
        self.connection = ENGINE.connect()

    def tearDown(self):
        '''
        Close underlying connection and remove all records from database
        '''
        self.connection.close()
        ENGINE.clear()

    def test_sports_table_created(self):
        '''
        Checks that the table initially contains 5 sports (check
        forum_data_dump.sql). NOTE: Do not use Connection instance but
        call directly SQL.
        '''
        print '('+self.test_sports_table_created.__name__+')', \
              self.test_sports_table_created.__doc__
        #Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query = 'SELECT * FROM sports'
        #Connects to the database.
        con = self.connection.con
        with con:
            #Cursor and row initialization
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            #Provide support for foreign keys
            cur.execute(keys_on)
            #Execute main SQL Statement
            cur.execute(query)
            sports = cur.fetchall()
            #Assert	
            self.assertEquals(len(sports), INITIAL_SIZE)

    def test_create_sport_object(self):
        '''
        Check that the method create_sport_object works return adequate values
        for the first database row. NOTE: Do not use Connection instace to
        extract data from database but call directly SQL.
        '''
        print '('+self.test_create_sport_object.__name__+')', \
              self.test_create_sport_object.__doc__
        #Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query = 'SELECT sports.* FROM sports'
        #Get the sqlite3 con from the Connection instance
        con = self.connection.con
        #I am doing operations after with, so I must explicitly close the
        # the connection to be sure that no locks are kepts. The with, close
        # the connection when it has gone out of scope
        #try:
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
    #finally:
        #    con.close()
        #Test the method
        sport = self.connection._create_sport_object(row)
        self.assertDictContainsSubset(sport, SPORT1)

    def test_get_sport(self):
        '''
        Test get_sport with name run and jog
        '''
        print '('+self.test_get_sport.__name__+')', \
              self.test_get_sport.__doc__

        #Test with an existing sport
        sport = self.connection.get_sport(SPORTNAME1)
        self.assertEquals(sport['note'], SPORTNOTE1)
        sport = self.connection.get_sport(SPORTNAME2)
        self.assertEquals(sport['note'], SPORTNOTE2)
		
    def test_get_sport_noexistingname(self):
        '''
        Test get_sport with  wring sportname (no-existing)
        '''
        print '('+self.test_get_sport_noexistingname.__name__+')', \
              self.test_get_sport_noexistingname.__doc__

        #Test with an existing sport
        sport = self.connection.get_sport(WRONG_SPORT_NAME)
        self.assertIsNone(sport)
		
    def test_get_sports(self):
        '''
        Test that get_sports work correctly and extract required sport info
        '''
        print '('+self.test_get_sports.__name__+')', \
              self.test_get_sports.__doc__
        sports = self.connection.get_sports()
        #Check that the size is correct
        self.assertEquals(len(sports), INITIAL_SIZE)
        #Iterate throug sports and check if the sports with SPORT_ID and
        #SPORT2_ID are correct:
        for sport in sports:
            if sport['sport_id'] == SPORT1_ID:
                self.assertEquals(sport['sportname'], SPORTNAME1)
            elif sport['sport_id'] == SPORT2_ID:
                self.assertEquals(sport['sportname'], SPORTNAME2)
				
    def test_delete_sport(self):
        '''
        Test that the sport run is deleted
        '''
        print '('+self.test_delete_sport.__name__+')', \
              self.test_delete_sport.__doc__
        resp = self.connection.delete_sport(SPORTNAME1)
        self.assertTrue(resp)
        #Check that the sports has been really deleted throug a get
        resp2 = self.connection.get_sport(SPORTNAME1)
        self.assertIsNone(resp2)
		
    def test_delete_sport_noexistingsportname(self):
        '''
        Test delete_sport with  Batty (no-existing)
        '''
        print '('+self.test_delete_sport_noexistingsportname.__name__+')', \
              self.test_delete_sport_noexistingsportname.__doc__
        #Test with an existing sport
        resp = self.connection.delete_sport(WRONG_SPORT_NAME)
        self.assertFalse(resp)	

    def test_append_sport(self):
        '''
        Test that I can add new sports
        '''
        print '('+self.test_append_sport.__name__+')', \
              self.test_append_sport.__doc__
        sportname = self.connection.append_sport(NEW_SPORT_NAME, NEW_SPORT)
        self.assertIsNotNone(sportname)
        self.assertEquals(sportname, NEW_SPORT_NAME)
        #Check that the orders has been really modified through a get
        resp2 = self.connection.get_sport(sportname)
        self.assertDictContainsSubset(NEW_SPORT,resp2)		
			

if __name__ == '__main__':
    print 'Start running sport tests'
    unittest.main()
