import webapp2
from web_temp.controllers.friends    import FriendsController
from web_temp.controllers.home       import HomePage
from web_temp.controllers.signup     import SignUpPage
from web_temp.controllers.login      import LoginPage
from web_temp.controllers.logout     import LogoutPage
from web_temp.controllers.forbidden  import Forbidden
from web_temp.controllers.messages   import MessagePage
from web_temp.controllers.profile    import ProfilePage
from web_temp.controllers.usersearch import Search

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

