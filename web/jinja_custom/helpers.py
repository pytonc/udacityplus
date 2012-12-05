from google.appengine.api import memcache
from google.appengine.api.app_identity import get_default_version_hostname
import webapp2
from web.controllers.helpers.authentication import Authentication
import urllib
from hashlib import md5

def is_authenticated():
    username  = webapp2.get_request().cookies.get("username")
    log_token = webapp2.get_request().cookies.get("log_token")

    return Authentication.valid_log_token(username, log_token) or False
