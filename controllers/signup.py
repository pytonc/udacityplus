from BaseHandler import *
from models.User import User
from helpers.authentication import Authentication as aut
from helpers.errorretrieval import valid

class SignUpPage(BaseHandler):

    def get(self):
        self.render("signup.html", {'errors': None})

    def post(self):
        #TODO: works with non-matching passwords, it shouldn't
        params = self.get_params(["username", "email", "password", "password_confirm"])
        user = User.save(*params)

        if user:
            log_token = aut.create_and_save_log_token(user)
            self.set_cookies({'username':user.username, 'log_token':log_token})
            self.redirect("/")
        else:
            _, errors = valid(*params)
            self.render("signup.html", {'errors': errors})