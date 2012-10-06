from webapp2 import uri_for
from BaseHandler import *
from controllers.helpers.authentication import Authentication
from jinja_custom.helpers import get_gravatar
from models.User import User


class ProfilePage(BaseHandler):
    #@Authentication.do
    def get(self, username):
        """display profile of user with username, if None, display logged in user
        """

        user = User.get_user(username)
        if not user:
            user = User.save(username, 'some long password', '{}@someplace.com'.format(username))


        gravatar = user.avatar_url
        friends = []

        if user:

            context = {'user': user, 'username': username, 'gravatar': gravatar, 'friends': friends, 'friend_btn': False}

            self.render("profile/profile.html", context)
        else:

            self.redirect('/logout')


    #@Authentication.do
    def post(self):
        pass
