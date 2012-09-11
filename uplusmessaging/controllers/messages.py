# Display specific message if message id is given in the 
# url, otherwise get show param and display inbox, outbox 
# or render form for a new message.
#
# If start and end params are given, in inbox/outbox show 
# messages from start to end sorted by creation time DESC
# else use default values defined in model (and temp.js)


from BaseHandler import *
from helpers.authentication import Authentication
from models.Message import Message, MessageIndex
import re


class MessagePage(BaseHandler):
    
    @Authentication.do
    def get(self):
        msg_id   = re.search(r"/messages(/?)([0-9]*)", self.request.url).group(2)
        username = self.get_cookie("username")
        show, start, end = self.get_params(["show", "from", "to"])

        if msg_id:
            self.display_message(int(msg_id))
        else:
            if show == "received":
                self.display_inbox(username, start, end)
            elif show == "sent":
                self.display_outbox(username, start, end)
            elif show == "new":
                self.show_form_for_new_message()
            else:
                self.response.out.write("Invalid url")

    def display_message(self, msg_id):
        message = Message.get_by_id(msg_id)
        template_values = { 'message' : message }
        self.render("messages/display_message.html", template_values)

    def display_inbox(self, username, start, end):
        messages = Message.received(username, start, end)
        template_values = { "messages" : messages }
        self.render("messages/display_inbox.html", template_values)

    def display_outbox(self, username, start, end):
        messages = Message.sent(username, start, end)
        template_values = { "messages" : messages }
        self.render("messages/display_outbox.html", template_values)

    def show_form_for_new_message(self):
        self.render("messages/messages/new_message.html")

    @Authentication.do
    def post(self):
        sender   = username = self.get_cookie("username")
        receiver = self.request.get('receiver')
        title    = self.request.get('title')
        content  = self.request.get('content')

        if receiver and title and content:
            r = receiver.split(',')
            msg = Message(sender   = sender, 
                          receivers = r,
                          title    = title, 
                          content  = content)
            msg.put()
            index = MessageIndex(
                key_name='msg_index',
                parent=msg,
                receivers=r
            )
            index.put()

            self.redirect('/')
        else:
            self.response.out.write("Error in Messages.post()")