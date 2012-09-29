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

        gravatar = None
        friends = None
        user = User.get_user(username)
        if user:
            # this is for link to logged in user's profile
            username = self.get_cookie("username")
            me = User.get_user(username)
            friends = me.get_friends()

            if user.use_gravatar:
                if not user.avatar_url:
                    gravatar = get_gravatar(user.email)
                    user.avatar_url = gravatar
                    user.put()
                else:
                    gravatar = user.avatar_url
            else:
                gravatar = user.avatar_url

            context = {'user': user, 'username': username, 'gravatar': gravatar, 'friends': friends}

            self.render("profile/profile.html", context)
        else:

            self.redirect('/logout')
    @Authentication.do
    def post(self):
        pass
