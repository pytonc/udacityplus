from BaseHandler import *
from models.User import User

class HomePage(BaseHandler):
    def get(self):
        #TODO: add sanity
        name = self.get_cookie('username')
        user = User.get_user(name)

        template_values = {'title' : self.get_title(), 'username': name, 'friends': user.get_friends()}
        self.render("index.html", template_values)

    def get_title(self):
        name = self.get_cookie('username')
        return "Welcome Back, %s!" % name if name else "Welcome to UdacityPlus!"