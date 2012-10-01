from webapp2 import uri_for
from BaseHandler import *
from controllers.helpers.authentication import Authentication
from jinja_custom.helpers import get_gravatar
from models.User import User


class ProfilePage(BaseHandler):
    @Authentication.do
    def get(self, username):
        """display profile of user with username, if None, display logged in user
        """
        if not username:
            username = self.get_cookie("username")

        user = User.get_user(username)
        if user:
            # this is for link to logged in user's profile
            username = self.get_cookie("username")
            me = User.get_user(username)
            friends = me.get_friends()

            if friends:
                friend_btn = user.username_norm not in (f.username_norm for f in friends)
            else:
                friend_btn = True
            context = {'user': user, 'username': username, 'friends': friends, 'friend_btn': friend_btn}

            self.render("profile/profile.html", context)
        else:
            self.abort(404)

    @Authentication.do
    def post(self):
        pass
