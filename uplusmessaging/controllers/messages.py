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
from contactextern.usernotifications import new_message_notify


class MessagePage(BaseHandler):

    @Authentication.do
    def get(self, conv_id=None, msg_id=None):
#       (conv_id and msg_id) or (not conv_id and not msg_id)
        if not bool(conv_id) ^ bool(msg_id):
            username = self.get_cookie("username")
            show, start, end, thread, id = self.get_params(["show", "from", "to", "thread", "id"])

            me = User.get_user(username)
            friends = me.get_friends()

            if show in ('all', 'new') or not show:
                if show == 'new':
                    self.show_form_for_new_message(conv_id, msg_id, friends)
                elif show == 'all' or not (show or conv_id or msg_id):
                    self.display_messages(username, start, end, friends)
                elif conv_id and msg_id:
                    self.display_message(int(msg_id), int(conv_id), friends)
            else:
                self.response.out.write("invalid url")


    def display_message(self, msg_id, conv_id, friends):
        message = Message.get_by_id(msg_id)
        username = self.get_cookie("username")
        if message.sender != username:
            message.read = True
        message.put()

        template_values = { 'message' : message,
                            'conv_id': conv_id,
                            'username': username,
                            'friends': friends}

        self.render("messages/display_message.html", template_values)

    def display_messages(self, username, start, end, friends):
        conv = User.get_conversations_for(username, start, end)

        template_values = { "conversations" : conv, "username": username, 'friends': friends}
        self.render("messages/messages.html", template_values)

    def show_form_for_new_message(self, thread=None, id=None, friends=None):
        """Shows a form for a brand new message and a reply if given thread and id
        """
        context = {'friends': friends, 'username': self.get_cookie('username')}

        if id and thread:
            id = int(id)
            thread = int(thread)

            msg = Message.get_by_id(id)
            conv = Conversation.get_by_id(thread)

            context['receiver'] = msg.sender
            context['title'] = conv.title

        self.render("messages/new_message.html", context)

    def notify_user(self, sender, conv_id, msg):
        #TODO: use task queue
        conv = Conversation.get_by_id(int(conv_id))
        for uname in conv.receivers_list_norm:
            if uname != sender:
                user = User.get_user(sender)
                if user.notify_on_msg:
                    new_message_notify(user.email, conv_id, msg)

    @Authentication.do
    def post(self, conv_id, msg_id):
        sender   = username = self.get_cookie("username")
        receiver = self.request.get('receiver')
        title    = self.request.get('title')
        content  = self.request.get('content')

        sender = sender.lower()
        receiver = receiver.lower()

        # Adds a new message to conversation
        if conv_id and msg_id:
            msg = Conversation.add_new_message(sender, content, conv_id=conv_id)
            self.notify_user(sender, conv_id, msg)

        # Adds a new conversation with first message
        elif receiver and title and content:
            (conv, msg) = User.add_new_conversation(sender, receiver, title, content)
            self.notify_user(sender, conv.key.id(), msg)
        else:
            self.response.out.write("Error in Messages.post()")

        if self.request.path.startswith('/messages'):
            self.redirect('/messages?show=all')
        else:
            self.redirect(self.request.referer)