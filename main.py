import os
import hashlib
import urllib
import logging
import re
import json

import webapp2
import jinja2
from google.appengine.api import channel
from google.appengine.ext import db
from google.appengine.api import memcache

# This section will eventually get moved to a Handler class
template_dir = os.path.join(
        os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(
        loader = jinja2.FileSystemLoader(template_dir),
        autoescape = True)

def render_str(template, **params):
    '''Returns a string of the rendered template'''
    t = jinja_env.get_template(template)
    return t.render(params)

def render(template, **kw):
    '''Render using the template and parameters'''
    return(render_str(template, **kw))
# End Handler

class ChatUser(db.Model):
    '''A user'''
    # key_name is username.lower()
    username = db.StringProperty(required = True) # case SeNsItIvE
    joined = db.DateTimeProperty(auto_now_add = True)
    identifier = db.StringProperty(required = True) # Session specific
    channels = db.TextProperty(required = True) # JSON array
    contacts = db.TextProperty(required = True) # JSON array    
    def store(self):
        '''Store in memcache and datastore'''
        memcache.set(user_key(self.key().name()), self)
        self.put()
    def get_contact_names(self):
        return json.loads(self.contacts)
    def add_contact(self, contactname):
        contacts = json.loads(self.contacts)
        contacts.append(contactname)
        self.contacts = json.dumps(contacts)
        self.store()
    def remove_contact(self, contactname):
        contacts = json.loads(self.contacts)
        if contactname in contacts:
            contacts.remove(contactname)
            self.contacts = json.dumps(contacts)
            self.store()
    def get_channel_names(self):
        return json.loads(self.channels)
    def add_channel(self, channelname):
        channels = json.loads(self.channels)
        channels.append(channelname)
        self.channels = json.dumps(channels)
        self.store()
    def remove_channel(self, channelname):
        channels = json.loads(self.channels)
        if channelname in channels:
            channels.remove(channelname)
            self.channels = json.dumps(channels)
            self.store()

class ChatChannel(db.Model):
    '''A chat channel'''
    # key_name is channelname.lower()
    channelname = db.StringProperty(required = True) # case SeNsItIvE
    created = db.DateTimeProperty(auto_now_add = True)
    users = db.TextProperty(required = False) # JSON array
    def store(self):
        '''Store in memcache and datastore'''
        memcache.set(channel_key(self.key().name()), self)
        self.put()
    def get_user_names(self):
        return json.loads(self.users)
    def add_user(self, username):
        users = json.loads(self.users)
        users.append(username)
        self.users = json.dumps(users)
        self.store()
    def remove_user(self, username):
        users = json.loads(self.users)
        if username in users:
            users.remove(username)
            self.users = json.dumps(users)
            self.store()

class Communication(webapp2.RequestHandler):
    '''Deals with chat traffic'''
    def post(self):
        # Client MUST ENFORCE correct syntax for commands 
        message = urllib.unquote(self.request.get('message'))
        username = urllib.unquote(self.request.get('username'))
        identifier = urllib.unquote(self.request.get('identifier'))
        if not (message and username and identifier): 
            return
        user = get_user(username)
        if identifier != user.identifier:
            return
        COMMANDS = {"JOIN": user_join,
                    "LEAVE": user_leave,
                    "PRIVMSG": user_privmsg,
                    "CHANNELMSG": user_channelmsg,
                    "QUIT": user_quit,
                    "PING": user_ping,
                    "PONG": user_pong
                    }
        command = message.split(' ')[0]
        arg = '' if ' ' not in message else message[message.index(' ')+1:]
        if command in COMMANDS:
            COMMANDS[command](username, arg)
        else:
            channel.send_message(username, "NOTICE Command not supported by server: "+message) # Echo, for testing

def user_join(username, channelname):
    pass

def user_leave(username, channelname):
    pass

def user_privmsg(username, args):
    pass

def user_channelmsg(username, args):
    pass

def user_quit(username, args):
    pass

def user_ping(username, args):
    pass

def user_pong(username, args):
    pass

class Connect(webapp2.RequestHandler):
    def post(self):
        client_id = self.request.get('from')
        logging.info("Connected: "+client_id)

class Disconnect(webapp2.RequestHandler):
    def post(self):
        # Have to propagate to all the channels the user was in
        client_id = self.request.get('from')
        logging.info("Disconnected: "+client_id)
        clear_user(client_id)

def user_key(username):
    '''For consistency'''
    return "user/"+username.lower()

def get_user(username):
    '''Get a user from memcache or datastore, returns None if user does not exist'''
    key = user_key(username)
    user = memcache.get(key)
    if not user:
        user = ChatUser.get_by_key_name(username.lower())
        if user:
            memcache.set(key, user)
        else:
            memcache.set(key, "placeholder to reduce memcache misses")
    if isinstance(user, ChatUser):
        return user

def clear_user(username):
    '''Removes a user from datastore and from memcache'''
    user = get_user(username)
    if user:
        user.delete()
        memcache.set(user_key(username), "placeholder to reduce memcache misses")
        logging.info("Removed "+username)

def channel_key(channelname):
    '''For consistency'''
    return "channel/"+channelname.lower()

def get_channel(channelname):
    '''Get a channel from memcache or datastore, returns None if channel does not exist'''
    key = channel_key(channelname)
    channel = memcache.get(key)
    if not channel:
        channel = ChatChannel.get_by_key_name(channelname.lower())
        if channel:
            memcache.set(key, channel)
        else:
            memcache.set(key, "placeholder to reduce memcache misses")
    if isinstance(channel, ChatChannel):
        return channel

def clear_channel(channelname):
    '''Removes a channel from datastore and from memcache'''
    channel = get_channel(channelname)
    if channel:
        channel.delete()
        memcache.set(channel_key(channelname), "placeholder to reduce memcache misses")

class Main(webapp2.RequestHandler):
    def get(self):
        '''Show connection page'''
        self.response.out.write(render("main.html", error=""))

    def post(self):
        '''Displays chat UI'''
        username = self.request.get('username')
        error = ""
        if not username:
            error="Please enter a username"
        elif not re.compile(r'^[a-zA-Z0-9_-]{3,20}$').match(username):
            error = "Username must consist of 3-20 alphanumeric characters."
        elif get_user(username):
            error="Username already in use"
        if len(error) > 0:
            self.response.out.write(render("main.html",
                                           username=username,
                                           error=error))
        else:
            channel_name = self.request.get('channel') # Not like we're doing anything with this, for now
            token = channel.create_channel(username) # Expires after 120 minutes
            identifier = os.urandom(16).encode('hex')
            user = ChatUser(key_name=username.lower(),
                            username=username,
                            identifier=identifier,
                            contacts=json.dumps([ ]),
                            channels=json.dumps([ ]))
            user.store()
            self.response.out.write(render("chat.html", token=token,
                                           username=username,
                                           identifier=identifier,
                                           server="!AwesomeServer"))

app = webapp2.WSGIApplication([
                               ('/', Main),
                               ('/communication', Communication),
                               ('/_ah/channel/connected/?', Connect),
                               ('/_ah/channel/disconnected/?', Disconnect)
                               ], debug=True)