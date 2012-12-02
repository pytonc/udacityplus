"""
Using redirect route instead of simple routes since it supports strict_slash
Simple route: http://webapp-improved.appspot.com/guide/routing.html#simple-routes
RedirectRoute: http://webapp-improved.appspot.com/api/webapp2_extras/routes.html#webapp2_extras.routes.RedirectRoute
"""


from webapp2_extras.routes import RedirectRoute
from web.controllers import home
#from web import handlers
from web.controllers import profile
from web.controllers import friends
from web.controllers import messages
from web.controllers import usersearch
from web.controllers import forbidden


secure_scheme = 'https'

_routes = [
    RedirectRoute('/', home.UserHomePage, name='home', strict_slash=True),
#    (r'/forbidden', forbidden.Forbidden),
    (r'/messages(?:/?)([0-9]*)(?:/?)([0-9]*)', messages.MessagePage),
    (r'/friends', friends.FriendsController),
    (r'/search', usersearch.Search),
    RedirectRoute('/<username:\w+>', profile.ProfilePage, name='profile', strict_slash=True),

#    RedirectRoute('/secure/', home.HomePage, name='secure', strict_slash=True),
    ]

def get_routes():
    return _routes

def add_routes(app):
    if app.debug:
        secure_scheme = 'http'
    for r in _routes:
        app.router.add(r)