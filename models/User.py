from google.appengine.ext import db

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


class User(db.Model):
    username = db.StringProperty(required=True)
    email    = db.StringProperty(required=True)
    password = db.StringProperty(required=True)

    @staticmethod
    def valid_password(password):
        n = len(password)
        return n > 7 and n < 21

    @staticmethod
    def valid_username(username):
        n = len(username)
        users = User.gql("WHERE username=:1", username).get()
        return users == None and n > 4 and n < 21

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
            user = User(username=username, password=password, email=email)
            user.put()
            return user
        return False

    @staticmethod
    def exist(username, password):
        user = User.gql("WHERE username=:1", username).get()
        if not user:
            return False 
        return user.password == password