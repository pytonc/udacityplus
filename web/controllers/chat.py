from web.controllers.BaseHandler import BaseHandler
from web.models.ChatUser import ChatUser
from web.util import chat
import logging
import json
import re
import os


class Chat(BaseHandler):
    def get(self, room):

        self.response.out.write(self.render_template("chat/main.html", channel=room))

    def post(self):
        '''Displays chat UI'''
        username = self.username

        channelname = self.request.get('channel')
        usernameerror = ""
        if not username:
            usernameerror="Please enter a username"
        elif not re.compile(r'^[a-zA-Z0-9_-]{3,20}$').match(username):
            usernameerror = "Username must consist of 3-20 alphanumeric characters."
        elif chat.get_user(username):
            usernameerror="Username already in use"
        channelerror = ""
        if channelname and not re.compile(r'^#[\w]{3,20}$').match(channelname):
            channelerror="Channel must consist of 3-20 alpha_numeric characters and start with a #"
        if len(usernameerror+channelerror) > 0:
            self.response.out.write(self.render_template("main.html",
                username=username,
                usernameerror=usernameerror,
                channel=channelname,
                channelerror=channelerror))
        else:
            token = chat.channel_api.create_channel(username) # Expires after 120 minutes
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
            self.response.out.write(self.render_template("chat.html", token=token,
                username=username,
                identifier=identifier,
                server="!AwesomeServer"))