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


_UDOB = '^(0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])[- /.]((?:19|20)\d\d)$'
udob = re.compile(_UDOB)
TEXTAREA_MAXLENGTH=2000

class OptionsMixin(forms.BaseForm):
    notify_on_msg = fields.BooleanField(u'Send email on new message')
    searchable = fields.BooleanField(u'Available in search')
    show_friends = fields.BooleanField(u'Show friends')

class EditProfileForm(forms.EditProfileForm, OptionsMixin):
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