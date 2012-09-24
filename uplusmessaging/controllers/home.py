from BaseHandler import *
from controllers.helpers.authentication import Authentication
from models.User import User

class HomePage(BaseHandler):
    @Authentication.do
    def get(self):
        #TODO: add sanity
        name = self.get_cookie('username')
        friends = None

        if name:
            user = User.get_user(name)
            friends = user.get_friends()

        template_values = {'title' : self.get_title(), 'username': name, 'friends': friends}
        self.render("index.html", template_values)

    def get_title(self):
        name = self.get_cookie('username')
        return "Welcome Back, %s!" % name if name else "Welcome to UdacityPlus!"