from web_temp.controllers.BaseHandler import *

class LogoutPage(BaseHandler):
    def get(self):
        self.set_cookies({"username":"", "log_token":""})
        self.redirect("/")