# Simple user model that we can use
# in further development of pm part
#
# Some helpful static methods added
#
#
# VALIDATORS
#
# valid_password()
# valid_username()
# valid_email()
# valid() - check all above
#
#
# SAVE
# 
# save() - save and return user if valid() else False
#
#
# LOG TOKEN
#
# bcrypt.gensalt() is used for creating tokens
# tokens in database are hashed with bcrypt
# new token is generated with every new login


from google.appengine.ext import  ndb
from google.appengine.ext.ndb.key import Key
from externals.bcrypt import bcrypt as bc

class ExternalProfileLink(ndb.Model):
    url             = ndb.StringProperty(required=True)
    profile_loc     = ndb.StringProperty(required=True, choices={'Facebook', 'Twitter', 'G+',
                                                                'LinkedIn', 'Website', 'GitHub', 'BitBucket',
                                                                'Blog', 'Portfolio', 'Other', 'Coursera', })

class Location(ndb.Model):
    city            = ndb.StringProperty()
    country         = ndb.StringProperty()


class User(ndb.Model):
    username        = ndb.StringProperty(required=True)
    username_norm   = ndb.ComputedProperty(lambda self: self.username.lower())
    password        = ndb.StringProperty(required=True)
    email           = ndb.StringProperty(required=True)

#    friends         = ndb.KeyProperty(kind='User', repeated=True)
    friends         = ndb.StringProperty(repeated=True)

    # details
    forum_name      = ndb.StringProperty()
    real_name       = ndb.StringProperty()
    short_about     = ndb.StringProperty()
    tools           = ndb.StringProperty()
    age             = ndb.IntegerProperty()
    profile_link    = ndb.StructuredProperty(ExternalProfileLink, repeated=True)
    location        = ndb.StructuredProperty(Location)

    # TODO: upload to a static directory?
    avatar          = ndb.BlobProperty()
    avatar_url      = ndb.StringProperty(default="/img/defaultavatar.png")
    use_gravatar    = ndb.BooleanProperty(default=False)

    # settings
    show_friends    = ndb.BooleanProperty(default=False)
    log_token       = ndb.StringProperty(required=False)

    conversations   = ndb.KeyProperty(kind='Conversation', repeated=True)

    created         = ndb.DateTimeProperty(auto_now_add=True)
    updated         = ndb.DateTimeProperty(auto_now=True)

    def add_conversation(self, conversation):
        self.conversations.append(conversation)

    def get_all_conversations(self):
        return ndb.get_multi(self.conversations)

    @classmethod
    def add_conversation_for_user(cls, username, conversation):
        """Add a conversation thread for user with username
        """
        u = cls.query(User.username_norm == username.lower()).get()
        u.conversations.append(conversation)
        u.put()

    @classmethod
    def add_conversation_for_users(cls, conversation, *users):
        """Adds participants to a conversation thread for each user in users
        """
        for user in users:
            cls.add_conversation_for_user(user, conversation)

    @classmethod
    def get_user(cls, username):
        # shortcut for other classes that import User
        return cls.query(User.username_norm == username).get()

    @classmethod
    def get_conversations_for(cls, username):
        """Gets conversations for user with username
        """
        u = User.query(User.username_norm == username.lower()).get()
        return ndb.get_multi(u.conversations)

    @classmethod
    def valid_password(cls, password):
        return len(password) < 40

    @classmethod
    def valid_username(cls, username):
        n = len(username)
        users = cls.get_user(username)
        return not users and n > 4 and n < 21

    @classmethod
    def valid_email(cls, email):
        emails = cls.query(User.email == email).get()
        #too lazy for regex now
        return emails == None

    @classmethod
    def valid(cls, username, email, password):
        return cls.valid_password(password) and \
               cls.valid_username(username) and \
               cls.valid_email(email)

    @classmethod
    def save(cls, username, email, password):
        #TODO: check for duplicate usernames and emails
        if cls.valid(username, email, password):
            password = bc.hashpw(password, bc.gensalt())
            # call to create and save log token is in signup controller
            user = cls(id = username, username = username, password = password, email = email)
            user.put()
            return user
        return False

    @classmethod
    def add_friend(cls, me, friend):
        #TODO: check if friend exists, etc
        #TODO: friend requests/approvals - right now auto adds to both parties
        #TODO: use transactions

        mes = cls.query(cls.username_norm == me.lower()).get()
        if friend not in mes.friends:
            mes.friends.append(friend.lower())
            mes.put()

        # just auto add me to the other person's list
        fs = cls.query(cls.username_norm == friend.lower()).get()
        if me not in fs.friends:
            fs.friends.append(me.lower())

            fs.put()

    def get_friends(self):
        keys = [ndb.Key('User', f) for f in self.friends]
        return ndb.get_multi(keys)

    def delete_friend(self):
        #TODO: deleting friends
        pass