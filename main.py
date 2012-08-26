import os
import hashlib
import urllib
import logging

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
    # username is the key
    joined = db.DateTimeProperty(auto_now_add = True)
    connected = db.BooleanProperty(required = True)
    identifier = db.StringProperty(required = True) # Session specific

class ChatChannel(db.Model):
    '''A chat channel'''

    pass

class Communication(webapp2.RequestHandler):
    '''Deals with chat traffic'''
    def post(self):
        # How do we authenticate that the message is coming from the user?
        # Send each user a key when rendering the page which they use in all communication
        message = urllib.unquote(self.request.get('message'))
        username = urllib.unquote(self.request.get('username'))
        identifier = urllib.unquote(self.request.get('identifier'))
        if not (message and username and identifier): 
            return
        channel.send_message(username, "NOTICE Server got this message from you: "+message) # Echo, for testing

class Connect(webapp2.RequestHandler):
    def post(self):
        client_id = self.request.get('from')

class Disconnect(webapp2.RequestHandler):
    def post(self):
        client_id = self.request.get('from')

class Main(webapp2.RequestHandler):
    def get(self):
        '''Show connection page'''
        self.response.out.write(render("main.html"))

    def post(self):
        '''Displays chat UI'''
        username = self.request.get('username')
        if not username:
            self.response.out.write(render("main.html"))
        else:
            channel_name = self.request.get('channel')
            token = channel.create_channel(username) # Expires after 120 minutes
            identifier = os.urandom(16).encode('hex')
            self.response.out.write(render("chat.html", token=token,
                                           username=username,
                                           identifier=identifier,
                                           server="!AwesomeServer"))            

app = webapp2.WSGIApplication([
                               ('/', Main),
                               ('/communication', Communication),
                               ('/_ah/channel/connected', Connect),
                               ('/_ah/channel/disconnected', Disconnect)
                               ], debug=True)