import json
from google.appengine.ext import  ndb
from google.appengine.api import memcache
from web.util.chat import user_key
import logging

class ChatUser(ndb.Model):
    '''A user'''
    # key_name is username.lower()
    username = ndb.StringProperty(required = True) # case SeNsItIvE
    joined = ndb.DateTimeProperty(auto_now_add = True)
    identifier = ndb.StringProperty(required = True) # Session specific
    startingchannel = ndb.TextProperty(required = False)
    channels = ndb.TextProperty(required = True) # JSON array
    contacts = ndb.TextProperty(required = True) # JSON array
    connected = ndb.BooleanProperty(default = False)
    def store(self):
        '''Store in memcache and datastore'''
        memcache.set(user_key(self.key.id()), self)
        self.put()
    def get_contact_names(self):
        '''Get the usernames of this user's contacts'''
        # Remove nonexistent contacts
        ##        contactnames = json.loads(self.contacts)
        ##        changed = False
        ##        for contactname in contactnames:
        ##            contact = get_user(contactname)
        ##            if not contact:
        ##                contactnames = [c for c in contactnames if c != contactname]
        ##                changed = True
        ##        if changed:
        ##            self.contacts = json.dumps(contactnames)
        ##            self.store()
        ##        return contactnames
        return json.loads(self.contacts)
    def add_contact(self, contactname):
        '''Add a username to this user's contacts'''
        contacts = json.loads(self.contacts)
        if contactname not in contacts:
            contacts.append(contactname)
            self.contacts = json.dumps(contacts)
            self.store()
    def remove_contact(self, contactname):
        '''Remove a username from this user's contacts'''
        contacts = json.loads(self.contacts)
        if contactname in contacts:
            contacts.remove(contactname) # Should only ever be one contactname
            self.contacts = json.dumps(contacts)
            self.store()
    def get_channel_names(self):
        '''Returns a list of the names of all channels this user is in'''
        return json.loads(self.channels)
    def add_channel(self, channelname):
        '''Adds a channel to this user's channel list'''
        logging.info("user: %s joined channel %s"%(self.username, channelname))
        channels = json.loads(self.channels)
        if channelname not in channels:
            channels.append(channelname)
            self.channels = json.dumps(channels)
            self.store()
    def remove_channel(self, channelname):
        '''Removes a channel from this user's channel list'''
        channels = json.loads(self.channels)
        if channelname in channels:
            channels.remove(channelname)
            self.channels = json.dumps(channels)
            self.store()