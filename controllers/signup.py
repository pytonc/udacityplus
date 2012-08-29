from BaseHandler import *

class SignUpPage(BaseHandler):

    def get(self):
        self.render("signup.html")

    def post(self):
        params = self.get_params(["username", "email", "password"])
        user = User.save(*params)

        if user:
            self.set_cookies({'username':user.username, 'password':user.password})
            self.redirect("/")
        else:
            self.redirect("/signup")