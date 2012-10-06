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

import re


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

    created         = ndb.DateTimeProperty(auto_now_add=True)
    updated         = ndb.DateTimeProperty(auto_now=True)

#    friends         = ndb.KeyProperty(kind='User', repeated=True)
    friends         = ndb.StringProperty(repeated=True)

    # details
    forum_name      = ndb.StringProperty()
    real_name       = ndb.StringProperty()
    short_about     = ndb.StringProperty()
    tools           = ndb.TextProperty()
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


    @classmethod
    def get_user(cls, username):
        # shortcut for other classes that import User
        return cls.query(User.username_norm == username.lower()).get()

    @classmethod
    def valid_password(cls, password):
        p = len(password)
        return  p >= 8 and p < 50

    @classmethod
    def valid_username(cls, username):
        if uname.match(username):
            users = cls.query(User.username_norm == username.lower()).fetch(1, projection=['username'])
        else:
            return False

        return not users

    @classmethod
    def valid_email(cls, email):
        email = cls.query(User.email == email).fetch(1, projection=['username'])
        return not email

    @classmethod
    def valid(cls, username, email, password):
        return cls.valid_password(password) and \
               cls.valid_username(username) and \
               cls.valid_email(email)

    @classmethod
    def save(cls, username, email, password):
        """Save a user object

        Returns:
         The saved User object
        """
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

    def get_friends(self, limit=10, offset=0):
        """Gets friends for current User object

        Returns:
         A list of User objects who are current in current User's friends list or
         None if User's friends list is empty
        """
        if bool(self.friends):
            f = User.query(User.username_norm.IN(self.friends)).order(-User.username)\
                    .fetch(limit, offset=offset, projection=['username', 'real_name'])
            return f
        return None

    def delete_friend(self):
        #TODO: deleting friends
        pass
