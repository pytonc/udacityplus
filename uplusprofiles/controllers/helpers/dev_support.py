from appengine.api import users

def check_login(fn):
    """Google App Engine's user provider handling with decorator
    """
    def wrapper(obj, *args):
        user = users.get_current_user()
        if user:
            return fn(obj, *args)
        else:
            obj.redirect(users.create_login_url(obj.request.uri))

    return wrapper