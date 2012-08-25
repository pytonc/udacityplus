import os

import webapp2
import jinja2
from google.appengine.api import channel

# This section will eventually get moved to a Handler class
template_dir = os.path.join(
        os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(
        loader = jinja2.FileSystemLoader(template_dir),
        autoescape = True)

def render_str(template, **params):
    '''Returns a string of the rendered template'''
    t = jinja_env.get_template(template)
    return t.render(params)

def render(template, **kw):
    '''Render using the template and parameters'''
    return(render_str(template, **kw))
# End Handler

class Communication(webapp2.RequestHandler):
    '''Deals with chat traffic'''
    def post(self):
        message = self.request.get('message')
        if not message:
            return

class Main(webapp2.RequestHandler):
    def get(self):
        '''Show connection page'''
        self.response.out.write(render("main.html"))

    def post(self):
        '''Displays chat UI'''
        username = self.request.get('username')
        if not username:
            self.response.out.write(render("main.html"))
        else:
            channel_name = self.request.get('channel')
            token = channel.create_channel(username)
            self.response.out.write(render("chat.html", token=token,
                                           username=username))            

app = webapp2.WSGIApplication([
                               ('/', Main),
                               ('/communication', Communication)
                               ], debug=True)