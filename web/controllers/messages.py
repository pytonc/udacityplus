# Display specific message if message id is given in the
# url, otherwise get show param and display inbox, outbox 
# or render form for a new message.
#
# If start and end params are given, in inbox/outbox show 
# messages from start to end sorted by creation time DESC
# else use default values defined in model (and temp.js)
from boilerplate.lib.basehandler import user_required
from web.models.User import User
from web.models.Message import Message
from web.controllers.BaseHandler import *
from web.models.Message import  Conversation
from web.contactextern.usernotifications import new_message_notify
from web.controllers.helpers.errorretrieval import check_valid_receiver
from web.util import forms
import webapp2


class MessagePage(BaseHandler):
    @user_required
    def get(self, conv_id=None, msg_id=None):
#       (conv_id and msg_id) or (not conv_id and not msg_id)
        if not bool(conv_id) ^ bool(msg_id):

            show, start, end, thread, id = self.get_params(["show", "from", "to", "thread", "id"])


            if show in ('all', 'new') or not show:
                if show == 'new':
                    self.show_form_for_new_message(conv_id, msg_id)
                elif show == 'all' or not (show or conv_id or msg_id):
                    self.display_messages(self.username, start, end)
                elif conv_id and msg_id:
                    self.display_message(int(msg_id), int(conv_id))
            else:
                self.response.out.write("invalid url")

    @user_required
    def display_message(self, msg_id, conv_id):
        conv = Conversation.get_by_id(conv_id)
        if self.username not in conv.receivers_list_norm:
            self.abort(403)
        else:
            message = Message.get_by_id(msg_id)
            if message.sender != self.username:
                message.read = True
                message.put()

            template_values = { 'message' : message,
                                'conv_id': conv_id,
                                'username': self.username,}

            self.render_template("messages/display_message.html", **template_values)

    def display_messages(self, username, start, end):
        conv = User.get_conversations_for(username, start, end)

        template_values = { "conversations" : conv, "username": username}
        self.render_template("messages/messages.html", **template_values)

    def show_form_for_new_message(self, thread=None, id=None):
        """Shows a form for a brand new message and a reply if given thread and id
        """
        context = {'username': self.username}

        if id and thread:
            id = int(id)
            thread = int(thread)

            msg = Message.get_by_id(id)
            conv = Conversation.get_by_id(thread)

            self.form.receiver.data = msg.sender
            self.form.title.data = conv.title

        self.render_template("messages/new_message.html", **context)

    def notify_user(self, sender, conv_id, msg):
        #TODO: use boilerplate/task queue
        conv = Conversation.get_by_id(int(conv_id))
        for uname in conv.receivers_list_norm:
            if uname != sender:
                user = User.get_user(uname)
                if user.notify_on_msg:
                    new_message_notify(user.email, conv_id, msg)

    @user_required
    def post(self, conv_id=None, msg_id=None):
        if not self.form.validate():
            return self.show_form_for_new_message()

        # Adds a new message to conversation
        if conv_id and msg_id and conv_id.isdigit() and msg_id.isdigit():

            msg = Conversation.add_new_message(self.form.sender.data, self.form.content.data, conv_id=conv_id)
            self.notify_user(self.form.sender.data, conv_id, msg)

        # new conversation: adds a new conversation with first message
        elif self.form.receiver.data and self.form.title.data and self.form.content.data:
            data = [self.form.data.get(i) for i in ('sender', 'receiver', 'title', 'content')]
            (conv, msg) = User.add_new_conversation(*data)
            self.notify_user(self.form.sender.data, conv.key.id(), msg)
        else:
            self.response.out.write("Error in Messages.post()")

        self.redirect(self.request.referer)

    @webapp2.cached_property
    def form(self):
        return forms.MessageForm(self)