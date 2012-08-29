import webapp2
from controllers.home import HomePage
from controllers.signup import SignUpPage
from controllers.login import LoginPage
from controllers.logout import LogoutPage

app = webapp2.WSGIApplication([
        ('/', HomePage),
        ('/signup', SignUpPage),
        ('/login', LoginPage),
        ('/logout', LogoutPage)
    ], debug=True)
