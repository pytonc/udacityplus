# Display specific message if message id is given in the 
# url, otherwise get show param and display inbox, outbox 
# or render form for a new message.
#
# If start and end params are given, in inbox/outbox show 
# messages from start to end sorted by creation time DESC
# else use default values defined in model (and temp.js)
from BaseHandler import *
from helpers.authentication import Authentication
from models.User import User
from models.Message import Message, Conversation
from google.appengine.ext import ndb
import re


class MessagePage(BaseHandler):
    
    @Authentication.do
    def get(self):
        (conv_id, msg_id)   = re.search(r"/messages(/?)([0-9]*)(/?)([0-9]*)", self.request.url).group(2, 4)

        username = self.get_cookie("username")
        show, start, end, thread, id = self.get_params(["show", "from", "to", "thread", "id"])

        me = User.get_user(username)
        friends = me.get_friends()

        if msg_id:
            self.display_message(int(msg_id), int(conv_id), friends)
        else:
            if show == "all":
                self.display_messages(username, start, end, friends)
            elif show == "new":
                self.show_form_for_new_message(thread, id, friends)
            else:
                self.response.out.write("Invalid url")

    def display_message(self, msg_id, conv_id, friends):
        message = Message.get_by_id(msg_id)
        message.read = True
        message.put()

        template_values = { 'message' : message,
                            'conv_id': conv_id,
                            'username': self.get_cookie("username"),
                            'friends': friends}

        self.render("messages/display_message.html", template_values)

    def display_messages(self, username, start, end, friends):
        conv = User.get_conversations_for(username)

        template_values = { "conversations" : conv, "username": username, 'friends': friends}
        self.render("messages/messages.html", template_values)

    def show_form_for_new_message(self, thread=None, id=None, friends=None):
        """Shows a form for a brand new message and a reply if given thread and id
        """
        context = {}
        if id and thread:
            id = int(id)
            thread = int(thread)

            msg = Message.get_by_id(id)
            conv = Conversation.get_by_id(thread)

            context = {'receiver': msg.sender,  'title': conv.title, 'friends': friends}

        self.render("messages/new_message.html", context)

    @Authentication.do
    def post(self):
        sender   = username = self.get_cookie("username")
        receiver = self.request.get('receiver')
        title    = self.request.get('title')
        content  = self.request.get('content')
        thread, id = self.get_params([ "thread", "id"])

        sender = sender.lower()
        receiver = receiver.lower()

        # Adds a new message to conversation
        if thread and id:
            Conversation.add_new_message(thread, sender, content)
        # Adds a new conversation with first message
        elif receiver and title and content:
            Conversation.add_new_conversation(sender, receiver, title, content)
        else:
            self.response.out.write("Error in Messages.post()")

        if self.request.path == '/messages':
            self.redirect('/messages')
        else:
            self.redirect(self.request.referer)