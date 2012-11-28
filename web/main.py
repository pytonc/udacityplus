import webapp2
from web.controllers.friends    import FriendsController
from web.controllers.home       import HomePage
from web.controllers.signup     import SignUpPage
from web.controllers.login      import LoginPage
from web.controllers.logout     import LogoutPage
from web.controllers.forbidden  import Forbidden
from web.controllers.messages   import MessagePage
from web.controllers.profile    import ProfilePage
from web.controllers.usersearch import Search

import logging
import os


DEBUG = bool(os.environ['SERVER_SOFTWARE'].startswith('Dev'))
if DEBUG:
    logging.getLogger().setLevel(logging.DEBUG)

app = webapp2.WSGIApplication([
    (r'/', HomePage),
    (r'/signup', SignUpPage),
    (r'/login', LoginPage),
    (r'/logout', LogoutPage),
    (r'/forbidden', Forbidden),
    (r'/messages(?:/?)([0-9]*)(?:/?)([0-9]*)', MessagePage),
    (r'/friends', FriendsController),
    (r'/search', Search),
    (r'/(?P<username>\w+)', ProfilePage),
    ], debug=DEBUG)

