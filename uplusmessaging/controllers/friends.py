from controllers.BaseHandler import BaseHandler
from models.User import User

class FriendsController(BaseHandler):
    def get(self, name, action):
            pass

    def post(self):
        to = self.request.get('to')
        name    = self.request.get('name')
        action  = self.request.get('action')

        if to and name and action:
            actions = {
                'add': User.add_friend,
            }

            actions[action](to, name)

        self.redirect(self.request.referer)