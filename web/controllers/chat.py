from boilerplate.lib.basehandler import user_required

__author__ = "rrandom, Jin Koo, Anthony, Jan Zegan"

from google.appengine.api import channel as channel_api
from web.controllers.BaseHandler import BaseHandler
from webapp2_extras.i18n import gettext as _
from web.models.ChatUser import ChatUser
from web.models.Course import Course
from web.models.User import User
from web.util import chat
import webapp2
import logging
import urllib
import json
import re
import os


class Chat(BaseHandler):
    def get(self, **kwargs):
        return self.redirect(self.uri_for('home'))

#    @user_required/
    def post(self, channelname):
        '''Displays chat UI'''
        username = self.username

#        if chat.get_user(username):
#            message = _("Username already in use")
#            self.add_message(message, 'error')
#            return self.redirect(self.request.url)

        if channelname not in Course.available_course_ids():
            #TODO: doesn't return info
            message = _("Channel not available")
            self.add_message(message, 'info')
            return self.redirect(self.request.url)

        channelname = "#{}".format(channelname)

        token = chat.channel_api.create_channel(username) # Expires after 120 minutes
        logging.info("%s is a token. type of token: %s"%(token,type(token)))
        identifier = os.urandom(16).encode('hex')
        user = ChatUser(user=User.get_by_id(self.user_id),
            id=username,
            username=username,
            identifier=identifier,
            startingchannel=channelname,
            connected=True,
            contacts=json.dumps([ ]),
            channels=json.dumps([ ]))
        user.store()
        self.response.out.write(self.render_template("chat/chat.html", token=token,
            username=username,
            identifier=identifier,
            server="!AwesomeServer",
            room=channelname))

class Connect(webapp2.RequestHandler):
    def post(self):
        # Not everything causes a proper disconnect
        username = self.request.get('from')
        user = chat.get_user(username)
        if user and user.startingchannel:
            chat.user_join(username, user.startingchannel) # Join default channel
        user = chat.get_user(username) # To prevent overwriting
        user.connected = True
        user.store()
        logging.info("Connected: "+username)
        logging.warning("End of CONNECT, %s's channels are: "%username+', '.join(chat.get_user(username).get_channel_names()))

class Disconnect(webapp2.RequestHandler):
    def post(self):
        # Have to propagate to all the channels the user was in
        username = self.request.get("from")
        user = chat.get_user(username)
        if user.connected:
            chat.user_quit(username, "")
        chat.clear_user(username)
        logging.info("Disconnected: "+username)

class TokenexpireHandler(webapp2.RequestHandler):
    def post(self):
        ##handle token expire
        username = urllib.unquote(self.request.get('username'))
        token = channel_api.create_channel(username)
        logging.info("this is a new token. :"+token)
        self.response.out.write(token)

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
        user = chat.get_user(username)
        if not user or (user and identifier != user.identifier):
            return
        COMMANDS = {"JOIN": chat.user_join,
                    "LEAVE": chat.user_leave,
                    "PRIVMSG": chat.user_privmsg,
                    "CHANNELMSG": chat.user_channelmsg,
                    "QUIT": chat.user_quit,
                    "PING": chat.user_ping,
                    "PONG": chat.user_pong
        }
        command = message.split(' ')[0].upper()
        arg = '' if ' ' not in message else message[message.index(' ')+1:]
        if command in COMMANDS:
            COMMANDS[command](username, arg)
        else:
            channel_api.send_message(username, "NOTICE Command not supported by server: "+message) # Echo, for testing