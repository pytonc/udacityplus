import urllib
from hashlib import md5
from google.appengine.api import memcache
from google.appengine.api.app_identity import get_default_version_hostname
from webapp2 import get_request


def add_dicts(*dicts):
    """add an arbitrary number of dictionaries together
    """
    d = {}
    for x in dicts:
        d.update(x)
    return d

def get_gravatar(email, username):
    gravatar_url = memcache.get('gravatar', namespace=username)

    if not gravatar_url:
        request = get_request()
        default = get_default_version_hostname() + '/img/defaultavatar.png'
        size = 146

        # construct the url
        gravatar_url = request.app.config.get('gravatar_base_url') + md5(email).hexdigest() + "?"
        gravatar_url += urllib.urlencode({'d':default, 's':str(size)})

        # 2 hour expire
        memcache.set('gravatar', gravatar_url, namespace=username, time=120)


    return gravatar_url