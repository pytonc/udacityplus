import webapp2
from controllers.profile import ProfilePage

app = webapp2.WSGIApplication([
    (r'/(?P<username>\w+)', ProfilePage),
    ], debug=False)

