from BaseHandler import *
from authentication import Authentication as aut
from externals.bcrypt import bcrypt as bc

class LoginPage(BaseHandler):
    def get(self):
        self.render("login.html")

    def post(self):
        params = self.get_params(["username", "password"])
        log_token = aut.valid_login(*params)
        if log_token:
            username, _ = params
            self.set_cookies({"username":username, "log_token":log_token})
            self.redirect("/")
        else:
            self.redirect("/login")