from BaseHandler import *

class HomePage(BaseHandler):
    def get(self):
        template_values = {'title' : self.get_title()}
        self.render("index.html", template_values)

    def get_title(self):
        name = self.get_cookie('username')
        return "Welcome Back, %s!" % name if name else "Welcome to UdacityPlus!"