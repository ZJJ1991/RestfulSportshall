'''
Created on 26.01.2013
Modified on 09.03.2016
@author: ivan

@modified: chenhaoyu, zhoujunjie
'''
#TODO: Create another file
import json

from flask import Flask, request, Response, g, jsonify, _request_ctx_stack, redirect
from flask.ext.restful import Resource, Api, abort
from flask.ext.cors import CORS
from werkzeug.exceptions import NotFound,  UnsupportedMediaType

from utils import RegexConverter
import database

#Constants for hypermedia formats and profiles
COLLECTIONJSON = "application/vnd.collection+json"
HAL = "application/hal+json"
FORUM_USER_PROFILE ="/profiles/user-profile"
FORUM_MESSAGE_PROFILE = "/profiles/message-profile"
ATOM_THREAD_PROFILE = "https://tools.ietf.org/html/rfc4685"
APIARY_PROFILES_URL = "http://docs.pwpforumappcomplete.apiary.io/#reference/profiles/"

#Define the application and the api
app = Flask(__name__)
app.debug = True
# Set the database Engine. In order to modify the database file (e.g. for
# testing) provide the database path   app.config to modify the
#database to be used (for instance for testing)
app.config.update({'Engine': database.Engine()})
#Start the RESTful API.
api = Api(app)
#Add support for cors
CORS(app)


#ERROR HANDLERS
#TODO: Modify this accordding
# http://soabits.blogspot.no/2013/05/error-handling-considerations-and-best.html
# I should define a profile for the error.
def create_error_response(status_code, title, message=None):
    ''' Creates a: py: class:`flask.Response` instance when sending back an
      HTTP error response
     : param integer status_code: The HTTP status code of the response
     : param str title: A short description of the problem
     : param message: A long description of the problem
     : rtype:: py: class:`flask.Response`

    '''
    resource_type = None
    resource_url = None
    ctx = _request_ctx_stack.top
    if ctx is not None:
        resource_url = request.path
        resource_type = ctx.url_adapter.match(resource_url)[0]
    response = jsonify(title=title,
                       message=message,
                       resource_url=resource_url,
                       resource_type=resource_type)
    response.status_code = status_code
    return response

@app.errorhandler(404)
def resource_not_found(error):
    return create_error_response(404, "Resource not found",
                                 "This resource url does not exit")

@app.errorhandler(400)
def resource_not_found(error):
    return create_error_response(400, "Malformed input format",
                                 "The format of the input is incorrect")

@app.errorhandler(500)
def unknown_error(error):
    return create_error_response(500, "Error",
                    "The system has failed. Please, contact the administrator")


@app.before_request
def connect_db():
    '''Creates a database connection before the request is proccessed.

    The connection is stored in the application context variable flask.g .
    Hence it is accessible from the request object.'''

    g.con = app.config['Engine'].connect()


#HOOKS
@app.teardown_request
def close_connection(exc):
    ''' Closes the database connection
        Check if the connection is created. It migth be exception appear before
        the connection is created.'''
    if hasattr(g, 'con'):
        g.con.close()

#Define the resources
class Orders(Resource):
    '''
    Resource Orders implementation
    '''
    def get(self):
        '''
        Get all orders.

        INPUT parameters:
          None

        RESPONSE ENTITY BODY:
        * Media type: Collection+JSON:
             http://amundsen.com/media-types/collection/
           - Extensions: template validation and value-types
             https://github.com/collection-json/extensions
         * Profile: Forum_order
           http://atlassian.virtues.fi: 8090/display/PWP
           /Exercise+4#Exercise4-Forum_order

        Link relations used in items: None
        Semantic descriptions used in items: headline
        Link relations used in links: users-all
        Semantic descriptors used in template: order_id, timestamp, user_nickname,
        sport_id.

        NOTE:
         * The attribute order_id is obtained from the column Orders.order_id
         * The attribute user_nickname is obtained from the column Orders.user_nickname
         * The attribute sport_id is obtained from the column Orders.sport_id
        '''
        #Extract Orders from database
        orders_db = g.con.get_orders()

        #Create the envelope
        envelope = {}
        collection = {}
        envelope["collection"] = collection
        collection['version'] = "1.0"
        collection['href'] = api.url_for(Orders)
        collection['links'] = [
                                {'prompt': 'List of all users in the Forum',
                                'rel': 'users-all', 'href': api.url_for(Users)
                                }
            ]
        collection['template'] = {
            "data": [
                {"prompt": "", "name": "order_id",
                 "value": "", "required": True},
                {"prompt": "", "name": "timestamp",
                 "value": "", "required": True},
                {"prompt": "", "name": "user_nickname",
                 "value": "", "required": False},
                {"prompt": "", "name": "sport_id",
                 "value": "", "required": False}
            ]
        }
        #Create the items
        items = []
        for order in orders_db:
            _orderid = order['orderid']
            _timestamp = order['timestamp']
            _url = api.url_for(Order, orderid=_orderid)
            order = {}
            order['href'] = _url
            order['data'] = []
            value = {'name':'timestamp', 'value': _timestamp}
            order['data'].append(value)
            order['links'] = []
            items.append(order)
        collection['items'] = items

        #RENDER
        return Response(json.dumps(envelope), 200,
                        mimetype=COLLECTIONJSON+";"+FORUM_ORDER_PROFILE)

    def post(self):
        '''
        Adds a a new order.

        REQUEST ENTITY BODY:
         * Media type: Collection+JSON:
             http://amundsen.com/media-types/collection/
           - Extensions: template validation and value-types
             https://github.com/collection-json/extensions
         * Profile: Forum_Message
           http://atlassian.virtues.fi: 8090/display/PWP
           /Exercise+4#Exercise4-Forum_Order

        
        The body should be a Collection+JSON template.
        Semantic descriptors used in template: nickname and sport_id.

        RESPONSE STATUS CODE:
         * Returns 201 if the order has been added correctly.
           The Location header contains the path of the new order
         * Returns 400 if the order is not well formed.
         * Returns 415 if the format of the response is not json
         * Returns 500 if the order could not be added to database.

        '''

        #Extract the request body. In general would be request.data
        #Since the request is JSON I use request.get_json
        #get_json returns a python dictionary after serializing the request body
        #get_json returns None if the body of the request is not formatted
        # using JSON. We use force=True since the input media type is not
        # application/json.

        if COLLECTIONJSON != request.headers.get('Content-Type',''):
            return create_error_response(415, "UnsupportedMediaType",
                                         "Use a JSON compatible format")
        request_body = request.get_json(force=True)
         #It throws a BadRequest exception, and hence a 400 code if the JSON is
        #not wellformed
        try:
            data = request_body['template']['data']
            title = None
            body = None
            sender = "Anonymous"
            ipaddress = request.remote_addr

            for d in data:
                #This code has a bad performance. We write it like this for
                #simplicity. Another alternative should be used instead.
                if d['name'] == 'nickname':
                    nickname = d['value']
                elif d['name'] == 'sport_id':
                    sport_id = d['value']

            #CHECK THAT DATA RECEIVED IS CORRECT
            if not nickname or not sport_id:
                return create_error_response(400, "Wrong request format",
                                             "Be sure you include nickname and sport_id")
        except:
            #This is launched if either nickname or sport_id does not exist or if
            # the template.data array does not exist.
            return create_error_response(400, "Wrong request format",
                                         "Be sure you include nickname and sport_id")
        #Create the new order and build the response code'
        neworderid = g.con.create_order(nickname, sport_id)
        if not neworderid:
            return create_error_response(500, "Problem with the database",
                                         "Cannot access the database")

        #Create the Location header with the id of the order created
        url = api.url_for(Order, orderid=neworderid)

        #RENDER
        #Return the response
        return Response(status=201, headers={'Location': url})

class Order(Resource):
    '''
    Resource that represents a single order in the API.
    '''

    def get(self, orderid):
        '''
        Get the order_id, timestamp, user_nickname, 
		sport_id of a specific order.
        Returns status code 404 if the orderid does not exist in the database.

        INPUT PARAMETER
       : param str orderid: The id of the order to be retrieved from the
            system

        RESPONSE ENTITY BODY:
         * Media type: application/hal+json:
             http://stateless.co/hal_specification.html
         * Profile: Forum_Order
           http://atlassian.virtues.fi: 8090/display/PWP
           /Exercise+4#Exercise4-Forum_Order

            Link relations used: 

            Semantic descriptors used: order_id, timestamp, user_nickname,
        sport_id
            NOTE: editor should not be included in the output if the database
            return None.

        RESPONSE STATUS CODE
         * Return status code 200 if everything OK.
         * Return status code 404 if the order was not found in the database.

        NOTE:
         * The attribute order_id is obtained from the column Orders.order_id
         * The attribute user_nickname is obtained from the column Orders.user_nickname
         * The attribute sport_id is obtained from the column Orders.sport_id
        '''

        #PEFORM OPERATIONS INITIAL CHECKS
        #Get the order from db
        order_db = g.con.get_order(orderid)
        if not order_db:
            return create_error_response(404, "Order does not exist",
                        "There is no a order with id %s" % orderid)

        #FILTER AND GENERATE RESPONSE
        #Create the envelope:
        envelope = {}
        #Now create the links
        links = {}
        envelope["_links"] = links

        #Fill the links
        _curies = [
            {
                "name": "order",
                "href": FORUM_ORDER_PROFILE + "/{rels}",
                "templated": True
            }
        ]
        links['curies'] = _curies
        links['self'] = {'href': api.url_for(Order, orderid=orderid),
                         'profile': FORUM_ORDER_PROFILE}
        links['order:edit'] = {'href': api.url_for(Order, orderid=orderid),
                         'profile': FORUM_ORDER_PROFILE}
        links['order:delete'] = {'href': api.url_for(Order, orderid=orderid),
                         'profile': FORUM_ORDER_PROFILE}

        links['collection'] = {'href': api.url_for(Orders),
                               'profile': FORUM_ORDER_PROFILE,
                               'type': COLLECTIONJSON}
        links['order:reply'] = {'href': api.url_for(Order, orderid=orderid),
                              'profile': FORUM_ORDER_PROFILE}

        #Fill the template
        envelope['template'] = {
            "data": [
                {"prompt": "", "name": "timestamp",
                 "value": "", "required": True},
                {"prompt": "", "name": "nickname",
                 "value": "", "required": True},
                {"prompt": "", "name": "sport_id",
                 "value": "", "required": False},
            ]
        }

        envelope['nickname'] = order_db['nickname']
        envelope['timestamp'] = order_db['timestamp']
        envelope['sport_id'] = order_db['sport_id']

        #RENDER
        return Response(json.dumps(envelope), 200,
                        mimetype=HAL+";"+FORUM_MESSAGE_PROFILE)

    def delete(self, orderid):
        '''
        Deletes an order from the Forum API.

        INPUT PARAMETERS:
       : param str orderid: The id of the order to be deleted

        RESPONSE STATUS CODE
         * Returns 204 if the order was deleted
         * Returns 404 if the orderid is not associated to any order.
        '''

        #PERFORM DELETE OPERATIONS
        if g.con.delete_order(orderid):
            return '', 204
        else:
            #Send error order
            return create_error_response(404, "Unknown order",
                                         "There is no a order with id %s" % orderid
                                        )

class Sports(Resource):

    def get(self):
        '''
        Gets a list of all the sports in the database.

        It returns always status code 200.

        RESPONSE ENTITITY BODY:
        '''
        #PERFORM OPERATIONS
        #Create the messages list
        sports_db = g.con.get_sports()

        #FILTER AND GENERATE THE RESPONSE
       #Create the envelope
        envelope = {}
        collection = {}
        envelope["collection"] = collection
        collection['version'] = "1.0"
        collection['href'] = api.url_for(Sports)
        collection['template'] = {
            "data": [
                {"prompt": "Insert sportname", "name": "sportname",
                 "value": "", "required": True},
                {"prompt": "Insert time", "name": "time",
                 "value": "", "required": False}
            ]
        }
        #Create the items
        items = []
        for sport in sports_db:
            print sport
            _sportname = sport['sportname']
            #print _sportname
            _time = sport['time']
            #print _time

            _url = api.url_for(Sport, sportnamee=_sportname)
            sport = {}
            sport['href'] = _url
            sport['read-only'] = True
            sport['data'] = []
            value = {'sportname': 'sportname', 'value': _sportname}
            sport['data'].append(value)
            value = {'name': 'time', 'value': _time}
            sport['data'].append(value)

            items.append(sport)
        collection['items'] = items
        #RENDER
        return Response(json.dumps(envelope), 200,
                        mimetype=COLLECTIONJSON+";"+FORUM_USER_PROFILE)



    def post(self):
       
        request_body = request.get_json(force=True)

        if COLLECTIONJSON != request.headers.get('Content-Type', ''):
            return create_error_response(415, "UnsupportedMediaType sad",
                                         "Use a JSON compatible format")
        #PARSE THE REQUEST:
        if not request_body:
            return create_error_response(415, "Unsupported Media Type 1",
                                         "Use a JSON compatible format ba",
                                         )
        #Get the request body and serialize it to object
        #We should check that the format of the request body is correct. Check
        #That mandatory attributes are there.

        data = request_body['template']['data']
        _sportname = None
        _time = None


        for d in data:
        #This code has a bad performance. We write it like this for
        #simplicity. Another alternative should be used instead. E.g.
        #generation expressions
            
            if d['name'] == "sportname":
                _sportname = d['value']
            elif d['name'] == "time":
                _time = d['value']
        
        print _sportname
        try:
            sportname = g.con.append_sport(_sportname, _time)
            print "here we have append sport name "
        except ValueError:
            return create_error_response(400, "Wrong request format",
                                         "Be sure you include all"
                                         " mandatory properties"
                                        )

        #CREATE RESPONSE AND RENDER
        if sportname:
            return Response(
                status=201,
                headers={"Location": api.url_for(Sport,
                                                 sportname=sportname)})
        #Already sport in the database
        else:
            return create_error_response(409, "Sport in database",
                                         "sportname: %s already in use" % sportname)

class Sport(Resource):
    '''
    Sport Resource.
    '''

    def get(self, sportname):
        
        #PERFORM OPERATIONS
        sport_db = g.con.get_sport(sportname)
        if not sport_db:
            return create_error_response(404, "Unknown sport",
                                         "There is no a sport with sportname %s"
                                         % sportname)

        #FILTER AND GENERATE RESPONSE
        #Create the envelope:
        envelope = {}
        #Now create the links
        links = {}
        envelope["_links"] = links

        #Fill the links
        _curies = [
            {
                "name": "sport",
                "href": FORUM_SPORT_PROFILE + "/{rels}",
                "templated": True
            }
        ]
        links['curies'] = _curies
        links['self'] = {'href': api.url_for(Sport, sportname=sportname),
                         'profile': FORUM_SPORT_PROFILE}
        links['collection'] = {'href': api.url_for(Sports),
                               'profile': FORUM_SPORT_PROFILE,
                               'type': COLLECTIONJSON}
        links['sport:delete'] = {
            'href': api.url_for(Sport, sportname=sportname),
            'profile': FORUM_SPORT_PROFILE
        }
        envelope['sportname'] = sportname
        envelope['time'] = sport_db['time']

        #RENDER
        return Response(json.dumps(envelope), 200,
                        mimetype=HAL+";"+FORUM_SPORT_PROFILE)

    def delete(self, sportname):
        '''
        Delete a sport in the system.

       : param str sportname: sportname of the required sport.

        RESPONSE STATUS CODE:
         * If the sport is deleted returns 204.
         * If the sportname does not exist return 404
        '''

        #PEROFRM OPERATIONS
        #Try to delete the sport. If it could not be deleted, the database
        #returns None.
        if g.con.delete_sport(sportname):
            #RENDER RESPONSE
            return '', 204
        else:
            #GENERATE ERROR RESPONSE
            return create_error_response(404, "Unknown sport",
                                         "There is no a sport with sportname %s"
                                         % sportname)

										
										
										
class Users(Resource):

    def get(self):
        '''
        Gets a list of all the users in the database.

        It returns always status code 200.

        RESPONSE ENTITITY BODY:
        '''
        #PERFORM OPERATIONS
        #Create the messages list
        users_db = g.con.get_users()

        #FILTER AND GENERATE THE RESPONSE
       #Create the envelope
        envelope = {}
        collection = {}
        envelope["collection"] = collection
        collection['version'] = "1.0"
        collection['href'] = api.url_for(Users)
        collection['template'] = {
            "data": [
                {"prompt": "Insert nickname", "name": "nickname",
                 "value": "", "required": True},
                {"prompt": "Insert user address", "name": "address",
                 "value": "", "required": False},
                {"prompt": "Insert user avatar", "name": "avatar",
                 "value": "", "required": True},
                {"prompt": "Insert user birthday", "name": "birthday",
                 "value": "", "required": True},
                {"prompt": "Insert user email", "name": "email",
                 "value": "", "required": True},
                {"prompt": "Insert user familyName", "name": "familyName",
                 "value": "", "required": True},
                {"prompt": "Insert user gender", "name": "gender",
                 "value": "", "required": True},
                {"prompt": "Insert user givenName", "name": "givenName",
                 "value": "", "required": True},
                {"prompt": "Insert user image", "name": "image",
                 "value": "", "required": False},
                {"prompt": "Insert user signature", "name": "signature",
                 "value": "", "required": True},
                {"prompt": "Insert user skype", "name": "skype",
                 "value": "", "required": False},
                {"prompt": "Insert user telephone", "name": "telephone",
                 "value": "", "required": False},
                {"prompt": "Insert user website", "name": "website",
                 "value": "", "required": False}
            ]
        }
        #Create the items
        items = []
        for user in users_db:
            print user
            _nickname = user['nickname']
            #print _nickname
            _registrationdate = user['registrationdate']
            #print _registrationdate
            _lastlogin = user['lastLogin']
            #print _lastlogin
            _timesviewed = user['timesviewed']
            #print _timesviewed
            '''
            _registrationdate = user['regDate']
            _lastlogin = user['lastLogin']
            _timesviewed = user['timesviewed']
            '''
            _url = api.url_for(User, nickname=_nickname)
            user = {}
            user['href'] = _url
            user['read-only'] = True
            user['data'] = []
            value = {'name': 'nickname', 'value': _nickname}
            user['data'].append(value)
            value = {'name': 'lastLogin', 'value': _lastlogin}
            user['data'].append(value)
            value = {'name': 'timesviewed', 'value': _timesviewed}
            user['data'].append(value)
            '''
            value = {'name': 'regDate', 'value': _registrationdate}
            user['data'].append(value)
            value = {'name': 'lastLogin', 'value': _lastlogin}
            user['data'].append(value)
            value = {'name': 'timesviewed', 'value': _timesviewed}
            user['data'].append(value)
            '''
            value = {'name': 'nickname', 'value': _nickname}
            user['data'].append(value)
            items.append(user)
        collection['items'] = items
        #RENDER
        return Response(json.dumps(envelope), 200,
                        mimetype=COLLECTIONJSON+";"+FORUM_USER_PROFILE)




    def post(self):
       
        request_body = request.get_json(force=True)

        if COLLECTIONJSON != request.headers.get('Content-Type', ''):
            return create_error_response(415, "UnsupportedMediaType sad",
                                         "Use a JSON compatible format")
        #PARSE THE REQUEST:
        if not request_body:
            return create_error_response(415, "Unsupported Media Type 1",
                                         "Use a JSON compatible format ba",
                                         )
        #Get the request body and serialize it to object
        #We should check that the format of the request body is correct. Check
        #That mandatory attributes are there.

        data = request_body['template']['data']
        _nickname = None
        _email = None
        _lastname = None
        _gender = None
        _firstname = None
        _picture = None
        _signature = None
        _skype = None
        _mobile = None
        _website = None

        for d in data:
        #This code has a bad performance. We write it like this for
        #simplicity. Another alternative should be used instead. E.g.
        #generation expressions
            
            if d['name'] == "avatar":
                _avatar = d['value']
            elif d['name'] == "email":
                _email = d['value']
            elif d['name'] == "familyName":
                _lastname = d['value']
            elif d['name'] == "gender":
                _gender = d['value']
            elif d['name'] == "givenName":
                _firstname = d['value']
            elif d['name'] == "image":
                _picture = d['value']
            elif d['name'] == "signature":
                _signature = d['value']
            elif d['name'] == "skype":
                _skype = d['value']
            elif d['name'] == "website":
                _website = d['value']
            elif d['name'] == "nickname":
                _nickname = d['value']
        
        #Conflict if user already exist
        if g.con.contains_user(_nickname):
            return create_error_response(409, "Wrong nickname",
                                         "There is already a user with same"
                                         "nickname:%s." % _nickname)

        user = {'public_profile': {'nickname': _nickname,
                                   'signature': _signature, 'avatar': _avatar},
                'restricted_profile': {'firstname': _firstname,
                                       'lastname': _lastname,
                                       'email': _email,
                                       'website': _website,
                                       'skype': _skype,
                                       'residence': _residence,
                                       'gender': _gender,
                                       'picture': _picture}
        }
        print _nickname
        try:
            nickname = g.con.append_user(_nickname, user)
            print "nihao a"
        except ValueError:
            return create_error_response(400, "Wrong request format",
                                         "Be sure you include all"
                                         " mandatory properties"
                                        )

        #CREATE RESPONSE AND RENDER
        if nickname:
            return Response(
                status=201,
                headers={"Location": api.url_for(User,
                                                 nickname=nickname)})
        #User in the database
        else:
            return create_error_response(409, "User in database",
                                         "nickname: %s already in use" % nickname)

class User(Resource):
    '''
    User Resource. Public and private profile are separate resources.
    '''

    def get(self, nickname):
        
        #PERFORM OPERATIONS
        user_db = g.con.get_user(nickname)
        if not user_db:
            return create_error_response(404, "Unknown user",
                                         "There is no a user with nickname %s"
                                         % nickname)

        #FILTER AND GENERATE RESPONSE
        #Create the envelope:
        envelope = {}
        #Now create the links
        links = {}
        envelope["_links"] = links

        #Fill the links
        _curies = [
            {
                "name": "user",
                "href": FORUM_USER_PROFILE + "/{rels}",
                "templated": True
            }
        ]
        links['curies'] = _curies
        links['self'] = {'href': api.url_for(User, nickname=nickname),
                         'profile': FORUM_USER_PROFILE}
        links['collection'] = {'href': api.url_for(Users),
                               'profile': FORUM_USER_PROFILE,
                               'type': COLLECTIONJSON}
        links['user:messages'] = {
            'href': api.url_for(History, nickname=nickname),
            'profile': FORUM_MESSAGE_PROFILE,
            'type': COLLECTIONJSON}
        links['user:public-data'] = {
            'href': api.url_for(User_public, nickname=nickname),
            'profile': FORUM_USER_PROFILE,
            'type': HAL}
        links['user:restricted-data'] = {
            'href': api.url_for(User_restricted, nickname=nickname),
            'profile': FORUM_USER_PROFILE,
            'type': HAL}
        links['user:delete'] = {
            'href': api.url_for(User, nickname=nickname),
            'profile': FORUM_USER_PROFILE
        }
        envelope['nickname'] = nickname
        envelope['registrationdate'] = user_db['public_profile']['registrationdate']

        #RENDER
        return Response(json.dumps(envelope), 200,
                        mimetype=HAL+";"+FORUM_USER_PROFILE)

    def delete(self, nickname):
        '''
        Delete a user in the system.

       : param str nickname: nickname of the required user.

        RESPONSE STATUS CODE:
         * If the user is deleted returns 204.
         * If the nickname does not exist return 404
        '''

        #PEROFRM OPERATIONS
        #Try to delete the user. If it could not be deleted, the database
        #returns None.
        if g.con.delete_user(nickname):
            #RENDER RESPONSE
            return '', 204
        else:
            #GENERATE ERROR RESPONSE
            return create_error_response(404, "Unknown user",
                                         "There is no a user with nickname %s"
                                         % nickname)
										 
#Add the Regex Converter so we can use regex expressions when we define the
#routes
app.url_map.converters['regex'] = RegexConverter


#Define the routes

api.add_resource(Orders, '/forum/api/orders/',
                 endpoint='orders')
api.add_resource(Order, '/forum/api/orders/<regex("order-\d+"):orderid>/',
                 endpoint='order')
api.add_resource(User_public, '/forum/api/users/<nickname>/public_profile/',
                 endpoint='public_profile')
api.add_resource(User_restricted, '/forum/api/users/<nickname>/restricted_profile/',
                 endpoint='restricted_profile')
api.add_resource(Users, '/forum/api/users/',
                 endpoint='users')
api.add_resource(User, '/forum/api/users/<nickname>/',
                 endpoint='user')
api.add_resource(Sports, '/forum/api/sports/',
                 endpoint='sports')
api.add_resource(Sport, '/forum/api/sports/'\d+':sportid>/',
                 endpoint='sport')				 



#Redirect profile
@app.route('/profiles/<profile_name>')
def redirect_to_profile(profile_name):
    return redirect(APIARY_PROFILES_URL + profile_name)


#Start the application
#DATABASE SHOULD HAVE BEEN POPULATED PREVIOUSLY
if __name__ == '__main__':
    #Debug true activates automatic code reloading and improved error messages
    app.run(debug=True)