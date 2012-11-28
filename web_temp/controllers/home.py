from web_temp.controllers.BaseHandler import *
from web_temp.controllers.helpers.authentication import Authentication
from web_temp.models import User

class HomePage(BaseHandler):
    def get(self):
        name = self.get_cookie('username')
        friends = None
        template_values = {}

        if name:
            user = User.get_user(name)
            if user and Authentication.valid_log_token(user.username_norm, user.log_token):
                friends = user.get_friends()
                template_values = {'title' : self.get_title(), 'username': name, 'friends': friends}
            else:
                self.redirect('/logout')

        self.render("index.html", template_values)

    def get_title(self):
        name = self.get_cookie('username')
        return "Welcome Back, %s!" % name if name else "Welcome to UdacityPlus!"