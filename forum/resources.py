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
import logging

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
        Check if the connection is created. It migth be exception appear before`
        the connection is created.'''
    if hasattr(g, 'con'):
        g.con.close()

#Define the resources
class Orders(Resource):
    '''
    Resource Orders implementation
    '''
    def get(self, nickname=None):

        #Extract Orders from database
        orders_db = g.con.get_orders(nickname)

        #Create the envelope
        envelope = {}
        collection = {}
        envelope["collection"] = collection
        collection['version'] = "1.0"
        '''collection['href'] = api.url_for(Orders)'''
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
                 "value": "", "required": False},
                {"prompt": "", "name": "sport_name",
                 "value": "", "required": True},
                {"prompt": "", "name": "timestamp",
                 "value": "", "required": True} 
            ]
        }
        #Create the items
        items = []
        for order in orders_db:
            _orderid = order['order_id']
            _usernickname = order['nickname']
            _sportname = order['sportname']
            _timestamp = order['timestamp']
            _url = api.url_for(Order, orderid=_orderid)
            order = {}
            order['href'] = _url
            order['data'] = []
            value = {'name':'order_id', 'value': _orderid}
            order['data'].append(value)
            value = {'name':'user_nickname', 'value': _usernickname}
            order['data'].append(value)

            value = {'name':'sportname', 'value': _sportname}
            order['data'].append(value)
            value = {'name':'timestamp', 'value': _timestamp}
            order['data'].append(value)
            order['links'] = []
            items.append(order)
        collection['items'] = items
        print envelope
        #RENDER
        return Response(json.dumps(envelope), 200,
                        mimetype=COLLECTIONJSON+";")



class AllOrders(Resource):
    '''
    Resource Orders implementation
    '''
    def get(self):

        #Extract Orders from database
        orders_db = g.con.get_orders(None)

        #Create the envelope
        envelope = {}
        collection = {}
        envelope["collection"] = collection
        collection['version'] = "1.0"
        '''collection['href'] = api.url_for(Orders)'''
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
                 "value": "", "required": False},
                {"prompt": "", "name": "sport_name",
                 "value": "", "required": True},
                {"prompt": "", "name": "timestamp",
                 "value": "", "required": True} 
            ]
        }
        #Create the items
        items = []
        for order in orders_db:
            _orderid = order['order_id']
            _usernickname = order['nickname']
            _sportname = order['sportname']
            _timestamp = order['timestamp']
            _url = api.url_for(Order, orderid=_orderid)
            order = {}
            order['href'] = _url
            order['data'] = []
            value = {'name':'order_id', 'value': _orderid}
            order['data'].append(value)
            value = {'name':'user_nickname', 'value': _usernickname}
            order['data'].append(value)

            value = {'name':'sportname', 'value': _sportname}
            order['data'].append(value)
            value = {'name':'timestamp', 'value': _timestamp}
            order['data'].append(value)
            order['links'] = []
            items.append(order)
        collection['items'] = items
        print envelope
        #RENDER
        return Response(json.dumps(envelope), 200,
                        mimetype=COLLECTIONJSON+";")
		
		
		
		
class BookSport(Resource):
    def post(self, nickname, sportname):


        #Extract the request body. In general would be request.data
        #Since the request is JSON I use request.get_json
        #get_json returns a python dictionary after serializing the request body
        #get_json returns None if the body of the request is not formatted
        # using JSON. We use force=True since the input media type is not
        # application/json.

        if COLLECTIONJSON != request.headers.get('Content-Type',''):
            return create_error_response(415, "UnsupportedMediaType",
                                         "Use a JSON compatible format")


        neworderid = g.con.create_order(nickname, sportname)
        if not neworderid:
            return create_error_response(500, "Problem with the database",
                                         "Cannot access the database")

        #Create the Location header with the id of the order created
        url = api.url_for(Order, orderid=neworderid)

        #RENDER
        #Return the response
        return Response(status=201, headers={'Location': url})




class Order(Resource):

    def get(self, orderid):
        
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
                 "value": "", "required": False},
                {"prompt": "Insert hallnumber", "name": "hallnumber",
                 "value": "", "required": True},
                {"prompt": "Insert note", "name": "note",
                 "value": "", "required": False}
            ]
        }
        #Create the items
        items = []
        for sport in sports_db:
            print sport
            _sportid = sport['sport_id']
            _sportname = sport['sportname']
            #print _sportname
            _time = sport['time']
            #print _time
            _hallnumber = sport['hallnumber']
            _note = sport['note']
            #_url = api.url_for(Sport, sportname=_sportname)
            sport = {}
            #sport['href'] = _url
            sport['read-only'] = True
            sport['data'] = []
            value = {'name': 'sport_id', 'value': _sportid}
            sport['data'].append(value)
            value = {'name': 'sportname', 'value': _sportname}
            sport['data'].append(value)
            value = {'name': 'time', 'value': _time}
            sport['data'].append(value)
            value = {'name': 'hallnumber', 'value': _hallnumber}
            sport['data'].append(value)
            value = {'name': 'note', 'value': _note}
            sport['data'].append(value)
            items.append(sport)
        collection['items'] = items
        #RENDER
        return Response(json.dumps(envelope), 200,
                        mimetype=COLLECTIONJSON+";"+FORUM_USER_PROFILE)



    def post(self):
       
       
        '''
        if COLLECTIONJSON != request.headers.get('Content-Type', ''):
            return create_error_response(415, "UnsupportedMediaType",
                                         "Use a JSON compatible format asd")
		'''
        request_body = request.get_json(force=True)
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
            elif d['name'] == "hallnumber":
                _hallnumber = d['value']
            elif d['name'] == "note":
                _note = d['value']
        print _sportname
        sport = {'sportname' : _sportname,
                 'time' : _time,
                 'hallnumber' : _hallnumber,
                 'note' : _note
                }
        print sport
        try:
            sportname = g.con.append_sport(_sportname, sport)
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
                                                 sportname=_sportname)})
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
        print sport_db
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
                "templated": True
            }
        ]
        links['curies'] = _curies
        links['self'] = {'href': api.url_for(Sport, sportname=sportname),
                         }
        links['collection'] = {'href': api.url_for(Sports),
                               'type': COLLECTIONJSON}
        links['sport:delete'] = {
            'href': api.url_for(Sport, sportname=sportname),
        }
        envelope['sportname'] = sportname
        envelope['time'] = sport_db['sport time']

        #RENDER
        return Response(json.dumps(envelope), 200,
                        mimetype=HAL+";")

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
            print _nickname
            _registrationdate = user['regDate']
            print _registrationdate
            _lastlogin = user['lastLogin']
            print _lastlogin
            _timesviewed = user['timesviewed']
            print _timesviewed
            '''
            _registrationdate = user['regDate']
            _lastlogin = user['lastLogin']
            _timesviewed = user['timesviewed']
            '''
            #_url = api.url_for(User, nickname= _nickname)
            user = {}
            #user['href'] = _url
            user['read-only'] = True
            user['data'] = []
            value = {'name': 'nickname', 'value': _nickname}
            user['data'].append(value)
            #value = {'name': 'lastLogin', 'value': _lastlogin}
            #user['data'].append(value)
            #value = {'name': 'timesviewed', 'value': _timesviewed}
            #user['data'].append(value)
            '''
            value = {'name': 'regDate', 'value': _registrationdate}
            user['data'].append(value)
            value = {'name': 'lastLogin', 'value': _lastlogin}
            user['data'].append(value)
            value = {'name': 'timesviewed', 'value': _timesviewed}
            user['data'].append(value)
            '''
            value = {'name': 'regDate', 'value': _registrationdate}
            user['data'].append(value)
            items.append(user)
        collection['items'] = items
        #RENDER

        return Response(json.dumps(envelope), 200,
                        mimetype=COLLECTIONJSON+";"+FORUM_USER_PROFILE)

    def post(self):
        print COLLECTIONJSON
        print request.headers.get('Content-Type','')
        if COLLECTIONJSON != request.headers.get('Content-Type', ''):
            return create_error_response(415, "UnsupportedMediaType",
                                         "Use a JSON compatible format saaszxc")
        print "verify request 1"
        #PARSE THE REQUEST:
        input = request.get_json(force=True)
        print input
        if not request.get_json(force=True):
            return create_error_response(415, "Unsupported Media Type",
                                         "Use a JSON compatible format",
                                         "User")
        #Get the request body and serialize it to object 
        #We should check that the format of the request body is correct. Check
        #That mandatory attributes are there.
    
        data = input['template']['data']
        _nickname = None
        _password = None
        _regDate = None
        _lastLogin = None
        _timeviewed = None
        _address = None
        _signature = None
        _avatar = None
        _birthday = None
        _email = None
        _website = None
        _familyName = None
        _gender = None
        _givenName = None

        for d in data:
        #This code has a bad performance. We write it like this for
        #simplicity. Another alternative should be used instead. E.g. 
        #generation expressions
            if d['name'] == "nickname":
                _nickname = d['value']
                print _nickname
            if d['name'] == "password":
                _password = d['value']
                print _password
            if d['name'] == "regDate":
                _regDate = d['value']
                print _regDate
            elif d['name'] == "address":
                _address = d['value']
                print _address
            elif d['name'] == "signature":
                _signature = d['value']
                print _signature
            elif d['name'] == "avatar":
                _avatar = d['value']
                print _avatar
            elif d['name'] == "birthday":
                _birthday = d['value']
                print _birthday
            elif d['name'] == "email":
                _email = d['value']
                print _email
            elif d['name'] == "website":
                _website = d['value']
                print _website
            elif d['name'] == "familyName":
                _familyName = d['value']
                print _familyName
            elif d['name'] == "gender":
                _gender = d['value']
                print _gender
            elif d['name'] == "givenName":
                _givenName = d['value']
                print _givenName
        #Error if not required value
      
        #Conflict if user already exist
        
        if g.con.contains_user(_nickname):
            return create_error_response(400, "Wrong nickname",
                                              "There is already a user with same username %s.\
                                               Try another one " % _nickname)
        
        user =  {'public_profile':{
                  'password': _password,
                  'regDate': _regDate,
                  'signature': _signature,
                  'avatar': _avatar},
                  'restricted_profile':{'firstname': _givenName,
                  'lastname': _familyName,
                  'email':_email,
                  'website': _website,
                  'birthday': _birthday,
                  'gender': _gender}
        }
        print user
        #But we are not going to do this exercise
        username = g.con.append_user(_nickname, user)

        #CREATE RESPONSE AND RENDER
        return  Response(status=201, 
                         headers={"Location":api.url_for(User, nickname=_nickname)}
                        )



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
        print user_db
        public_profile = user_db['public_profile']
        print public_profile
        restricted_profile = user_db['restricted_profile']
        print restricted_profile
        collection = {}
        envelope['collection'] = collection
        items = []
        #_url = api.url_for(User, nickname= _nickname)
        profile = {}
        profile['data'] = []
        value = {'name': 'nickname', 'value': public_profile['nickname']}
        print value
        profile['data'].append(value)
        value = {'name': 'registrationdate', 'value': public_profile['regDate']}
        profile['data'].append(value)
        value = {'name': 'signature', 'value': public_profile['signature']}
        profile['data'].append(value)
        
        print profile
        items.append(profile)
        collection['items'] = items   
        #RENDER
        return Response(json.dumps(envelope), 200,
                        mimetype=HAL+";"+FORUM_USER_PROFILE)

						
						
class deleteUser(Resource):
    def delete(self, nickname, password):
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
        if g.con.delete_user(nickname, password):
            #RENDER RESPONSE
            return '', 200
        else:
            #GENERATE ERROR RESPONSE
            return create_error_response(404, "Unknown user",
                                         "There is no user with nickname %s"
                                         % nickname)




class Login(Resource):

    def get(self, nickname, password):
        data = g.con.login(nickname, password)
        if data:
            userType = data['userType'] 
            if  userType == "True":
			    return "Admin", 200
            else:
                return "Normal", 200
        else:
            return create_error_response(404, "Wrong info",
                                         "The username and password do not match"
                                         )

class File(Resource):

	def get(self, text):
		file = open("D:/DS_project/Node_1/forum_admin/static/data.txt", "w")
		file.writelines(text)
		file.close()
		return 'successfully login', 200
		
		
		
#Add the Regex Converter so we can use regex expressions when we define the
#routes
app.url_map.converters['regex'] = RegexConverter


#Define the routes

api.add_resource(Orders, '/forum/api/orders/<nickname>/',
                 endpoint='orders')
api.add_resource(AllOrders, '/forum/api/orders/',
                 endpoint='allorders')
api.add_resource(BookSport, '/forum/api/booksport/<nickname>/<sportname>/',
                 endpoint='booksport')
api.add_resource(Order, '/forum/api/orders/<regex("order-\d+"):orderid>/',
                 endpoint='order')
api.add_resource(Users, '/forum/api/users/',
                 endpoint='users')
api.add_resource(User, '/forum/api/users/<nickname>/',
                 endpoint='user')
api.add_resource(deleteUser, '/forum/api/deleteuser/<nickname>/<password>/',
                 endpoint='deleteuser')
api.add_resource(Login, '/forum/api/login/<nickname>/<password>/',
                 endpoint='login')
api.add_resource(Sports, '/forum/api/sports/',
                 endpoint='sports')
api.add_resource(Sport, '/forum/api/sports/<sportname>/',
                 endpoint='sport') 
api.add_resource(File, '/forum/api/files/<text>/',
                 endpoint='file') 


#Redirect profile
@app.route('/profiles/<profile_name>')
def redirect_to_profile(profile_name):
    return redirect(APIARY_PROFILES_URL + profile_name)


#Start the application
#DATABASE SHOULD HAVE BEEN POPULATED PREVIOUSLY
if __name__ == '__main__':
    #Debug true activates automatic code reloading and improved error messages
    app.run(debug=True)