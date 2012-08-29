# AUTHENTICATION
#
# @Authentication.do decorator check 
# if user is allowed to see a page


from models.User import User

class Authentication(object):
    
    @staticmethod
    def do(fn):
        def wrapper(self, *args):
            username = self.request.cookies.get("username")
            password = self.request.cookies.get("password")
            if User.exist(username, password):
                return fn(self, *args)
            else:
                self.redirect("/forbidden")
        return wrapper