from web_temp.controllers.BaseHandler import *
from web_temp.controllers.helpers.authentication import Authentication as aut
from web_temp.controllers.helpers.errorretrieval import valid
from web_temp.models import User

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