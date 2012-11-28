from google.appengine.api import memcache
from google.appengine.api.app_identity import get_default_version_hostname
import webapp2
from web_temp.controllers.helpers.authentication import Authentication
import urllib
from hashlib import md5

def is_authenticated():
    username  = webapp2.get_request().cookies.get("username")
    log_token = webapp2.get_request().cookies.get("log_token")

    return Authentication.valid_log_token(username, log_token) or False


def get_gravatar(email):
    gravatar_url = memcache.get(email, namespace='gravatar')

    if not gravatar_url:
        default = get_default_version_hostname()
        size = 146

        # construct the url
        gravatar_url = "http://www.gravatar.com/avatar/" + md5(email.lower()).hexdigest() + "?"
        gravatar_url += urllib.urlencode({'d':default, 's':str(size)})

        memcache.set(email, gravatar_url, namespace='gravatar')

    return gravatar_url