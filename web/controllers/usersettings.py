from boilerplate.lib.basehandler import user_required
from web.controllers.BaseHandler import BaseHandler
import webapp2
import logging
from web.util.forms import EditSettingsForm
from web.models.User import User
from webapp2_extras.i18n import gettext as _

class UserSettings(BaseHandler):
    @user_required
    def get(self):
        profile = User.get_by_id(long(self.user_id))
        self.form.process(obj=profile)
        self.render_template('usersettings.html')

    @user_required
    def post(self):
        """Edit settings
        """
        if not self.form.validate():
            return self.get()

        user = User.get_by_id(long(self.user_id))

        self.form.populate_obj(user)
        user.put()

        message = _("Settings saved")
        self.add_message(message, 'info')

        self.redirect(self.request.url)

    @webapp2.cached_property
    def form(self):
        return EditSettingsForm(self)