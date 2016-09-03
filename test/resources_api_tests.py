'''
Created on 26.01.2013
Modified on 24.06.2016
@author: ivan
@modified: chenhaoyu, zhoujunjie
'''
import unittest, copy
import json

import flask

import forum.resources as resources
import forum.database as database
import unittest

DB_PATH = 'db/forum_test.db'
ENGINE = database.Engine(DB_PATH)

COLLECTIONJSON = "application/vnd.collection+json"
HAL = "application/hal+json"

#Tell Flask that I am running it in testing mode.
resources.app.config['TESTING'] = True
#Database Engine utilized in our testing
resources.app.config.update({'Engine': ENGINE})

class ResourcesAPITestCase(unittest.TestCase):
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
        #Create a test client
        self.client = resources.app.test_client()

    def tearDown(self):
        '''
        Remove all records from database
        '''
        ENGINE.clear()

class AllOrdersTestCase (ResourcesAPITestCase):

    url = '/forum/api/orders/'

    def test_url(self):
        '''
        Checks that the URL points to the right resource
        '''
        #NOTE: self.shortDescription() shuould work.
        print '('+self.test_url.__name__+')', self.test_url.__doc__,

        with resources.app.test_request_context(self.url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.AllOrders)

    def test_get_orders(self):
        '''
        Checks that GET Orders return correct status code and data format
        '''
        print '('+self.test_get_orders.__name__+')', self.test_get_orders.__doc__

        with resources.app.test_client() as client:
            resp = client.get(self.url)
            self.assertEquals(resp.status_code, 200)
            data = json.loads(resp.data)
            link = data['collection']['links']
            self.assertEquals(link[0]['title'], 'List of all orders in the sporthall')
            self.assertEquals(link[0]['rel'], 'orders-all')
            self.assertEquals(link[0]['href'],
                              resources.api.url_for(resources.AllOrders))
            orders = data['collection']['items']
            #Just check one order the rest are constructed in the same way
            order0 = orders[0]
            self.assertIn('links', order0)



class OrderTestCase (ResourcesAPITestCase):
    
    #ATTENTION: json.loads return unicode
    url = '/forum/api/orderid/order-1/'
    url_wrong = '/forum/api/orderid/order-500/'

    def test_url(self):
        '''
        Checks that the URL points to the right resource
        '''
        #NOTE: self.shortDescription() shuould work.
        print '('+self.test_url.__name__+')', self.test_url.__doc__
        with resources.app.test_request_context(self.url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.Order)

    def test_wrong_url(self):
        '''
        Checks that GET Order return correct status code if given a
        wrong order
        '''
        resp = self.client.get(self.url_wrong)
        self.assertEquals(resp.status_code, 404)
    

    def test_get_order(self):
        '''
        Checks that GET Order return correct status code and data format
        '''
        print '('+self.test_get_order.__name__+')', self.test_get_order.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url)
            self.assertEquals(resp.status_code, 200)
            data = json.loads(resp.data)
            #The data is formed by links and order

            links = data['_links']

            #Check that the link format is correct
            self.assertEquals(len(links), 5)
            curies = links['curies']
            self.assertEquals(curies[0]['title'], 'order')

            #Check that the order contains all required attributes
            for attribute in ('nickname', 'timestamp', 'sportname'):
                self.assertIn(attribute, data)

            #Check that the user format is correct
            collection = links['collection']
            for attribute in ('href', 'profile', 'type'):
                self.assertIn(attribute, collection)

            #Check that we provide the correct user
            self.assertEquals(resources.api.url_for(resources.User,
                                                    nickname=data['nickname']),
                              '/forum/api/users/' + data['nickname'] + '/')
 
    def test_delete_order(self):
        '''
        Checks that Delete Order return correct status code if corrected delete
        '''
        print '('+self.test_delete_order.__name__+')', self.test_delete_order.__doc__
        resp = self.client.delete(self.url)
        self.assertEquals(resp.status_code, 204)
        resp2 = self.client.get(self.url)
        self.assertEquals(resp2.status_code, 404)


    def test_delete_unexisting_order(self):
        '''
        Checks that Delete Order return correct status code if given a wrong address
        '''
        print '('+self.test_delete_unexisting_order.__name__+')', self.test_delete_unexisting_order.__doc__
        resp = self.client.delete(self.url_wrong)
        self.assertEquals(resp.status_code, 404)

class BookSportTestCase(ResourcesAPITestCase):

    url = '/forum/api/booksport/chen/run/'
    url_wrong = '/forum/api/booksport/chen/sleep/'
    order_1 = {"nickname":"chen",
                 "sport_name": "run"}
    order_1_wrong = {u"nickname":u"CSS: chen",
                                        u"sport_name":u"sleeping"}

    def test_add_order(self):
        '''
        Add a new order and check that I receive the same data
        '''
        print '('+self.test_add_order.__name__+')', self.test_add_order.__doc__
        resp = self.client.post(self.url,
                                data=json.dumps(self.order_1),
                                headers={"Content-Type": "application/vnd.collection+json"})
        self.assertEquals(resp.status_code, 201)
        self.assertIn('Location', resp.headers)
        order_url = resp.headers['Location']
        #Check that the order is stored
        resp2 = self.client.get(order_url)
        self.assertEquals(resp2.status_code, 200)

    def test_add_wrong_order(self):
        '''
        Try to add a reply to an order sending wrong data
        '''
        print '('+self.test_add_wrong_order.__name__+')', self.test_add_wrong_order.__doc__
        resp = self.client.post(self.url_wrong,
                                data=json.dumps(self.order_1_wrong),
                                headers={"Content-Type": "application/vnd.collection+json"})
        self.assertEquals(resp.status_code, 500)


class SportsTestCase (ResourcesAPITestCase):

    url = '/forum/api/sports/'

    def test_url(self):
        '''
        Checks that the URL points to the right resource
        '''
        #NOTE: self.shortDescription() shuould work.
        print '('+self.test_url.__name__+')', self.test_url.__doc__,

        with resources.app.test_request_context(self.url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.Sports)

    def test_get_sports(self):
        '''
        Checks that GET Orders return correct status code and data format
        '''
        print '('+self.test_get_sports.__name__+')', self.test_get_sports.__doc__

        with resources.app.test_client() as client:
            resp = client.get(self.url)
            self.assertEquals(resp.status_code, 200)
            data = json.loads(resp.data)
            link = data['collection']['links']
            self.assertEquals(link[0]['title'], 'List of all sports in the sporthall')
            self.assertEquals(link[0]['rel'], 'sports-all')
            self.assertEquals(link[0]['href'],
                              resources.api.url_for(resources.Sports))
            sport = data['collection']['items'][0]['data']
            #Just check one sport the rest are constructed in the same way
            sport0 = sport[0]
            self.assertIn('name', sport0)


class SportTestCase (ResourcesAPITestCase):
    
    #ATTENTION: json.loads return unicode
    url = '/forum/api/sports/run/'
    url_wrong = '/forum/api/sports/sleep/'

    def test_url(self):
        '''
        Checks that the URL points to the right resource
        '''
        #NOTE: self.shortDescription() shuould work.
        print '('+self.test_url.__name__+')', self.test_url.__doc__
        with resources.app.test_request_context(self.url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.Sport)

    def test_wrong_url(self):
        '''
        Checks that GET Order return correct status code if given a
        wrong sport
        '''
        resp = self.client.get(self.url_wrong)
        self.assertEquals(resp.status_code, 404)


    def test_get_sport(self):
        '''
        Checks that GET Sport return correct status code and data format
        '''
        print '('+self.test_get_sport.__name__+')', self.test_get_sport.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url)
            self.assertEquals(resp.status_code, 200)
            data = json.loads(resp.data)
            #The data is formed by links and sport

            links = data['_links']

            #Check that the link format is correct
            self.assertEquals(len(links), 4)
            curies = links['curies']
            self.assertEquals(curies[0]['name'], 'sport')

            #Check that the sport contains all required attributes
            for attribute in ('time', 'sportname'):
                self.assertIn(attribute, data)

 
    def test_delete_sport(self):
        '''
        Checks that Delete Sport return correct status code if corrected delete
        '''
        print '('+self.test_delete_sport.__name__+')', self.test_delete_sport.__doc__
        resp = self.client.delete(self.url)
        self.assertEquals(resp.status_code, 204)
        resp2 = self.client.get(self.url)
        self.assertEquals(resp2.status_code, 404)


    def test_delete_unexisting_sport(self):
        '''
        Checks that Delete Order return correct status code if given a wrong address
        '''
        print '('+self.test_delete_unexisting_sport.__name__+')', self.test_delete_unexisting_sport.__doc__
        resp = self.client.delete(self.url_wrong)
        self.assertEquals(resp.status_code, 404)


class UsersTestCase (ResourcesAPITestCase):

    url = '/forum/api/users/'

    def test_url(self):
        '''
        Checks that the URL points to the right resource
        '''
        #NOTE: self.shortDescription() shuould work.
        print '('+self.test_url.__name__+')', self.test_url.__doc__,
        with resources.app.test_request_context(self.url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.Users)


    def test_get_users(self):
        '''
        Checks that GET users return correct status code and data format
        '''
        print '('+self.test_get_users.__name__+')', self.test_get_users.__doc__
        #I use this because I need the app context to use the api.url_for
        with resources.app.test_client() as client:
            resp = client.get(self.url)
            self.assertEquals(resp.status_code, 200)
            data = json.loads(resp.data)
            link = data['collection']['links']
            self.assertEquals(link[0]['title'], 'List of all users')
            self.assertEquals(link[0]['rel'], 'users-all')
            self.assertEquals(link[0]['href'], resources.api.url_for(resources.Users))

class UserTestCase (ResourcesAPITestCase):
    user1 = 'chen'
    user2 = 'Jacobino'
    url1 = '/forum/api/users/%s/'% user1
    url2 = '/forum/api/users/%s/'% user2
    url_wrong = '/forum/api/users/unknown/'

    user = {'public_profile': {'nickname':'Jacobino','password':'201','regDate':'213','signature': 'New signature', 'avatar': 'new_avatar.jpg','userType':'True'},'restricted_profile': {'firstname': 'Jake', 'lastname': 'Sully','email': 'sully@rda.com','website': 'http: //www.pandora.com/', 'gender': 'Male'}}

    def test_url(self):
        '''
        Checks that the URL points to the right resource
        '''
        #NOTE: self.shortDescription() shuould work.
        print '('+self.test_url.__name__+')', self.test_url.__doc__
        with resources.app.test_request_context(self.url1):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.User)

    def test_wrong_url(self):
        '''
        Checks that GET Message return correct status code if given a wrong message
        '''
        print '('+self.test_wrong_url.__name__+')', self.test_wrong_url.__doc__
        resp = self.client.get(self.url_wrong)
        self.assertEquals(resp.status_code, 404)


    def test_get_format(self):
        '''
        Checks that the format of user is correct

        '''
        print '('+self.test_get_format.__name__+')', self.test_get_format.__doc__
        #TO be authorized the I must include the header Authorization with name of the user or admin
        resp = self.client.get(self.url1)
        data = json.loads(resp.data)
        self.assertIn('items', data['collection'])



if __name__ == '__main__':
    print 'Start running tests'
    unittest.main()
