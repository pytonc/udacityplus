__author__ = "Anthony, Jan Zegan"

import urllib
import logging
import webapp2
from google.appengine.api import channel as channel_api # 'channel' is kind of ambiguous in context
from web.util import chat

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