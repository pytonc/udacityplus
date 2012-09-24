import webapp2
from controllers.helpers.authentication import Authentication
import urllib, hashlib

def is_authenticated():
    username  = webapp2.get_request().cookies.get("username")
    log_token = webapp2.get_request().cookies.get("log_token")

    return Authentication.valid_log_token(username, log_token) or False


def get_gravatar(email):
    default = "http://jz-uplusmessaging.appspot.com"
    size = 146

    # construct the url
    gravatar_url = "http://www.gravatar.com/avatar/" + hashlib.md5(email.lower()).hexdigest() + "?"
    gravatar_url += urllib.urlencode({'d':default, 's':str(size)})

    return gravatar_url