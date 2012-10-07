from webapp2 import uri_for
from BaseHandler import *
from controllers.helpers.authentication import Authentication
from jinja_custom.helpers import get_gravatar
from models.User import User
from datetime import date, timedelta


class ProfilePage(BaseHandler):
    #@Authentication.do
    def get(self, username):
        """display profile of user with username, if None, display logged in user
        """

        mode, = self.get_params(['mode'])


        if mode != 'edit':
            template = 'profile/profile.html'
        else:
            template = 'profile/edit.html'

        user = User.get_user(username)
        if not user:
            user = User.save(username, 'some long password', '{}@someplace.com'.format(username))


        dob = user.created - 13 * timedelta(days=365)

        gravatar = user.avatar_url
        friends = []

        if user:

            context = {'user': user, 'dob': dob, 'username': username, 'gravatar': gravatar, 'friends': friends, 'friend_btn': False}

            self.render(template, context)
        else:

            self.redirect('/logout')


    #@Authentication.do
    def post(self, username):

        pass
