# Defines connection protocols for GAE's channel to serve XMLHttpRequest headers

# Use memcache for chat instead of datastore (otherwise too many write ops)
# But use datastore to store user details (for authentication), preferences, etc - although these can be cached too

from google.appengine.api import channel
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template


# token = channel.create_channel(user.user_id() + game_key) #Token needs to be unique identifier of client

self.response.out.write(template.render('index.html', token=token))
