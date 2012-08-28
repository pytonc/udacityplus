from BaseHandler import *

class LogoutPage(BaseHandler):
    def get(self):
        self.set_cookies({"username":"", "password":""})
        self.redirect("/")