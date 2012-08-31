# AUTHENTICATION
#
# @Authentication.do decorator check 
# if user is allowed to see a page
#
#
# valid_login(username, password) 
# if username and password are ok, new log_token is created, saved 
# in db and returned to contrroler so it can can be set in a cookie
#
# valid_log_token(username, log_token)
# create_and_save_log_token(user)



from models.User import User
from externals.bcrypt import bcrypt as bc

class Authentication(object):
    
    @staticmethod
    def do(fn):
        def wrapper(self, *args):
            username  = self.request.cookies.get("username")
            log_token = self.request.cookies.get("log_token")

            if Authentication.valid_log_token(username, log_token):
                return fn(self, *args)
            else:
                self.redirect("/forbidden")
        return wrapper

    @staticmethod
    def valid_login(username, password):
        user = User.get_user(username)
        if user and bc.hashpw(password, user.password) == user.password:
            return Authentication.create_and_save_log_token(user) 

    @staticmethod
    def valid_log_token(username, log_token):
        user = User.get_user(username)
        return user and bc.hashpw(log_token, user.log_token) == user.log_token
        
    @staticmethod
    def create_and_save_log_token(user):
        log_token = bc.gensalt()
        user.log_token = bc.hashpw(log_token, bc.gensalt())
        user.put()
        return log_token