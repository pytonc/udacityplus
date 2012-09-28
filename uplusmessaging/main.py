import webapp2
from controllers.friends import FriendsController
from controllers.home      import HomePage
from controllers.signup    import SignUpPage
from controllers.login     import LoginPage
from controllers.logout    import LogoutPage
from controllers.forbidden import Forbidden
from controllers.messages  import MessagePage
from controllers.profile import ProfilePage

app = webapp2.WSGIApplication([
        (r'/', HomePage),
        (r'/signup', SignUpPage),
        (r'/login', LoginPage),
        (r'/logout', LogoutPage),
        (r'/forbidden', Forbidden),
        (r'/messages(?:/?)([0-9]*)(?:/?)([0-9]*)', MessagePage),
        (r'/friends', FriendsController),
        (r'/(?P<username>\w+)', ProfilePage),
    ], debug=False)

