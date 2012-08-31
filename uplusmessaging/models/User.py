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


from google.appengine.ext import db
from externals.bcrypt import bcrypt as bc

class User(db.Model):
    username  = db.StringProperty(required=True)
    password  = db.StringProperty(required=True)
    email     = db.StringProperty(required=True)
    log_token = db.StringProperty(required=False)

    @staticmethod
    def get_user(username):
        # shortcut for other classes that import User
        return User.gql("WHERE username=:1", username).get()

    @staticmethod
    def valid_password(password):
        return len(password) < 40

    @staticmethod
    def valid_username(username):
        n = len(username)
        users = User.get_user(username)
        return not users and n > 4 and n < 21

    @staticmethod
    def valid_email(email):
        emails = User.gql("WHERE email=:1", email).get()
        #too lazy for regex now
        return emails == None

    @staticmethod
    def valid(username, email, password):
        return User.valid_password(password) and \
               User.valid_username(username) and \
               User.valid_email(email)

    @staticmethod
    def save(username, email, password):
        if User.valid(username, email, password):
            password = bc.hashpw(password, bc.gensalt())
            # call to create and save log token is in signup controller
            user = User(username = username, password = password, email = email)
            user.put()
            return user
        return False