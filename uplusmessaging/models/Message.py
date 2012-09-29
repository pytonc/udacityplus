from google.appengine.ext import ndb


class Message(ndb.Model):
    created     = ndb.DateTimeProperty(auto_now_add=True)
    modified    = ndb.DateTimeProperty(auto_now=True)
    content     = ndb.TextProperty(required=True)
    sender      = ndb.StringProperty(required=True)
    read        = ndb.BooleanProperty(default=False)
    deleted_for = ndb.StringProperty()


class Conversation(ndb.Model):
    owner           = ndb.StringProperty(required=True)
    receivers_list    = ndb.KeyProperty(kind='User', repeated=True)
    receivers_list_norm    = ndb.StringProperty(repeated=True)
    title           = ndb.StringProperty(required=True)
    created         = ndb.DateTimeProperty(auto_now_add=True)
    modified        = ndb.DateTimeProperty(auto_now=True)
    messages_list   = ndb.KeyProperty(Message, repeated=True)
    deleted_for     = ndb.StringProperty()

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
    def add_new_message(cls, sender, content, conv_id=None, conv_key=None):
        """Creates a new message appends to conversation

        Returns:
         The new Message object
        """

        if not bool(conv_id) ^ bool(conv_key):
            raise AttributeError('Provide either conv_id or key but not both')

        if conv_key:
            conv = conv_key.get()
        else:
            conv = cls.get_by_id(int(conv_id))

        msg = Message(
            sender = sender,
            content = content,
        )
        msg.put()
        conv.insert_message(msg.key)
        conv.put()
        return msg

    @classmethod
    def delete_message(cls, username, conv_id, msg_id):
        """Delete a message. If username is Conversation.owner, the message gets deleted for both users, otherwise

        Args:
         username: User for which to delete the message. If owner, delete for both receivers, if not, delete only for
                   username
         conv_id: Conversation id
         msg_id: Message id to delete

        Returns: ????????

        """
        msg = Message.get_by_id(msg_id)
        conv = cls.get_by_id(conv_id)

        # check if username is an owner of the Conversation
        if username == conv.owner:
            # delete entire conversation if there's only one message in it
            if len(conv.messages_list) == 1:
                cls.delete_conversation(username, key=conv.key)
            # delete the single message from conversation list and the message object
            else:
                conv.messages_list.remove(msg.key)
                msg.key.delete()
        # username is not the owner of the conversation
        else:
            if len(conv.messages_list) == 1:
                cls.delete_conversation(username, key=conv.key)
            else:
                msg.deleted_for = username
                msg.put()

    @classmethod
    def delete_messages_for(cls, username, keys):
        """Deletes messages for username

        Args:
         username: username of the user who to delete messages for
         keys: list of Message keys to delete

        Returns:
         A list of keys for the deleted messages
        """
        msgs = ndb.get_multi(keys)

        for m in msgs:
            m.deleted_for = username

        return ndb.put_multi(msgs)

    @classmethod
    def delete_conversation(cls, username, conv_id=None, key=None):
        """Delete conversation for username, if owner, delete permanently, if not, write to deleted_for

        Args:
         conv_id: Conversation id
         key: Conversation key, provide either one, not both

        Returns:
         ?????????
        """
        if not bool(conv_id) ^ bool(key):
            raise AttributeError('Provide either conv_id or key but not both')

        if key:
            conv = key.get()
        else:
            conv = cls.get_by_id(conv_id)

        if username == conv.owner:
            ndb.delete_multi(conv.messages_list)
            key.delete()
        else:
            conv.deleted_for = username
            cls.delete_messages_for(username, conv.messages_list)
            conv.put()
