from BaseHandler import *
from models.User import User
from authentication import Authentication as aut

class SignUpPage(BaseHandler):

    def get(self):
        self.render("signup.html")

    def post(self):
        params = self.get_params(["username", "email", "password"])
        user = User.save(*params)

        if user:
            log_token = aut.create_and_save_log_token(user)
            self.set_cookies({'username':user.username, 'log_token':log_token})
            self.redirect("/")
        else:
            self.redirect("/signup")