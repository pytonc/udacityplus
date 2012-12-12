from web.util import forms
import webapp2
from boilerplate.lib.basehandler import BaseHandler as bh
from web.models.User import User
from web.models.Course import Course

class BaseHandler(bh):
    def get_params(self, params):
        return [self.request.get(param) for param in params]

    def get_params_dict(self, params):
        return {param : self.request.get(param) for param in params}

    @webapp2.cached_property
    def message_form(self):
        return forms.MessageForm(self)

    def render_template(self, filename, **kwargs):
        try:
            user = User.get_by_id(long(self.user_id))
            friends = user.get_friends()
            kwargs['friends'] = friends
            kwargs['user_courses'] = user.chat_rooms
        except TypeError:
            # home page, not logged in, so no freinds
            pass

        if hasattr(self, 'message_form'):
            kwargs['message_form'] = self.message_form

        kwargs['all_courses'] = Course.available_course_ids()

        bh.render_template(self, filename, **kwargs)