__author__ = "Anthony, rrandom, Jan Zegan"

import json
from google.appengine.ext import  ndb
from google.appengine.api import memcache
from web.util.common import channel_key

class ChatChannel(ndb.Model):
    '''A chat channel'''
    # key_name is channelname.lower()
    channelname = ndb.StringProperty(required = True) # case SeNsItIvE
    created = ndb.DateTimeProperty(auto_now_add = True)
    users = ndb.TextProperty(required = False) # JSON array
    def store(self):
        '''Store in memcache and datastore'''
        memcache.set(channel_key(self.key.id()), self)
        self.put()
    def get_user_names(self):
        '''Returns a list of all the users in this channel'''
        return json.loads(self.users)
    def add_user(self, username):
        '''Adds a username to this channel's user list'''
        users = json.loads(self.users)
        if username not in users:
            users.append(username)
            self.users = json.dumps(users)
            self.store()
    def remove_user(self, username):
        '''Removes a username from this channel's user list'''
        users = json.loads(self.users)
        if username in users:
            users.remove(username)
            self.users = json.dumps(users)
            self.store()