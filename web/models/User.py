from google.appengine.api import memcache

from google.appengine.ext import  ndb
from google.appengine.ext.ndb import QueryOptions
from google.appengine.ext.ndb.key import Key

# messaging
from web.models.Message import  Conversation
from web.models.Message import Message
import web.models.Details as Details

# boilerplate
from boilerplate.models import User
from wtforms.validators import ValidationError

# search index in _post_put_hool
from web.util.searching import create_user_search_document
from web.util.searching import add_to_index
from web.util.searching import find_users
from web.util.searching import remove_from_index

# gravatar
from web.util.common import get_gravatar, available_chat_rooms


class User(User):
    real_name       = ndb.ComputedProperty(lambda x: ''.join([x.name, ' ', x.last_name] if x.name and x.last_name else ''))

    friends         = ndb.StringProperty(repeated=True)
    projects        = ndb.JsonProperty()
    short_about     = ndb.StringProperty(default='')
    tools           = ndb.TextProperty(default='')
    dob             = ndb.DateProperty()

    # settings
    show_friends    = ndb.BooleanProperty(default=False)
    notify_on_msg   = ndb.BooleanProperty(default=True)
    searchable      = ndb.BooleanProperty(default=True)
    public          = ndb.BooleanProperty(default=True)

    conversations   = ndb.KeyProperty(kind='Conversation', repeated=True)

    def _post_put_hook(self, future):
        """Post put hook, adds user's username and real name to search index. This fires every time a user
         instance is saved
        """
        #TODO: this doesn't fire when user is registered, only on profile edit
        try:

            doc_id = find_users(self.username).results[0].doc_id
        except IndexError:
            doc_id = None

        if self.searchable:
            doc = create_user_search_document(self.username, self.real_name, self.gravatar, doc_id)
            add_to_index(doc, 'users')
        elif not self.searchable and doc_id:
            remove_from_index(doc_id, 'users')

        available_chat_rooms(self.username, self.get_all_courses())

    @property
    def gravatar(self):
        return get_gravatar(self.email, self.username)


    @property
    def chat_rooms(self):
        rooms = memcache.get('chat_rooms', namespace=self.username)
        if not rooms:
            rooms = available_chat_rooms(self.username, self.get_all_courses())
        return rooms

    @classmethod
    def get_user(cls, username):
        """Get User instance for username

        Args:
         username:  string with username

        Returns:
         instance of User class for given username or None
        """
        return User.query(User.username == username).get()


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

    def update(self, form, **kwargs):
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

        form.populate_obj(self)
        for k, v in kwargs.iteritems():
            if hasattr(self, k):
                    setattr(self, k, v)

        self.put()

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
         me_id:        current user's id
         friend_id:    friend's username as string
        """
        #TODO: check if friend exists, etc
        #TODO: friend requests/approvals - right now auto adds to both parties
        #TODO: use transactions

        memcache.delete('friends', namespace=me)

        mes = cls.query(cls.username == me).get()
        if friend not in mes.friends:
            mes.friends.append(friend)

            mes.put()

        # just auto add me to the other person's list
        fs = ndb.Key(User, friend).get()
        fs = cls.query(cls.username == friend).get()
        if me not in fs.friends:
            fs.friends.append(me)

            fs.put()

    def get_friends(self, limit=10, offset=0):
        """Gets friends for current User object

        Returns:
         A list of User objects who are current in current User's friends list or
         None if User's friends list is empty
        """
        if bool(self.friends):
            f = memcache.get('friends', namespace=self.username)
            if not f:
                f = User.query(User.username.IN(self.friends)).order(-User.username)\
                        .fetch(limit, offset=offset)
                memcache.set('friends', f, namespace=self.username, time=1440)
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
        u = cls.query(User.username == username).get()
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

        c = Conversation.query(Conversation.receivers_list_norm.IN([username]))\
        .order(-Conversation.modified)\
        .fetch(limit=limit, offset=offset, keys_only=True)
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

        skey = cls.get_user(sender).key
        rkey = cls.get_user(receiver).key

        if sender == receiver:
            rl = [skey]
            rln  = [sender]
        else:
            rl = [rkey, skey]
            rln = [sender, receiver]

        conv = Conversation(
            owner = skey,
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
