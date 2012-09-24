from google.appengine.ext import ndb
from User import User


class Message(ndb.Model):
    created     = ndb.DateTimeProperty(auto_now_add=True)
    modified    = ndb.DateTimeProperty(auto_now=True)
    content     = ndb.TextProperty(required=True)
    sender      = ndb.StringProperty(required=True)
    read        = ndb.BooleanProperty(default=False)


class Conversation(ndb.Model):
    receivers_list    = ndb.KeyProperty(User, repeated=True)
    receivers_list_norm    = ndb.StringProperty(repeated=True)
    title           = ndb.StringProperty(required=True)
    created         = ndb.DateTimeProperty(auto_now_add=True)
    messages_list   = ndb.KeyProperty(Message, repeated=True)

    @property
    def messages(self):
        """Get all messages in this Conversation instance
        """
        u = ndb.get_multi(self.messages_list)
        return u

    @property
    def receivers(self):
        """Get all participants in this Conversation thread
        """
        return ndb.get_multi(self.receivers_list)

    def insert_message(self, m):
        """Appends a message to the conversation thread
        """
        self.messages_list.append(m)

    @classmethod
    def add_new_message(cls, thread, sender, content):
        """Creates a new message appends to conversation
        """
        conv = cls.get_by_id(int(thread))
        msg = Message(
            sender = sender,
            content = content,
        )
        msg.put()
        conv.insert_message(msg.key)
        conv.put()

    @classmethod
    def add_new_conversation(cls, sender, receiver, title, content):
        """Adds new conversation with receiver for sender
        """
        skey = ndb.Key('User', sender)
        rkey = ndb.Key('User', receiver)

        conv = cls(
            receivers_list = [rkey, skey],
            receivers_list_norm = [sender, receiver],
            title = title,
        )
        msg = Message(
            sender = sender,
            content = content
        )


        k = msg.put()
        conv.insert_message(k)
        ck = conv.put()

        User.add_conversation_for_users(ck, sender, receiver)

    def delete_message(self):
        #TODO: delete message
        pass

    def delete_conversation(self):
        #TODO: delete conversation
        pass