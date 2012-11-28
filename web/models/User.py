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
from web.externals.bcrypt import bcrypt as bc
import web.models.Details as Details
from datetime import datetime
import re
from web.models import Message
from web.models.Message import  Conversation
from web.controllers.helpers.common import adduep
from web.util.searching import create_user_search_document, add_to_index, find_users, remove_from_index


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
    short_about     = ndb.StringProperty()
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
    searchable      = ndb.BooleanProperty(default=True)

    conversations   = ndb.KeyProperty(kind='Conversation', repeated=True)

    def _post_put_hook(self, future):
        """Post put hook, adds user's username and real name to search index. This fires every time a user
         instance is saved
        """
        try:
            doc_id = find_users(self.username_norm).results[0].doc_id
        except IndexError:
            doc_id = None

        if self.searchable:
            # TODO: update document by putting one with the same id
            # TODO: separate log_token to a login tracking subsystem or implement GAE Users. every time a user logs in
            #       User instance gets saved and _post_put_hook called, etc.

            doc = create_user_search_document(self.username_norm, self.real_name, self.avatar_url, doc_id)
            add_to_index(doc, 'users')
        elif not self.searchable and doc_id:
            remove_from_index(doc_id, 'users')

    @classmethod
    def _pre_delete_hook(cls, key):
        # TODO: handle user deletions from index
        pass


    @classmethod
    def save(cls, username, email, password):
        """Save a user object

        Returns:
         The saved User object
        """
        if cls.valid(username, email, password):
            password = bc.hashpw(password, bc.gensalt())
            # call to create and save log token is in signup controller
            user = cls(id = username, username = username, password = password, email = email)
            user.put()
            return user
        return False

    @classmethod
    def get_user(cls, username):
        """Get User instance for username

        Args:
         username:  string with username

        Returns:
         instance of User class for given username or None
        """
        return cls.query(User.username_norm == username.lower()).get()

    @classmethod
    def valid_password(cls, password):
        """Check if password matches some constraint

        Args:
         password:  password string to be checked

        Returns:
         a tuple of
             True or False, indicates if password fits constraint
             dictionary of errors, error_password, or empty
        """
        p = len(password)
        if not ( p >= 8 and p < 50):
            return False, {'error_password': 'Invalid password length'}
        return True, {}

    @classmethod
    def valid_passwords(cls, password, confirmation):
        """Check if password and password confirmation are valid

        Args:
         password:      password
         confirmation:  password confirmation, should be the same as password

        returns:
         tuple of:
          state:        True or False, indicates if password and confirmation are valid
          errors:       dictionary of errors: error_password, error_verify, error_match or empty
        """
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
        """Check if username is valid and available

        Args
         username:  username as string

        Returns
         tupple of:
          state:    True or False indicating if username is valid
          errors;   dictionary of errors, empty or with error_user_exists or error_invalid_username
        """
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
        #TODO: valid_username checks only signup
        _, u = cls.valid_username(username)
        _, p = cls.valid_password(password)
        _, e = cls.valid_email(email)
        errors = adduep(u, e, p)
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
        if remove:
            self.remove_courses(remove, compd)

        new = pset - keep
        if new:
            self.add_courses(new, compd)

    def update(self, **kwargs):
        """Update user fields

        Args:
         **kwargs:  dictionary of updated values
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
    def save(cls, username, email, password, *args):
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
    def add_project(cls, username, project_id):
        """If this is user's first project, creates a new list and adds project_id to it
        otherwise appends project_id to the existing list. 
        """
        user = cls.get_user(username)
        if user:
            projects = user.projects
            if projects:
                projects.append(project_id)
            else:
                projects = [project_id]
            user.projects = projects
            user.put()

    @classmethod
    def remove_project(cls, username, project_id):
        """Removes project_id from user's projects        
        """
        user = cls.get_user(username)
        if user:
            projects = user.projects
            pid = int(project_id)
            if pid in projects:
                projects.remove(pid)
                user.projects = projects
                user.put()

    @classmethod
    def add_friend(cls, me, friend):
        """Add friend to me's friends list and vice versa

        Args:
         me:        current user's username as string
         friend:    friend's username as string
        """
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

    def delete_friend(self):
        #TODO: deleting friends
        pass

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
        """Get all courses for this student

        Returns:
         list of CourseAttempt instances
        """
        keys = Details.CourseAttempt.query(
            Details.CourseAttempt.student == self.key,
            default_options=QueryOptions(keys_only=True))

        return ndb.get_multi(keys)

    def get_courses(self, completed=True):
        """Get CourseAttempts for current user, filter by completed or not

        Args:
         completed: True (default) or False, get completed or incomplete courses

        Returns:
         list of CourseAttempt instances
        """
        keys = Details.CourseAttempt.query(
            Details.CourseAttempt.student == self.key,
            Details.CourseAttempt.completed == completed,
            default_options=QueryOptions(keys_only=True))

        return ndb.get_multi(keys)


    def add_course(self, course_key, completed=True):
        """Adds course for current user

        Args:
         course_key:    Key of the course to be added
         completed:     True (default) or False, indicates whether course is complete or not

        Returns:
         key of the inserted CourseAttempt instance
        """
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
        """Removes course for the current user

        Args:
         course_key:    Key instance of Course to be removed
         completed:     True (default) or False, indicates whether course is complete or not. User may be enrolled
                        and have completed the same course.
        """
        ca = self.get_courses(completed)

        rem_list = [attempt for attempt in ca if
                    attempt and attempt.course == course_key and attempt.completed == completed]

        ndb.delete_multi(rem_list)
        return self

    def remove_courses(self, keys, completed=True):
        """Removes courses from a list of keys

        Args: keys - list of ndb.Key('Course', ...)
        """
        current = self.get_all_courses()
        remove = [attempt.key for attempt in current if
                  attempt and attempt.course in keys and attempt.completed == completed]
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

    def add_conversation(self, conversation):
        self.conversations.append(conversation)

    def get_all_conversations(self):
        return ndb.get_multi(self.conversations)

    @classmethod
    def add_conversation_for_user(cls, username, conversation):
        """Add a conversation thread for user with username

        Args:
         username:  username of user for which to add the conversation
         conversation:  Conversation key to be added

        Returns:
         None:  if no user with username was found
         User instance: if insert was successfull
        """
        u = cls.query(User.username_norm == username.lower()).get()
        if u:
            u.conversations.append(conversation)
            u.put()
            return u
        return None

    @classmethod
    def add_conversation_for_users(cls, conversation, *users):
        """Adds participants to a conversation thread for each user in users

        Args:
         conversation:  Conversation key to be added
         *users:        list of users
        """
        #TODO: why is this conditional here again?
        if all(users):
            users = [users[0]]
        for user in users:
            cls.add_conversation_for_user(user, conversation)

    @classmethod
    def get_conversations_for(cls, username, offset, limit):
        """Gets conversations for user with username

        Returns:
         A list of Conversation objects for username
        """
        limit = int(limit) if limit else 10
        offset = int(offset) if offset else 0

        c = Conversation.query(Conversation.receivers_list_norm.IN([username.lower()]))\
        .order(-Conversation.modified)\
        .fetch(limit=limit, offset=offset, keys_only=True)
        return ndb.get_multi(c)

    def get_conversations(self, limit=10, offset=0):
        """UNUSED - Get conversations for current User object

        Returns:
         A list of Conversation objects
        """

        c = Conversation.query(self.username_norm in Conversation.receivers, keys_only=True)\
        .order(Conversation.modified)\
        .limit(limit, offset=offset)
        return ndb.get_multi(c)

    @classmethod
    def add_new_conversation(cls, sender, receiver, title, content):
        """Adds new conversation with receiver for sender, returns Conversation object

        Args:
         sender:    sender's username as string
         receiver:  receiver's username as string
         title:     title of the conversation
         content:   content of the first post

        Returns:
         tupple with:
          newly created Conversation instance
          newly created Message instance
        """
        #TODO: check if sender and receiver aren't the same person, if so, add only once

        skey = ndb.Key('User', sender)
        rkey = ndb.Key('User', receiver)

        if sender == receiver:
            rl = [skey]
            rln  = [sender]
        else:
            rl = [rkey, skey]
            rln = [sender, receiver]

        conv = Conversation(
            owner = sender,
            receivers_list = rl,
            receivers_list_norm = rln,
            title = title,
        )
        msg = Message(
            sender = sender,
            content = content
        )


        k = msg.put()
        conv.insert_message(k)
        ck = conv.put()

        User.add_conversation_for_users(ck, sender, receiver)

        return conv, msg
