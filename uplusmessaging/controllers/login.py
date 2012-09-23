from BaseHandler import *
from externals.bcrypt import bcrypt as bc
from helpers.authentication import Authentication as aut

class LoginPage(BaseHandler):
    def get(self):
        self.render("login.html")

    def post(self):
        #TODO: what if i'm already logged in
        params = self.get_params(["username", "password"])
        log_token = aut.valid_login(*params)
        if log_token:
            username, _ = params
            self.set_cookies({"username":username, "log_token":log_token})
            self.redirect("/")
        else:
            self.redirect("/login")