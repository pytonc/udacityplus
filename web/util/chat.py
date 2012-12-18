__author__ = "rrandom, Jin Koo, Anthony, Jan Zegan"

import logging
import re
import json
from google.appengine.api import channel as channel_api # 'channel' is kind of ambiguous in context
from google.appengine.api import memcache
from web.models.ChatChannel import ChatChannel
from web.models.ChatUser import ChatUser


def user_join(username, channelname):
    user = get_user(username)
    username = user.username # Use actual name
    channel = get_channel(channelname)
    if not channel:
        if channelname and not re.compile(r'^#[\w]{3,20}$').match(channelname):
            channelerror="Channel must consist of 3-20 alpha_numeric characters and start with a #"
            channel_api.send_message(username, "NOTICE "+channelerror)
            return
        channel = ChatChannel(id=channelname,
            channelname=channelname,
            users=json.dumps([ ])
        )
    channelname = channel.channelname # Use actual name
    channel.add_user(username)
    user.add_channel(channelname)
    userlist = ' '.join(channel.get_user_names())
    channel_api.send_message(username, "USERS "+channelname+" "+userlist) # Tell the user who is in the channel
    for u in channel.get_user_names():
        # Tell the individual channel members that the new user joined
        channel_api.send_message(u, "JOINED "+username+" "+channelname)
    logging.warning("End of JOIN, %s's channels are: "%username+', '.join(get_user(username).get_channel_names()))

def user_leave(username, channelname):
    user = get_user(username)
    username = user.username # Use actual name
    channel = get_channel(channelname)
    channelname = channel.channelname # Use actual name
    channel.remove_user(username)
    # Do we inform the user they have successfully left?
    # If we do, then that may cause a closed tab to reopen, better for client to handle that
    for u in channel.get_user_names():
        channel_api.send_message(u, "LEFT "+username+" "+channelname)

def user_quit(username, args):
    '''User has quit'''
    # This may take a while to execute
    user = get_user(username)
    username = user.username # Use actual name
    user.connected = False
    for channelname in user.get_channel_names():
        # Remove the user from channel
        channel = get_channel(channelname)
        channel.remove_user(username) # Do this first to prevent infinite loops
        for u in channel.get_user_names():
            # Let the people in the channel know
            channel_api.send_message(u, "QUIT "+username+" "+channelname)
    for contactname in user.get_contact_names():
        # Remove user from their contacts' contact lists
        # Possible double-handling, but that's ok because remove_contact checks for that
        contact = get_user(contactname)
        if contact:
            contact.remove_contact(username)
    try:
        channel_api.send_message(username, "NOTICE You have quit")
    except:
        # POKEMON exception!
        # Not really needed since send_message does not throw exceptions
        pass
    user.store()
    # Let the disconnect handler deal with clearing the user object

def user_privmsg(username, args):
    '''Private message from one user to another'''
    recipientname = args.split(' ')[0]
    message = args[args.index(' ')+1:]
    recipient = get_user(recipientname)
    user = get_user(username)
    username = user.username # Use actual name
    if recipient and user:
        recipientname = recipient.username # Use actual name
        channel_api.send_message(recipientname, "PRIVMSG "+username+" "+message)
        channel_api.send_message(username, "SENTMSG "+recipientname+" "+message)
        # Add sender and recipient to each other's contact lists to inform of e.g. quittage
        recipient.add_contact(username)
        user.add_contact(recipientname)
    else:
        channel_api.send_message(username, "NOTICE "+recipientname+" is not a valid user. Maybe they disconnected "+
                                           "or maybe you need to check your spelling")

def user_channelmsg(username, args):
    channelname = args.split(' ')[0]
    message = args[args.index(' ')+1:]
    channel = get_channel(channelname)
    user = get_user(username)
    username = user.username # Use actual name
    channelname = channel.channelname # Use actual name
    if channel and username in channel.get_user_names():
        for u in channel.get_user_names():
            # Send message to all the users in the channel
            channel_api.send_message(u, "CHANNELMSG "+channelname+" "+username+" "+message)
    else:
        channel_api.send_message(username, "NOTICE "+channelname+" does not appear to be a channel "+
                                           "(or it is a channel, and you're not in it, somehow).")

def user_ping(username, args):
    user = get_user(username)
    username = user.username # Use actual name
    channel_api.send_message(username, "PONG "+args)

def user_pong(username, args):
    # Do nothing, since we have not yet implemented PING/PONG
    pass

def user_key(username):
    '''user_key function is for key consistency'''
    return "user/"+username

def get_user(username):
    '''Get a user from memcache or datastore, returns None if user does not exist'''
    key = user_key(username)
    user = memcache.get(key)
    if not user:
        user = ChatUser.get_by_id(username)
        if user:
            memcache.set(key, user)
        else:
            memcache.set(key, "placeholder to reduce memcache misses")
    if isinstance(user, ChatUser):
        return user

def clear_user(username):
    '''Removes a user from datastore and from memcache'''
    user = get_user(username)
    if user:
        user.key.delete()
        memcache.set(user_key(username), "placeholder to reduce memcache misses")
        logging.info("Removed "+username)

def channel_key(channelname):
    '''For consistency'''
    return "channel/"+channelname

def get_channel(channelname):
    '''Get a channel from memcache or datastore, returns None if channel does not exist'''
    key = channel_key(channelname)
    channel = memcache.get(key)
    if not channel:
        channel = ChatChannel.get_by_id(channelname)
        if channel:
            memcache.set(key, channel)
        else:
            memcache.set(key, "placeholder to reduce memcache misses")
    if isinstance(channel, ChatChannel):
        return channel

def clear_channel(channelname):
    '''Removes a channel from datastore and from memcache'''
    channel = get_channel(channelname)
    if channel:
        channel.key.delete()
        memcache.set(channel_key(channelname), "placeholder to reduce memcache misses")
