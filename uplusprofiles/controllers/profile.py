from google.appengine.ext.ndb import Key, get_multi
from BaseHandler import *
from jinja_custom.helpers import get_gravatar
from models.Course import Course
from models.User import User
from datetime import date, timedelta
import logging


class ProfilePage(BaseHandler):
    def organize_courses_for(self, user):
        all =  user.get_all_courses()
        cc = get_multi([c.course for c in all if c.completed == True])
        ic = get_multi([c.course for c in all if c.completed == False])

        return all, ic, cc

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
            user = User.save(username, '{}@someplace.com'.format(username), 'some long password')


        gravatar = user.avatar_url
        friends = []

        if user:
            all, ic, cc = self.organize_courses_for(user)

            if user.dob:
                dob = user.dob.strftime('%m/%d/%Y')
            else:
                dob = None


            context = {'user': user,
                       'dob': dob,
                       'username': username,
                       'gravatar': gravatar,
                       'friends': friends,
                       'friend_btn': False,
                       'courses_all': Course.courses_to_dict(),
                       'courses_completed': cc,
                       'courses_incomplete': ic,
                       'errors': {}}

            self.render(template, context)
        else:
            self.redirect('/logout')

    def clean_user_data(self, user, **kwargs):
        if not kwargs['password'] and not kwargs['password_confirm']:
            del kwargs['password']
            del kwargs['password_confirm']
            p = {}
        else:
            _, p = User.valid_passwords(kwargs['password'], kwargs['password_confirm'])
        _, e = User.valid_email(kwargs['email'], user)
        _, b = User.valid_date(kwargs['dob'])


        if user.email != kwargs['email']:
            valid, e = User.valid_email(kwargs['email'])

        #TODO: should probably rename this, it can add whatever 3 dictionaries
        errors = User.adduep(p, e, b)

        return errors

    #@Authentication.do
    def post(self, username):
        fields = self.get_params_dict((
            'real_name',
            'email',
            'short_about',
            'dob',
            'tools',
            'password',
            'password_confirm',
            'notify_on_msg'
            ))

        iclasses = self.request.get_all('classes_inprog')
        cclasses = self.request.get_all('classes_completed')
        fields['iclasses'] = iclasses
        fields['cclasses'] = cclasses
        fields['username'] = username

        user = Key(User, username).get()

        errors = self.clean_user_data(user, **fields)

        context = {
            'errors': errors,
            'user': user
        }

        if not errors:
            user.update(**fields)
            self.redirect('/{}'.format(username))
        else:

            if user.dob:
                dob = user.dob.strftime('%m/%d/%Y')
            else:
                dob = None
            all, ic, cc = self.organize_courses_for(user)
            context['courses_all'] = Course.courses_to_dict()
            context['courses_completed'] = cc
            context['courses_incomplete'] = ic
            context['dob'] = dob
            context['username'] = username
            context['gravatar'] = user.avatar_url
            context['friends'] = []
            context['friend_btn'] = False
            context['errors'] = errors
            self.render('profile/edit.html'.format(username), context)