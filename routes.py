"""
Using redirect route instead of simple routes since it supports strict_slash
Simple route: http://webapp-improved.appspot.com/guide/routing.html#simple-routes
RedirectRoute: http://webapp-improved.appspot.com/api/webapp2_extras/routes.html#webapp2_extras.routes.RedirectRoute
"""


from webapp2_extras.routes import RedirectRoute
from web.controllers import home
from web.controllers import chat
from web.controllers import profile
from web.controllers import friends
from web.controllers import messages
from web.controllers import usersearch
from web.controllers import usersettings


secure_scheme = 'https'

_routes = [
    RedirectRoute('/', home.UserHomePage, name='home', strict_slash=True),
    RedirectRoute('/messages', messages.MessagePage, name="messages", strict_slash=True),
    RedirectRoute('/messages/<conv_id:[0-9]*>/<msg_id:[0-9]*>', messages.MessagePage, name="message", strict_slash=True),
    RedirectRoute('/friends', friends.FriendsController, name='friends', strict_slash=True),
    RedirectRoute('/chat/<channelname:\w+>', chat.Chat, name='chat', strict_slash=True),
    RedirectRoute('/search', usersearch.Search, name="search", strict_slash=True),
    RedirectRoute('/communication', chat.Communication, name='chat-communication', strict_slash=True),
    RedirectRoute('/tokenexpireHandler',chat.TokenexpireHandler, name='tokenexpire', strict_slash=True),
    ('/_ah/channel/connected/?', chat.Connect),
    ('/_ah/channel/disconnected/?', chat.Disconnect),

    RedirectRoute(r'/settings', usersettings.UserSettings, name="settings", strict_slash=True),

    RedirectRoute('/<username:\w+>/project/<mode:\w+>', profile.Projects,
        name="project_view", strict_slash=True, handler_method='view_project', methods=('GET')),

    RedirectRoute('/<username:\w+>/project/add', profile.ProjectsUpload,
        name='project-add', strict_slash=True, handler_method='add_project', methods=('POST')),

    RedirectRoute('/<username:\w+>/project/edit', profile.ProjectsUpload,
        name='project-edit', strict_slash=True, handler_method='edit_project', methods=('POST')),

    RedirectRoute('/<username:\w+>/project/delete', profile.Projects,
        name='project-delete', strict_slash=True, handler_method='delete_project', methods=('POST')),

    RedirectRoute('/', home.UserHomePage, name='home', strict_slash=True),
    ]

_routes_catchall = [
    RedirectRoute('/<username:\w+>', profile.ProfilePage, name='profile', strict_slash=True, methods=('GET, POST')),
]

def get_routes():
    return _routes

def add_routes(app, routes=_routes):
    if app.debug:
        secure_scheme = 'http'
    for r in routes:
        app.router.add(r)

def add_routes_catchall(app):
    add_routes(app, _routes_catchall)