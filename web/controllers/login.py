from web.controllers.BaseHandler import *
from web.externals.bcrypt import bcrypt as bc
from web.controllers.helpers.authentication import Authentication as aut
from web.controllers.helpers.errorretrieval import get_login_errors

class LoginPage(BaseHandler):
    def get(self):
        self.render("login.html", {'errors': None})

    def post(self):
        #TODO: what if i'm already logged in
        params = self.get_params(["username", "password"])
        log_token = aut.valid_login(*params)
        if log_token:
            username, _ = params
            self.set_cookies({"username": username, "log_token": log_token})
            self.redirect("/")
        else:
            errors = get_login_errors(*params)
            self.render("login.html", {'errors': errors})