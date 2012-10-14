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


from google.appengine.ext import  ndb
from google.appengine.ext.ndb.key import Key
from externals.bcrypt import bcrypt as bc
import models.Details as Details

import re


_UNAMEP = r'^[A-Za-z0-9_-]{4,21}$'
uname = re.compile(_UNAMEP)


class User(ndb.Model):
    username        = ndb.StringProperty(required=True)
    username_norm   = ndb.ComputedProperty(lambda self: self.username.lower())
    password        = ndb.StringProperty(required=True)
    email           = ndb.StringProperty(required=True)

    real_name       = ndb.StringProperty()
    display_name    = ndb.StringProperty()

    created         = ndb.DateTimeProperty(auto_now_add=True)
    updated         = ndb.DateTimeProperty(auto_now=True)

    friends         = ndb.StringProperty(repeated=True)

    # details
    forum_name      = ndb.StringProperty()
    short_about     = ndb.StringProperty()
    prog_langs      = ndb.StructuredProperty(Details.Tool, repeated=True)
    soft_tools      = ndb.StructuredProperty(Details.Tool, repeated=True)
    dob             = ndb.DateProperty()
    profile_link    = ndb.StructuredProperty(Details.ExternalProfileLink, repeated=True)
    location        = ndb.StructuredProperty(Details.Location)
    courses         = ndb.KeyProperty(Details.CourseAttempt, repeated=True)

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
        return  p >= 8 and p < 50

    @classmethod
    def valid_username(cls, username):
        if uname.match(username):
            users = cls.query(User.username_norm == username.lower()).fetch(1, projection=['username'])
        else:
            return False

        return not users

    @classmethod
    def valid_email(cls, email):
        email = cls.query(User.email == email).fetch(1, projection=['username'])
        return not email

    @classmethod
    def valid(cls, username, email, password):
        return cls.valid_password(password) and \
               cls.valid_username(username) and \
               cls.valid_email(email)

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


    def add_courses(self, keys):
        """Add a completed or an in-progress course

        Args:
         key: list of key_name/id of the added course
         completed: True by default, adds to courses_completed, False adds to courses_inprogress
        """
        for k in keys:
            if k not in self.courses:
                self.courses.append(k)

        self.put()
        return self

    def get_all_courses(self):
        return ndb.get_multi(self.courses)

    def get_courses(self, completed=True):
        c = ndb.get_multi(self.courses)
        return [course for course in c if course.completed == completed]


    def add_course(self, course_key, completed=True):
        if not isinstance(course_key, Key):
            raise ValueError("course_key must be a Key of a Course")

        # don't append if in list
        courses = ndb.get_multi(self.courses)
        if any([c.course == course_key and c.completed == completed for c in courses]):
            return None

        c = Details.CourseAttempt(
            course=course_key,
            completed=completed,
            parent=self.key
        )
        k = c.put()
        self.courses.append(k)
        self.put()
        return self

    def remove_course(self, course_key, completed=True):
        c = ndb.get_multi(self.courses)

        rem_list = [course for course in c if course.course == course_key and course.completed == completed]

        for course in rem_list:
            self.courses.remove(course.key)
        self.put()
        return self

    def delete_all_courses(self):
        if self.courses:
            ndb.delete_multi(self.courses)
            del self.courses[:]
            self.put()
        return self

    def delete_courses(self, completed=True):
        courses = self.get_courses(completed)
        worklist = map(lambda c: c.key, filter(lambda x: x.completed == completed, courses))
        complist = map(lambda c: c.key, filter(lambda x: x.completed != completed, courses))
        ndb.delete_multi(worklist)
        self.courses = complist
        self.put()
        return self

    def reassign_courses(self, newcourses):
        """Assigns a new list of the existing list of courses
        """
        if not isinstance(newcourses, list):
            raise TypeError('newcourses needs to be a list')

        self.delete_all_courses()
        self.add_courses([c.key for c in newcourses])
        self.put()
        return self



    def delete_friend(self):
        #TODO: deleting friends
        pass
