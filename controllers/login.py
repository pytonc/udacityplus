from BaseHandler import *
from models.User import User

class LoginPage(BaseHandler):
    def get(self):
        self.render("login.html")

    def post(self):
        params = self.get_params(["username", "password"])
        if User.exist(*params):
            username, password = params
            self.set_cookies({"username":username, "password":password})
            self.redirect("/")
        else:
            self.redirect("/login")