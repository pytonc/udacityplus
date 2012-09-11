import webapp2
from controllers.helpers.authentication import Authentication

def is_authenticated():
    username  = webapp2.get_request().cookies.get("username")
    log_token = webapp2.get_request().cookies.get("log_token")

    return Authentication.valid_log_token(username, log_token) or False