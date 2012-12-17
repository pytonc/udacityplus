from wtforms import fields
from wtforms import Form
from wtforms import validators
from boilerplate.lib import utils
from webapp2_extras.i18n import lazy_gettext as _
#from webapp2_extras.i18n import ngettext, gettext
from boilerplate import forms
from web.models.Course import Course
import re
from datetime import date
from web.models.User import User

_UDOB = '^(0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])[- /.]((?:19|20)\d\d)$'
udob = re.compile(_UDOB)

_UNAMEP = r'^[A-Za-z0-9_-]{4,21}$'
uname = re.compile(_UNAMEP)

TEXTAREA_MAXLENGTH=2000

class SettingsMixin(forms.BaseForm):
    public = fields.BooleanField(_("Profile is visible"))
    notify_on_msg = fields.BooleanField(_('Send email on new message'))
    searchable = fields.BooleanField(_('Available in search'))
    show_friends = fields.BooleanField(_('Show friends'))

class EditSettingsForm(SettingsMixin):
    pass

class EditProfileForm(forms.EditProfileForm, SettingsMixin):
    # needs formatting
#    aboutd = fields.TextAreaField(_('About'), [validators.Length(max=TEXTAREA_MAXLENGTH)], id='wmd-input-about')
#    tools = about = fields.TextAreaField(_('Tools'), [validators.Length(max=TEXTAREA_MAXLENGTH)], id='wmd-input-tools')
    # need to know what was selected
#    classes_inprog = fields.SelectField(u'Courses in progress', choices=Course.courses_to_optgroup())
#    classes_completed = fields.SelectField(u'Courses completed', choices=Course.courses_to_optgroup())

    dob = fields.DateField(_('Date of Birth'),
        [validators.optional()], format='%m/%d/%Y')

    def validate_dob(form, field):
        if not field.raw_data or isinstance(field.raw_data[0], basestring) and not field.raw_data[0].strip():
            field.errors[:] = []
            raise validators.StopValidation()
        elif not udob.match(field.raw_data[0]):
            raise validators.ValidationError("Invalid date format.")
        else:
            m, d, y = map(int, udob.match(field.raw_data[0]).groups())
            return date(y, m, d)

class MessageForm(forms.BaseForm):
    sender = fields.TextField(_('Sender'), [validators.Length(max=forms.FIELD_MAXLENGTH)])
    receiver = fields.TextField(_('Receiver'), [validators.Required(), validators.Length(max=forms.FIELD_MAXLENGTH)])
    title = fields.TextField(_('Title'), [validators.Required(), validators.Length(max=forms.FIELD_MAXLENGTH)])
    content = fields.TextAreaField(_('Sender'), [validators.Required(), validators.Length(max=TEXTAREA_MAXLENGTH)])

    def validate_receiver(form, field):
        if not field.raw_data or isinstance(field.raw_data[0], basestring) and not field.raw_data[0].strip():
            field.errors[:] = []
            raise validators.StopValidation()
        if not uname.match(field.raw_data[0]):
            raise validators.ValidationError("Bad username format.")
        elif not bool(User.query(User.username == field.raw_data[0]).fetch(1, projection=['email'])):
            raise validators.ValidationError("User does not exist")
        elif form.sender.data != field.raw_data[0] and \
             field.raw_data[0] not in User.get_user(form.sender.data).friends:
            raise validators.ValidationError("You cannot message this user")
        return field.raw_data[0]