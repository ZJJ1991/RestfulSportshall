'''
Created on 05.06.2016
Modified on 21.06.2016
Database interface testing for all orders related methods.

@author: chenhaoyu
'''

import sqlite3, unittest

from forum import database

#Path to the database file, different from the deployment db
DB_PATH = 'db/forum_test.db'
ENGINE = database.Engine(DB_PATH)


#CONSTANTS DEFINING DIFFERENT USERS AND USER PROPERTIES
ORDER1_ID = 'order-1'

ORDER1 = {'order_id': 'order-1',
            'nickname': 'chen',
            'sportname': "swim",
            'timestamp': 123}

ORDER1_MODIFIED = {'order_id': 'order-1',
					'nickname': 'chendashuai',
					'sportname': "swim",
					'timestamp': '548'}
					
ORDER2_ID = 'order-2'

ORDER2 = {'order_id': 'order-2',
					'nickname': 'zhoujj',
					'sportname': "run",
					'timestamp': 355}

WRONG_ORDER_ID = 'order-200'

INITIAL_SIZE = 2


class OrderDBAPITestCase(unittest.TestCase):
    '''
    Test cases for the Orders related methods.
    '''
    #INITIATION AND TEARDOWN METHODS
    @classmethod
    def setUpClass(cls):
        ''' Creates the database structure. Removes first any preexisting
            database file
        '''
        print "Testing ", cls.__name__
        ENGINE.remove_database()
        ENGINE.create_tables()

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

    def test_orders_table_created(self):
        '''
        Checks that the table initially contains 2 orders (check
        forum_data_dump.sql). NOTE: Do not use Connection instance but
        call directly SQL.
        '''
        print '('+self.test_orders_table_created.__name__+')', \
                  self.test_orders_table_created.__doc__
        #Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query = 'SELECT * FROM orders'
        #Get the sqlite3 con from the Connection instance
        con = self.connection.con
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
            self.assertEquals(len(users), INITIAL_SIZE)

    def test_create_order_object(self):
        '''
        Check that the method _create_order_object works return adequate
        values for the first database row. NOTE: Do not use Connection instace
        to extract data from database but call directly SQL.
        '''
        print '('+self.test_create_order_object.__name__+')', \
              self.test_create_order_object.__doc__
        #Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query = 'SELECT * FROM orders WHERE order_id = 1'
        #Get the sqlite3 con from the Connection instance
        con = self.connection.con
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
        order = self.connection._create_order_object(row)
        self.assertDictContainsSubset(order, ORDER1)

    def test_get_order(self):
        '''
        Test get_order with id order-1 and -2
        '''
        print '('+self.test_get_order.__name__+')', \
              self.test_get_order.__doc__
        #Test with an existing order
        order = self.connection.get_order(ORDER1_ID)
        self.assertDictContainsSubset(order, ORDER1)
        order = self.connection.get_order(ORDER2_ID)
        self.assertDictContainsSubset(order, ORDER2)
		
    def test_get_order_malformedid(self):
        '''
        Test get_order with id 1 (malformed)
        '''
        print '('+self.test_get_order_malformedid.__name__+')', \
              self.test_get_order_malformedid.__doc__
        #Test with an existing order
        with self.assertRaises(ValueError):
            self.connection.get_order('1')
			
    def test_get_order_noexistingid(self):
        '''
        Test get_order with order-200 (no-existing)
        '''
        print '('+self.test_get_order_noexistingid.__name__+')',\
              self.test_get_order_noexistingid.__doc__
        #Test with an existing order
        order = self.connection.get_order(WRONG_ORDER_ID)
        self.assertIsNone(order)
		
    def test_get_orders(self):
        '''
        Test that get_orders work correctly
        '''
        print '('+self.test_get_orders.__name__+')', self.test_get_orders.__doc__
        orders = self.connection.get_orders()
        #Check that the size is correct
        self.assertEquals(len(orders), INITIAL_SIZE)
        #Iterate throug orders and check if the orders with ORDER1_ID and
        #ORDER2_ID are correct:
        for order in orders:
            if order['order_id'] == ORDER1_ID:
                self.assertEquals(len(order), 4)
                self.assertDictContainsSubset(order, ORDER1)
            elif order['order_id'] == ORDER2_ID:
                self.assertEquals(len(order), 4)
                self.assertDictContainsSubset(order, ORDER2)
		
    def test_get_orders_specific_user(self):
        '''
        Get all orders from user chen. Check that id 1.
        '''
        #Order created from chen is 1
        print '('+self.test_get_orders_specific_user.__name__+')', \
              self.test_get_orders_specific_user.__doc__
        orders = self.connection.get_orders(nickname="chen")
        self.assertEquals(len(orders), 1)
        #order id is 1
        for order in orders:
            self.assertIn(order['order_id'], ('order-1'))
            self.assertNotIn(order['order_id'], ('order-2'))	
		
    def test_get_orders_length(self):
        '''
        Check that the number_of_orders  is working in get_orders
        '''
        #orders sent from chen is 1
        print '('+self.test_get_orders_length.__name__+')',\
              self.test_get_orders_length.__doc__
        orders = self.connection.get_orders(nickname="chen")
        self.assertEquals(len(orders), 1)
        #Number of orders is 2
        orders = self.connection.get_orders()
        self.assertEquals(len(orders), 2)
		
    def test_delete_order(self):
        '''
        Test that the order order-1 is deleted
        '''
        print '('+self.test_delete_order.__name__+')', \
              self.test_delete_order.__doc__
        resp = self.connection.delete_order(ORDER1_ID)
        self.assertTrue(resp)
        #Check that the orders has been really deleted throug a get
        resp2 = self.connection.get_order(ORDER1_ID)
        self.assertIsNone(resp2)
		
    def test_delete_order_malformedid(self):
        '''
        Test that trying to delete order wit id ='2' raises an error
        '''
        print '('+self.test_delete_order_malformedid.__name__+')', \
              self.test_delete_order_malformedid.__doc__
        #Test with an existing order
        with self.assertRaises(ValueError):
            self.connection.delete_order('1')
			
    def test_delete_order_noexistingid(self):
        '''
        Test delete_order with  order-200 (no-existing)
        '''
        print '('+self.test_delete_order_noexistingid.__name__+')', \
              self.test_delete_order_noexistingid.__doc__
        #Test with an existing order
        resp = self.connection.delete_order(WRONG_ORDER_ID)
        self.assertFalse(resp)		

    def test_create_order(self):
        '''
        Test that a new order can be created
        '''
        print '('+self.test_create_order.__name__+')',\
              self.test_create_order.__doc__
        orderid = self.connection.create_order("doudou", "jog")
        self.assertIsNotNone(orderid)
        #Get the expected modified order
        new_order = {} 
        new_order['nickname'] = 'doudou'
        new_order['sportname'] = 'jog'
        #Check that the orders has been really modified through a get
        resp2 = self.connection.get_order(orderid)
        self.assertDictContainsSubset(new_order, resp2)
        #CHECK NOW NOT REGISTERED USER
        orderid = self.connection.create_order("doudou", "jog")
        self.assertIsNotNone(orderid)
        #Get the expected modified order
        new_order = {}
        new_order['nickname'] = 'doudou'
        new_order['sportname'] = 'jog'
        #Check that the orders has been really modified through a get
        resp2 = self.connection.get_order(orderid)
        self.assertDictContainsSubset(new_order, resp2)
		
    def test_not_contains_order(self):
        '''
        Check if the database does not contain orders with id order-200

        '''
        print '('+self.test_contains_order.__name__+')', \
              self.test_contains_order.__doc__
        self.assertFalse(self.connection.contains_order(WRONG_ORDER_ID))

    def test_contains_order(self):
        '''
        Check if the database contains orders with id order-1 and order-2

        '''
        print '('+self.test_contains_order.__name__+')', \
              self.test_contains_order.__doc__
        self.assertTrue(self.connection.contains_order(ORDER1_ID))
        self.assertTrue(self.connection.contains_order(ORDER2_ID))
		

if __name__ == '__main__':
    print 'Start running order tests'
    unittest.main()
