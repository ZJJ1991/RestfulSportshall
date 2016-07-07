'''
Created on 26.01.2013
Modified on 24.02.2016
@author: ivan
'''
import unittest, copy
import json

import flask

import forum.resources as resources
import forum.database as database

DB_PATH = 'db/forum_test.db'
ENGINE = database.Engine(DB_PATH)

COLLECTIONJSON = "application/vnd.collection+json"
HAL = "application/hal+json"
FORUM_USER_PROFILE ="/profiles/user-profile"
FORUM_MESSAGE_PROFILE = "/profiles/message-profile"
ATOM_THREAD_PROFILE = "https://tools.ietf.org/html/rfc4685"

#Tell Flask that I am running it in testing mode.
resources.app.config['TESTING'] = True
#Necessary for correct translation in url_for
resources.app.config['SERVER_NAME'] = 'localhost:5000'

#Database Engine utilized in our testing
resources.app.config.update({'Engine': ENGINE})

#Other database parameters.
initial_messages = 20
initial_users = 5


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
        #Activate app_context for using url_for
        self.app_context = resources.app.app_context()
        self.app_context.push()
        #Create a test client
        self.client = resources.app.test_client()

    def tearDown(self):
        '''
        Remove all records from database
        '''
        ENGINE.clear()
        self.app_context.pop()



class UsersTestCase (ResourcesAPITestCase):

    user_1_request = {"template":{
        "data":[
            {"required": "true", "prompt": "Insert user nickname", "name": "nickname", "value": "test 1"},
            {"required": "true", "prompt": "Insert user password", "name": "password", "value": "123"},
            {"required": "true", "prompt": "Insert user regDate", "name": "regDate", "value": "1990-02-12"},
            {"required": "false", "prompt": "Insert user address", "name": "address", "value": "146"},
            {"required": "false", "prompt": "Insert user signature", "name": "signature", "value": "I'm the tester 1"},
            {"required": "true", "prompt": "Insert user avatar", "name": "avatar", "value": "aad"},
            {"required": "true", "prompt": "Insert user userType", "name": "userType", "value": "False"},
            {"required": "true", "prompt": "Insert user birthday", "name": "birthday", "value": "24315"},
            {"required": "true", "prompt": "Insert user email", "name": "email", "value": "asdas@asd.com"},
            {"required": "true", "prompt": "Insert user website", "name": "website", "value": "www.baidu.com"},  
            {"required": "true", "prompt": "Insert user familyName", "name": "familyName", "value": "Wang"},
            {"required": "true", "prompt": "Insert user gender", "name": "gender", "value": "male"},
            {"required": "true", "prompt": "Insert user givenName", "name": "givenName", "value": "Jiebao"}
        ]}
    }

    user_2_request = {"template":{
        "data":[
            {"required": "true", "prompt": "Insert user nickname", "name": "nickname", "value": "tester 2"},
            {"required": "true", "prompt": "Insert user password", "name": "password", "value": "234"},
            {"required": "true", "prompt": "Insert user regDate", "name": "regDate", "value": "1981-2-2"},
            {"required": "false", "prompt": "Insert user address", "name": "address", "value": "1d2"},
            {"required": "false", "prompt": "Insert user signature", "name": "signature", "value": "zadfgf"},
            {"required": "true", "prompt": "Insert user avatar", "name": "avatar", "value": "aas"},
            {"required": "true", "prompt": "Insert user userType", "name": "userType", "value": "False"},
            {"required": "true", "prompt": "Insert user birthday", "name": "birthday", "value": "2315"},
            {"required": "true", "prompt": "Insert user email", "name": "email", "value": "sa"},
            {"required": "true", "prompt": "Insert user website", "name": "website", "value": "ww.asdas.com"},  
            {"required": "true", "prompt": "Insert user familyName", "name": "familyName", "value": "asdmalesa"},
            {"required": "true", "prompt": "Insert user gender", "name": "gender", "value": "male"},
            {"required": "true", "prompt": "Insert user givenName", "name": "givenName", "value": "xiao"}
        ]}
    }

    #Existing nickname
    user_wrong_1_request =  {"template": {
        "data": [
            {"name": "nickname", "value": "AxelW"},
            {"name": "avatar", "value": "image3.jpg"},
            {"name": "birthday", "value": "2009-09-09"},
            {"name": "email", "value": "rango@gmail.com"},
            {"name": "familyName", "value": "Rango"},
            {"name": "gender", "value": "Male"},
            {"name": "givenName", "value": "Rangero"},
            {"name": "signature", "value": "I am like Ronald McDonald"},
        ]}
    }

    #Mssing nickname
    user_wrong_2_request =  {"template": {
        "data": [
            {"name": "avatar", "value": "image3.jpg"},
            {"name": "birthday", "value": "2009-09-09"},
            {"name": "email", "value": "rango@gmail.com"},
            {"name": "familyName", "value": "Rango"},
            {"name": "gender", "value": "Male"},
            {"name": "givenName", "value": "Rangero"},
            {"name": "signature", "value": "I am like Ronald McDonald"},
        ]}
    }

    #Missing mandatory
    user_wrong_3_request = {"template": {
        "data": [
            {"name": "nickname", "value": "Rango"},
            {"name": "email", "value": "rango@gmail.com"},
            {"name": "familyName", "value": "Rango"},
            {"name": "gender", "value": "Male"},
            {"name": "givenName", "value": "Rangero"},
            {"name": "signature", "value": "I am like Ronald McDonald"},
        ]}
    }

    #Wrong address
    user_wrong_4_request = {"template": {
        "data": [
            {"name": "nickname", "value": "Rango"},
            {"name": "avatar", "value": "image3.jpg"},
            {"name": "address", "value": "Indonesia, Spain"},
            {"name": "birthday", "value": "2009-09-09"},
            {"name": "email", "value": "rango@gmail.com"},
            {"name": "familyName", "value": "Rango"},
            {"name": "gender", "value": "Male"},
            {"name": "givenName", "value": "Rangero"},
            {"name": "signature", "value": "I am like Ronald McDonald"},
        ]}
    }

    def setUp(self):
        super(UsersTestCase, self).setUp()
        self.url = resources.api.url_for(resources.Users,
                                         _external=False)

    def test_url(self):
        '''
        Checks that the URL points to the right resource
        '''
        #NOTE: self.shortDescription() shuould work.
        _url = '/forum/api/users/'
        print '('+self.test_url.__name__+')', self.test_url.__doc__,
        with resources.app.test_request_context(_url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.Users)

    def test_get_users(self):
        '''
        Checks that GET users return correct status code and data format
        '''
        print '('+self.test_get_users.__name__+')', self.test_get_users.__doc__
        #Check that I receive status code 200
        resp = self.client.get(flask.url_for('users'))
        self.assertEquals(resp.status_code, 200)

        # Check that I receive a collection and adequate href
        data = json.loads(resp.data)['collection']
        self.assertEquals(resources.api.url_for(resources.Users,
                                                _external=False),
                          data['href'])

        #Check that template is correct
        template_data = data['template']['data']
        self.assertEquals(len(template_data), 13)
        for t_data in template_data:
            self.assertIn(('required' and 'prompt' and 'name'),
                          t_data)
            self.assertTrue(any(k in t_data for k in ('value', 'object')))
            self.assertIn(t_data['name'], ('nickname', 'address',
                                           'avatar', 'birthday',
                                           'email', 'familyName',
                                           'gender', 'givenName',
                                           'image', 'signature',
                                           'skype', 'telephone',
                                           'website'))


        #Check that items are correct.
        items = data['items']
        self.assertEquals(len(items), initial_users)
        for item in items:
            #self.assertIn(flask.url_for('users', _external=False),
             #             item['href'])
            #self.assertIn('links', item)
            self.assertEquals(2, len(item['data']))
            for attribute in item['data']:
                self.assertIn(attribute['name'], ('nickname', 'address'))

    def test_get_users_mimetype(self):
        '''
        Checks that GET Messages return correct status code and data format
        '''
        print '('+self.test_get_users_mimetype.__name__+')', self.test_get_users_mimetype.__doc__

        #Check that I receive status code 200
        resp = self.client.get(self.url)
        self.assertEquals(resp.status_code, 200)
        self.assertEquals(resp.headers.get('Content-Type',None),
                          COLLECTIONJSON+";"+FORUM_USER_PROFILE)

    def test_add_user(self):
        '''
        Checks that the user is added correctly

        '''
        print '('+self.test_add_user.__name__+')', self.test_add_user.__doc__

        # With a complete request
        resp = self.client.post(resources.api.url_for(resources.Users),
                                headers={'Content-Type': COLLECTIONJSON},
                                data=json.dumps(self.user_1_request)
                               )
        self.assertEquals(resp.status_code, 201)
        self.assertIn('Location', resp.headers)
        url = resp.headers['Location']
        resp2 = self.client.get(url)
        self.assertEquals(resp2.status_code, 200)

        #With just mandaaory parameters
        resp = self.client.post(resources.api.url_for(resources.Users),
                                headers={'Content-Type': COLLECTIONJSON},
                                data=json.dumps(self.user_2_request)
                               )
        self.assertEquals(resp.status_code, 201)
        self.assertIn('Location', resp.headers)
        url = resp.headers['Location']
        resp2 = self.client.get(url)
        self.assertEquals(resp2.status_code, 200)

    def test_add_user_missing_mandatory(self):
        '''
        Test that it returns error when is missing a mandatory data
        '''
        print '('+self.test_add_user_missing_mandatory.__name__+')', self.test_add_user_missing_mandatory.__doc__

        # Removing nickname
        resp = self.client.post(resources.api.url_for(resources.Users),
                                headers={'Content-Type': COLLECTIONJSON},
                                data=json.dumps(self.user_wrong_2_request)
                               )
        self.assertEquals(resp.status_code, 400)

        #Removing avatar
        resp = self.client.post(resources.api.url_for(resources.Users),
                                headers={'Content-Type': COLLECTIONJSON},
                                data=json.dumps(self.user_wrong_3_request)
                               )
        self.assertEquals(resp.status_code, 400)

    def test_add_existing_user(self):
        '''
        Testign that trying to add an existing user will fail

        '''
        print '('+self.test_add_existing_user.__name__+')', self.test_add_existing_user.__doc__
        resp = self.client.post(resources.api.url_for(resources.Users),
                                headers={'Content-Type': COLLECTIONJSON},
                                data=json.dumps(self.user_wrong_1_request)
                               )
        self.assertEquals(resp.status_code, 409)

    def test_add_bad_formmatted(self):
        '''
        Test that it returns error when address is bad formatted
        '''
        print '('+self.test_add_bad_formmatted.__name__+')', self.test_add_bad_formmatted.__doc__

        # Removing nickname
        resp = self.client.post(resources.api.url_for(resources.Users),
                                headers={'Content-Type': COLLECTIONJSON},
                                data=json.dumps(self.user_wrong_4_request)
                               )
        self.assertEquals(resp.status_code, 400)

    def test_wrong_type(self):
        '''
        Test that return adequate error if sent incorrect mime type
        '''
        print '('+self.test_wrong_type.__name__+')', self.test_wrong_type.__doc__
        resp = self.client.post(resources.api.url_for(resources.Users),
                                headers={'Content-Type': "application/json"},
                                data=json.dumps(self.user_1_request)
                               )
        self.assertEquals(resp.status_code, 415)

class UserTestCase (ResourcesAPITestCase):

    def setUp(self):
        super(UserTestCase, self).setUp()
        user1_nickname = 'AxelW'
        user2_nickname = 'Jacobino'
        self.url1 = resources.api.url_for(resources.User,
                                          nickname=user1_nickname,
                                          _external=False)
        self.url_wrong = resources.api.url_for(resources.User,
                                               nickname=user2_nickname,
                                               _external=False)
    def test_url(self):
        '''
        Checks that the URL points to the right resource
        '''
        #NOTE: self.shortDescription() shuould work.
        print '('+self.test_url.__name__+')', self.test_url.__doc__
        url = "/forum/api/users/AxelW/"
        with resources.app.test_request_context(url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.User)

    def test_wrong_url(self):
        '''
        Checks that GET Message return correct status code if asking for an
        unexisting user.
        '''
        print '('+self.test_wrong_url.__name__+')', self.test_wrong_url.__doc__
        resp = self.client.get(self.url_wrong)
        self.assertEquals(resp.status_code, 404)

    def test_right_url(self):
        '''
        Checks that GET Message return correct status code if asking for an
        existing user.
        '''
        print '('+self.test_right_url.__name__+')', self.test_right_url.__doc__
        resp = self.client.get(self.url1)
        self.assertEquals(resp.status_code, 200)

    def test_get_user_mimetype(self):
        '''
        Checks that GET Messages return correct status code and data format
        '''
        print '('+self.test_get_user_mimetype.__name__+')', self.test_get_user_mimetype.__doc__

        #Check that I receive status code 200
        resp = self.client.get(self.url1)
        self.assertEquals(resp.status_code, 200)
        self.assertEquals(resp.headers.get('Content-Type',None),
                          HAL+";"+FORUM_USER_PROFILE)

    def test_get_format(self):
        '''
        Checks that the format of user is correct

        '''
        print '('+self.test_get_format.__name__+')', self.test_get_format.__doc__
        resp = self.client.get(self.url1)
        self.assertEquals(resp.status_code, 200)
        data = json.loads(resp.data)

        attributes = ('nickname', 'registrationdate', '_links')
        self.assertEquals(len(data), 3)
        for data_attribute in data:
            self.assertIn(data_attribute, attributes)

        links = data["_links"]
        links_attributes = ("user:messages", "user:public-data",
                            "user:restricted-data", "curies", "self",
                            "collection", "delete")

        for links_attribute in links:
            self.assertIn(links_attribute, links_attributes)

        link_attributes = ("href", "profile", "type")
        for link_name, link in links.items():
            if link_name == "curies":
                continue
            else:
                for link_attribute in link:
                    self.assertIn(link_attribute, link_attributes)
                    if link_name == 'self' or link_name == 'delete':
                        self.assertEquals(link['href'], self.url1)
                        self.assertEquals(link['profile'], FORUM_USER_PROFILE)
                    elif link_name == 'user:messages':
                        self.assertEquals(link['href'],
                                            resources.api.url_for(
                                                resources.History,
                                                nickname='AxelW',
                                                _external=False))
                        self.assertEquals(link['profile'], FORUM_MESSAGE_PROFILE)
                        self.assertEquals(link['type'], COLLECTIONJSON)
                    elif link_name == "user:public-data":
                        self.assertEquals(link['href'],
                                            resources.api.url_for(
                                                resources.User_public,
                                                nickname='AxelW',
                                                _external=False))
                        self.assertEquals(link['profile'], FORUM_USER_PROFILE)
                        self.assertEquals(link['type'], HAL)
                    elif link_name == "user:restricted-data":
                        self.assertEquals(link['href'],
                                            resources.api.url_for(
                                                resources.User_restricted,
                                                nickname='AxelW',
                                                _external=False))
                        self.assertEquals(link['profile'], FORUM_USER_PROFILE)
                        self.assertEquals(link['type'], HAL)
                    elif link_name == "collection":
                        self.assertEquals(link['href'],
                                          resources.api.url_for(resources.Users, _external=False))
                        self.assertEquals(link['profile'], FORUM_USER_PROFILE)
                        self.assertEquals(link['type'], COLLECTIONJSON)

    def test_delete_user(self):
        '''
        Checks that Delete user return correct status code if corrected delete
        '''
        print '('+self.test_delete_user.__name__+')', self.test_delete_user.__doc__
        resp = self.client.delete(self.url1)
        self.assertEquals(resp.status_code, 204)
        resp2 = self.client.get(self.url1)
        self.assertEquals(resp2.status_code, 404)

    def test_delete_unexisting_user(self):
        '''
        Checks that Delete user return correct status code if given a wrong address
        '''
        print '('+self.test_delete_unexisting_user.__name__+')', self.test_delete_unexisting_user.__doc__
        resp = self.client.delete(self.url_wrong)
        self.assertEquals(resp.status_code, 404)

class HistoryTestCase (ResourcesAPITestCase):


    def setUp(self):
        super(HistoryTestCase, self).setUp()
        self.url1= resources.api.url_for(resources.History, nickname='AxelW',
                                         _external=False)
        self.messages1_number = 2
        self.url2= resources.api.url_for(resources.History, nickname='Mystery',
                                         _external=False)
        self.messages2_number = 2
        self.url3 = self.url1+'?length=1'
        self.messages3_number = 1
        self.url4 = self.url1+'?after=1362317481'
        self.messages4_number = 1
        self.url5 = self.url1+'?before=1362317481'
        self.messages5_number = 1
        self.url6 = self.url1+'?before=1362317481&after=1362217481'
        self.url_wrong= resources.api.url_for(resources.History, nickname='WRONG',
                                         _external=False)


    def test_url(self):
        '''
        Checks that the URL points to the right resource
        '''
        #NOTE: self.shortDescription() shuould work.
        print '('+self.test_url.__name__+')', self.test_url.__doc__,
        url = '/forum/api/users/AxelW/history/'
        with resources.app.test_request_context(url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.History)

    def test_get_history_mimetype(self):
        '''
        Checks that GET Messages return correct status code and data format
        '''
        print '('+self.test_get_history_mimetype.__name__+')', self.test_get_history_mimetype.__doc__

        #Check that I receive status code 200
        resp = self.client.get(self.url1)
        self.assertEquals(resp.status_code, 200)
        self.assertEquals(resp.headers.get('Content-Type',None),
                          COLLECTIONJSON+";"+FORUM_MESSAGE_PROFILE)

    def test_get_history_number_values(self):
        '''
        Checks that GET history return correct status code and number of values
        '''
        print '('+self.test_get_history_number_values.__name__+')', self.test_get_history_number_values.__doc__
        #I use this because I need the app context to use the api.url_for
        with resources.app.test_client() as client:
            resp = client.get(self.url1)
            self.assertEquals(resp.status_code, 200)
            data = json.loads(resp.data)['collection']
            self.assertIn('items', data)
            messages = data['items']
            self.assertEquals(len(messages), self.messages1_number)

            resp = client.get(self.url2)
            self.assertEquals(resp.status_code, 200)
            data = json.loads(resp.data)['collection']
            self.assertIn('items', data)
            messages = data['items']
            self.assertEquals(len(messages), self.messages2_number)

            resp = client.get(self.url3)
            self.assertEquals(resp.status_code, 200)
            data = json.loads(resp.data)['collection']
            self.assertIn('items', data)
            messages = data['items']
            self.assertEquals(len(messages), self.messages3_number)


    def test_get_history_timestamp_values(self):
        '''
        Checks that GET history return correct status code and format
        '''
        print '('+self.test_get_history_timestamp_values.__name__+')', self.test_get_history_timestamp_values.__doc__
        #I use this because I need the app context to use the api.url_for
        with resources.app.test_client() as client:
            resp = client.get(self.url4)
            self.assertEquals(resp.status_code, 200)
            data = json.loads(resp.data)['collection']
            self.assertIn('items', data)
            messages = data['items']
            self.assertEquals(len(messages), self.messages4_number)

            resp = client.get(self.url5)
            data = json.loads(resp.data)['collection']
            self.assertIn('items', data)
            messages = data['items']
            self.assertEquals(len(messages), self.messages5_number)

            resp = client.get(self.url6)
            self.assertEquals(resp.status_code, 404)

    def test_get_history_unknown_user(self):
        '''
        Checks that the system returns 404 when tryign to find history for unknown
        user.
        '''
        print '('+self.test_get_history_unknown_user.__name__+')', self.test_get_history_unknown_user.__doc__
        resp = self.client.get(self.url_wrong)
        self.assertEquals(resp.status_code, 404)

    def test_get_history(self):
        '''
        Checks that GET history return correct status code and number of values
        '''
        print '('+self.test_get_history.__name__+')', self.test_get_history.__doc__
        #I use this because I need the app context to use the api.url_for
        with resources.app.test_client() as client:
            resp = client.get(self.url1)
            self.assertEquals(resp.status_code, 200)
            data = json.loads(resp.data)['collection']
            collection_attributes = ('href', 'items', 'version', 'links', 'queries')
            self.assertEquals(len(data), 5)
            for collection_attribute in data:
                self.assertIn(collection_attribute, collection_attributes)


if __name__ == '__main__':
    print 'Start running tests'
    unittest.main()
