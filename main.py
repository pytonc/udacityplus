from google.appengine.api import channel
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

class Chat(webapp.RequestHandler):
    """Displays chat UI"""

    def get(self):
        user = users.get_current_user()
        if not user:
            # Restrict access to authenticated viewers
            self.redirect(users.create_login_url(self.request.uri))
            return
        
        
