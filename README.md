upluschat
=========

Collaborative Social Network Realtime Chat

#Readme
This is a realtime chat server and client designed to run on Google App Engine.
It is part of the collaborative Udacity Plus project.

## Bugs
- privmsg doesn't show for the sender (not sure whether to implement at client or server level)
  - probably server
- need to find a way to clear user after a certain amount of time if they did not connect (but did log in)
  - maybe at the login phase, check if user exists (if they are not connected and session is X seconds old, delete the old user)
- remove arguments from XHR post (use jQuery's .ajax() function)
- the Channel will expire after 2 hours, must add a reconnect feature
- check syntax/format compliance on server side (yawn)

## Todos (not yet implemented features)
- fix bugs
- connect to channel on join
- name changing
- ping/pong/timeouts
- UI option to close tabs for users/channels
- topics, op, voice
- options pane below the chatarea
  - scrolling (to new content): always, never, auto


## Dependencies
### Server
- Jinja2
- Webapp2
- Google AppEngine API

### Client
- Twitter Bootstrap
- jQuery
