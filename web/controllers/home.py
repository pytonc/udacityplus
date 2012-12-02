from boilerplate.lib.basehandler import BaseHandler
from web.models.User import User

class UserHomePage(BaseHandler):
    def get(self, **kwargs):
        user_session = self.user
        user_session_object = self.auth.store.get_session(self.request)
        if self.user_id:
            user_info = User.get_by_id(long( self.user_id ))
            user_info_object = self.auth.store.user_model.get_by_auth_token(
                user_session['user_id'], user_session['token'])

            try:
                params = {
                    "user_session" : user_session,
                    "user_session_object" : user_session_object,
                    "user_info" : user_info,
                    "user_info_object" : user_info_object,
                    "userinfo_logout-url" : self.auth_config['logout_url'],
                    "friends": user_info.get_friends()
                    }
                return self.render_template('home.html', **params)
            except (AttributeError, KeyError), e:
                return "Secure zone error:" + " %s." % e
        else:
            return self.render_template('home.html')