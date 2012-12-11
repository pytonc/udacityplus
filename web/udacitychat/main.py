import os
import hashlib
import urllib
import logging
import re
import json

import webapp2
import jinja2
from google.appengine.api import channel as channel_api # 'channel' is kind of ambiguous in context
from google.appengine.ext import  ndb
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

class ChatUser(ndb.Model):
    '''A user'''
    # key_name is username.lower()
    username = ndb.StringProperty(required = True) # case SeNsItIvE
    joined = ndb.DateTimeProperty(auto_now_add = True)
    identifier = ndb.StringProperty(required = True) # Session specific
    startingchannel = ndb.TextProperty(required = False)
    channels = ndb.TextProperty(required = True) # JSON array
    contacts = ndb.TextProperty(required = True) # JSON array
    connected = ndb.BooleanProperty(default = False)
    def store(self):
        '''Store in memcache and datastore'''
        memcache.set(user_key(self.key.id()), self)
        self.put()
    def get_contact_names(self):
        '''Get the usernames of this user's contacts'''
        # Remove nonexistent contacts
##        contactnames = json.loads(self.contacts)
##        changed = False
##        for contactname in contactnames:
##            contact = get_user(contactname)
##            if not contact:
##                contactnames = [c for c in contactnames if c != contactname]
##                changed = True
##        if changed:
##            self.contacts = json.dumps(contactnames)
##            self.store()
##        return contactnames
        return json.loads(self.contacts)
    def add_contact(self, contactname):
        '''Add a username to this user's contacts'''
        contacts = json.loads(self.contacts)
        if contactname not in contacts:
            contacts.append(contactname)
            self.contacts = json.dumps(contacts)
            self.store()
    def remove_contact(self, contactname):
        '''Remove a username from this user's contacts'''
        contacts = json.loads(self.contacts)
        if contactname in contacts:
            contacts.remove(contactname) # Should only ever be one contactname
            self.contacts = json.dumps(contacts)
            self.store()
    def get_channel_names(self):
        '''Returns a list of the names of all channels this user is in'''
        return json.loads(self.channels)
    def add_channel(self, channelname):
        '''Adds a channel to this user's channel list'''
        logging.info("user: %s joined channel %s"%(self.username, channelname))
        channels = json.loads(self.channels)
        if channelname not in channels:
            channels.append(channelname)
            self.channels = json.dumps(channels)
            self.store()
    def remove_channel(self, channelname):
        '''Removes a channel from this user's channel list'''
        channels = json.loads(self.channels)
        if channelname in channels:
            channels.remove(channelname)
            self.channels = json.dumps(channels)
            self.store()

class ChatChannel(ndb.Model):
    '''A chat channel'''
    # key_name is channelname.lower()
    channelname = ndb.StringProperty(required = True) # case SeNsItIvE
    created = ndb.DateTimeProperty(auto_now_add = True)
    users = ndb.TextProperty(required = False) # JSON array
    def store(self):
        '''Store in memcache and datastore'''
        memcache.set(channel_key(self.key.id()), self)
        self.put()
    def get_user_names(self):
        '''Returns a list of all the users in this channel'''
        return json.loads(self.users)
    def add_user(self, username):
        '''Adds a username to this channel's user list'''
        users = json.loads(self.users)
        if username not in users:
            users.append(username)
            self.users = json.dumps(users)
            self.store()
    def remove_user(self, username):
        '''Removes a username from this channel's user list'''
        users = json.loads(self.users)
        if username in users:
            users.remove(username)
            self.users = json.dumps(users)
            self.store()

class Communication(webapp2.RequestHandler):
    '''Deals with chat traffic'''
    def post(self):
        # Client MUST ENFORCE correct syntax for commands, and ensure usernames and channelnames exist
        # Perhaps that's a dangerous statement?
        message = urllib.unquote(self.request.get('message'))
        username = urllib.unquote(self.request.get('username'))
        identifier = urllib.unquote(self.request.get('identifier'))
        logging.info("Username: "+username+" Message: "+message)
        if not (message and username and identifier): 
            return
        user = get_user(username)
        if not user or (user and identifier != user.identifier):
            return
        COMMANDS = {"JOIN": user_join,
                    "LEAVE": user_leave,
                    "PRIVMSG": user_privmsg,
                    "CHANNELMSG": user_channelmsg,
                    "QUIT": user_quit,
                    "PING": user_ping,
                    "PONG": user_pong
                    }
        command = message.split(' ')[0].upper()
        arg = '' if ' ' not in message else message[message.index(' ')+1:]
        if command in COMMANDS:
            COMMANDS[command](username, arg)
        else:
            channel_api.send_message(username, "NOTICE Command not supported by server: "+message) # Echo, for testing

def user_join(username, channelname):
    user = get_user(username)
    username = user.username # Use actual name
    channel = get_channel(channelname)
    if not channel:        
        if channelname and not re.compile(r'^#[\w]{3,20}$').match(channelname):
            channelerror="Channel must consist of 3-20 alpha_numeric characters and start with a #"
            channel_api.send_message(username, "NOTICE "+channelerror)
            return
        channel = ChatChannel(key_name=channelname.lower(),
                              channelname=channelname,
                              users=json.dumps([ ])
                              )
    channelname = channel.channelname # Use actual name
    channel.add_user(username)
    user.add_channel(channelname)
    userlist = ' '.join(channel.get_user_names())
    channel_api.send_message(username, "USERS "+channelname+" "+userlist) # Tell the user who is in the channel
    for u in channel.get_user_names():
        # Tell the individual channel members that the new user joined
        channel_api.send_message(u, "JOINED "+username+" "+channelname)
    logging.warning("End of JOIN, %s's channels are: "%username+', '.join(get_user(username).get_channel_names()))

def user_leave(username, channelname):
    user = get_user(username)
    username = user.username # Use actual name
    channel = get_channel(channelname)
    channelname = channel.channelname # Use actual name
    channel.remove_user(username)
    # Do we inform the user they have successfully left?
    # If we do, then that may cause a closed tab to reopen, better for client to handle that
    for u in channel.get_user_names():
        channel_api.send_message(u, "LEFT "+username+" "+channelname)

def user_quit(username, args):
    '''User has quit'''
    # This may take a while to execute
    user = get_user(username)
    username = user.username # Use actual name
    user.connected = False
    for channelname in user.get_channel_names():
        # Remove the user from channel
        channel = get_channel(channelname)
        channel.remove_user(username) # Do this first to prevent infinite loops
        for u in channel.get_user_names():
            # Let the people in the channel know
            channel_api.send_message(u, "QUIT "+username+" "+channelname)
    for contactname in user.get_contact_names():
        # Remove user from their contacts' contact lists
        # Possible double-handling, but that's ok because remove_contact checks for that
        contact = get_user(contactname)
        if contact:
            contact.remove_contact(username)
    try:
        channel_api.send_message(username, "NOTICE You have quit")
    except:
        # POKEMON exception!
        # Not really needed since send_message does not throw exceptions
        pass
    user.store()
    # Let the disconnect handler deal with clearing the user object

def user_privmsg(username, args):
    '''Private message from one user to another'''
    recipientname = args.split(' ')[0]
    message = args[args.index(' ')+1:]
    recipient = get_user(recipientname)
    user = get_user(username)
    username = user.username # Use actual name
    if recipient and user:
        recipientname = recipient.username # Use actual name
        channel_api.send_message(recipientname, "PRIVMSG "+username+" "+message)
        channel_api.send_message(username, "SENTMSG "+recipientname+" "+message)
        # Add sender and recipient to each other's contact lists to inform of e.g. quittage
        recipient.add_contact(username)
        user.add_contact(recipientname)
    else:
        channel_api.send_message(username, "NOTICE "+recipientname+" is not a valid user. Maybe they disconnected "+
                                 "or maybe you need to check your spelling")

def user_channelmsg(username, args):
    channelname = args.split(' ')[0]
    message = args[args.index(' ')+1:]
    channel = get_channel(channelname)
    user = get_user(username)
    username = user.username # Use actual name
    channelname = channel.channelname # Use actual name
    if channel and username in channel.get_user_names():
        for u in channel.get_user_names():
            # Send message to all the users in the channel
            channel_api.send_message(u, "CHANNELMSG "+channelname+" "+username+" "+message)
    else:
        channel_api.send_message(username, "NOTICE "+channelname+" does not appear to be a channel "+
                                 "(or it is a channel, and you're not in it, somehow).")

def user_ping(username, args):
    user = get_user(username)
    username = user.username # Use actual name
    channel_api.send_message(username, "PONG "+args)

def user_pong(username, args):
    # Do nothing, since we have not yet implemented PING/PONG
    pass

class Connect(webapp2.RequestHandler):
    def post(self):
        # Not everything causes a proper disconnect
        username = self.request.get('from')
        user = get_user(username)
        if user and user.startingchannel:
            user_join(username, user.startingchannel) # Join default channel
        user = get_user(username) # To prevent overwriting
        user.connected = True
        user.store()
        logging.info("Connected: "+username)
        logging.warning("End of CONNECT, %s's channels are: "%username+', '.join(get_user(username).get_channel_names()))

class Disconnect(webapp2.RequestHandler):
    def post(self):
        # Have to propagate to all the channels the user was in
        username = self.request.get("from")
        user = get_user(username)
        if user.connected:
            user_quit(username, "")
        clear_user(username)
        logging.info("Disconnected: "+username)
        
class TokenexpireHandler(webapp2.RequestHandler):
    def post(self):
        ##handle token expire
        username = urllib.unquote(self.request.get('username'))
        token = channel_api.create_channel(username)
        logging.info("this is a new token. :"+token)
        self.response.out.write(token)
        
def user_key(username):
    '''user_key function is for key consistency'''
    return "user/"+username.lower()

def get_user(username):
    '''Get a user from memcache or datastore, returns None if user does not exist'''
    key = user_key(username)
    user = memcache.get(key)
    if not user:
        user = ChatUser.get_by_id(username.lower())
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
        channel = ChatChannel.get_by_id(channelname.lower())
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
        self.response.out.write(render("main.html", channel="#udacity"))

    def post(self):
        '''Displays chat UI'''
        username = self.request.get('username')
        channelname = self.request.get('channel')
        usernameerror = ""
        if not username:
            usernameerror="Please enter a username"
        elif not re.compile(r'^[a-zA-Z0-9_-]{3,20}$').match(username):
            usernameerror = "Username must consist of 3-20 alphanumeric characters."
        elif get_user(username):
            usernameerror="Username already in use"
        channelerror = ""
        if channelname and not re.compile(r'^#[\w]{3,20}$').match(channelname):
            channelerror="Channel must consist of 3-20 alpha_numeric characters and start with a #"
        if len(usernameerror+channelerror) > 0:
            self.response.out.write(render("main.html",
                                           username=username,
                                           usernameerror=usernameerror,
                                           channel=channelname,
                                           channelerror=channelerror))
        else:
            token = channel_api.create_channel(username) # Expires after 120 minutes
            logging.info("%s is a token. type of token: %s"%(token,type(token)))
            identifier = os.urandom(16).encode('hex')
            user = ChatUser(id=username.lower(),
                            username=username,
                            identifier=identifier,
                            startingchannel=channelname,
                            connected=True,
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
                               ('/_ah/channel/disconnected/?', Disconnect),
                               ('/tokenexpireHandler',TokenexpireHandler)
                               ], debug=True)
