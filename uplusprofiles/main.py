import webapp2
from controllers.profile import ProfilePage
import logging
import os

DEBUG = bool(os.environ['SERVER_SOFTWARE'].startswith('Development'))
if DEBUG:
    logging.getLogger().setLevel(logging.DEBUG)


app = webapp2.WSGIApplication([
    (r'/(?P<username>\w+)', ProfilePage),
    ], debug=DEBUG)

