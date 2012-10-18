# Simple user model that we can use
# in further development of pm part
#
# Some helpful static methods added
#
#
# VALIDATORS
#
# valid_password()
# valid_username()
# valid_email()
# valid() - check all above
#
#
# SAVE
# 
# save() - save and return user if valid() else False
#
#
# LOG TOKEN
#
# bcrypt.gensalt() is used for creating tokens
# tokens in database are hashed with bcrypt
# new token is generated with every new login
from google.appengine.ext.ndb import QueryOptions

from google.appengine.ext import  ndb
from google.appengine.ext.ndb.key import Key
from externals.bcrypt import bcrypt as bc
import models.Details as Details
from datetime import datetime
import logging
import re


_UNAMEP = r'^[A-Za-z0-9_-]{4,21}$'
uname = re.compile(_UNAMEP)

_UDOB = r'^(0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])[- /.](19|20)\d\d$'
udob = re.compile(_UDOB)


class User(ndb.Model):
    username        = ndb.StringProperty(required=True)
    username_norm   = ndb.ComputedProperty(lambda self: self.username.lower())
    password        = ndb.StringProperty(required=True)
    email           = ndb.StringProperty(required=True)

    real_name       = ndb.StringProperty(default='')
    display_name    = ndb.StringProperty()

    created         = ndb.DateTimeProperty(auto_now_add=True)
    updated         = ndb.DateTimeProperty(auto_now=True)

    friends         = ndb.StringProperty(repeated=True)

    # details
    forum_name      = ndb.StringProperty()
    short_about     = ndb.StringProperty(default='')
#    prog_langs      = ndb.StructuredProperty(Details.Tool, repeated=True)
    tools           = ndb.TextProperty(default='')
    dob             = ndb.DateProperty()
    profile_link    = ndb.StructuredProperty(Details.ExternalProfileLink, repeated=True)
    location        = ndb.StructuredProperty(Details.Location)

    # TODO: upload to a static directory?
    avatar          = ndb.BlobProperty()
    avatar_url      = ndb.StringProperty(default="/img/defaultavatar.png")
    use_gravatar    = ndb.BooleanProperty(default=False)

    # settings
    show_friends    = ndb.BooleanProperty(default=False)
    log_token       = ndb.StringProperty(required=False)
    notify_on_msg   = ndb.BooleanProperty(default=True)

    conversations   = ndb.KeyProperty(kind='Conversation', repeated=True)


    @classmethod
    def get_user(cls, username):
        # shortcut for other classes that import User
        return cls.query(User.username_norm == username.lower()).get()

    @classmethod
    def valid_password(cls, password):
        p = len(password)
        if not ( p >= 8 and p < 50):
            return False, {'error_password': 'Invalid password length'}
        return True, {}

    @classmethod
    def valid_passwords(cls, password, confirmation):
        errors = {}
        state = True

        if not password or not confirmation:
            errors['error_password'] = "Enter both password and confirmation"
            errors['error_verify'] = 'Enter both password and confirmation'
            state = False
        if not cls.valid_password(password)[0]:
            errors['error_password'] = "Enter a valid password."
            state = False
        if not cls.valid_password(confirmation)[0]:
            errors['error_verify'] = "Enter a valid confirmation password."
            state = False
        if password and password and password != confirmation:
            state = False
            errors['error_match'] = "Passwords do not match."

        return state, errors

    @classmethod
    def valid_username(cls, username):
        errors = {}
        state = True
        if uname.match(username):
            users = cls.query(User.username_norm == username.lower()).fetch(1, projection=['username'])
            if users:
                errors['error_user_exists'] = 'User already exists'
                state = False
        else:
            errors['error_invalid_username'] = 'Invalid username'
            state = False
        return state, errors

    @classmethod
    def valid_email(cls, email, user=None):
        #TODO: validate email format (regex?)
        e = cls.query(User.email == email).get(projection=['username'])

        if e and not user:
            return False, {'error_email': 'Invalid email'}
        elif e and user:
            if e.username == user.username:
                return True, {}
            else:
                return False, {'error_email': 'Invalid email'}
        return True, {}

    @classmethod
    def valid(cls, username, email, password):
        #TODO: check confirmation password, implemented in valid_passwords
        u = cls.valid_username(username)
        p = cls.valid_password(password)
        e = cls.valid_email(email)
        errors = User.adduep(u, e, p)
        if not errors:
            return True, {}

        return False, errors

    @classmethod
    def adduep(cls, udict, edict, pdict):
        """Consolidate dictionaries containing user, email, password errors
        """
        #TODO: generalize this for an arbitrary number of dicts
        errors = dict(
            (n, udict.get(n, '') + pdict.get(n, '') + edict.get(n, ''))
                for n in set(udict)|set(pdict)|set(edict)
        )
        return errors

    def recafooble_classes(self, current, pset, completed):
        """Add or remove courses from the profile

        Args:
         current   - list of Keys of classes currently saved in profile, should be a list of completed or incomplete
                     courses
         pset      - the new list of classes to replace current
         completed - string "iclasses" or "classes" to indicate incomplete or complete respectively
        """
        current = set(current)
        pset = set(pset)
        keep = current.intersection(pset)

        compd = {'iclasses': False, 'cclasses': True}[completed]

        remove = current - keep
        self.remove_courses(remove, compd)

        new = pset - keep
        self.add_courses(new, compd)

    def update(self, **kwargs):
        """Update user fields
        """
        #TODO: update only the changed fields
        current = self.get_all_courses()
        incomplete = [ic.course for ic in filter(lambda c: c.completed == False, current)]
        completed  = [cc.course for cc in filter(lambda c: c.completed, current)]

        classpartition = {
            'iclasses': incomplete,
            'cclasses': completed
        }
        for t, l in classpartition.iteritems():
            if kwargs.has_key(t):
                self.recafooble_classes(l,
                    [ndb.Key('Course', k) for k in kwargs[t]], t)

        if kwargs.has_key('dob'):
            kwargs['dob'] = datetime.strptime(kwargs['dob'], '%m/%d/%Y')
        if kwargs.has_key('notify_on_msg'):
            kwargs['notify_on_msg'] = kwargs['notify_on_msg'] == 'on'

        for k, v in kwargs.iteritems():
            if hasattr(self, k):
                if k != 'password':
                    setattr(self, k, v)
                else:
                    setattr(self, k, bc.hashpw(kwargs['password'], bc.gensalt()))
        self.put()

    @classmethod
    def valid_date(cls, date):
        if udob.match(date):
            return True, {}
        return False, {'error_date': 'Invalid date format, use mm/dd/yyyy'}

    @classmethod
    def save(cls, username, email, password):
        """Save a user object

        Returns:
         The saved User object
        """
        valid, errors = cls.valid(username, email, password)
        if valid:
            password = bc.hashpw(password, bc.gensalt())
            # call to create and save log token is in signup controller
            user = cls(id = username, username = username, password = password, email = email)
            user.put()
            return user
        return False

    @classmethod
    def add_friend(cls, me, friend):
        #TODO: check if friend exists, etc
        #TODO: friend requests/approvals - right now auto adds to both parties
        #TODO: use transactions

        mes = cls.query(cls.username_norm == me.lower()).get()
        if friend not in mes.friends:
            mes.friends.append(friend.lower())
            mes.put()

        # just auto add me to the other person's list
        fs = cls.query(cls.username_norm == friend.lower()).get()
        if me not in fs.friends:
            fs.friends.append(me.lower())

            fs.put()

    def get_friends(self, limit=10, offset=0):
        """Gets friends for current User object

        Returns:
         A list of User objects who are current in current User's friends list or
         None if User's friends list is empty
        """
        if bool(self.friends):
            f = User.query(User.username_norm.IN(self.friends)).order(-User.username)\
                    .fetch(limit, offset=offset, projection=['username', 'real_name'])
            return f
        return None


    def add_courses(self, keys, completed=True):
        """Add a completed or an in-progress course

        Args:
         key: list of key_name/id of the added course
         completed: True by default, adds to courses_completed, False adds to courses_inprogress

        Returns:
         list of CourseAttempt keys
        """
        attempts = []

        for key in keys:
            k = self.add_course(key, completed)
            attempts.append(k)

        return attempts

    def get_all_courses(self):
        keys = Details.CourseAttempt.query(
            Details.CourseAttempt.student == self.key,
            default_options=QueryOptions(keys_only=True))

        return ndb.get_multi(keys)

    def get_courses(self, completed=True):
        keys = Details.CourseAttempt.query(
            Details.CourseAttempt.student == self.key,
            Details.CourseAttempt.completed == completed,
            default_options=QueryOptions(keys_only=True))

        return ndb.get_multi(keys)


    def add_course(self, course_key, completed=True):
        if not isinstance(course_key, Key):
            raise ValueError("course_key must be a Key of a Course instance")

        # don't append if in list
        courses = self.get_all_courses()
        if any([c.course == course_key and c.completed == completed for c in courses]):
            return None

        c = Details.CourseAttempt(
            course=course_key,
            completed=completed,
            student=self.key
        )
        k = c.put()
        return k

    def remove_course(self, course_key, completed=True):
        ca = self.get_courses(completed)

        rem_list = [attempt for attempt in ca if attempt.course == course_key and attempt.completed == completed]

        ndb.delete_multi(rem_list)
        return self

    def remove_courses(self, keys, completed=True):
        """Removes courses from a list of keys

        Args: keys - list of ndb.Key('Course', ...)
        """
        current = self.get_all_courses()
        remove = [attempt.key for attempt in current if attempt.course in keys and attempt.completed == completed]
        ndb.delete_multi(remove)

        return self

    def delete_all_courses(self):
        courses = self.get_all_courses()
        ndb.delete_multi([c.key for c in courses])

        return self

    def delete_courses(self, completed=True):
        courses = self.get_courses(completed)
        ndb.delete_multi([c.key for c in courses])

        return self



    def delete_friend(self):
        #TODO: deleting friends
        pass
