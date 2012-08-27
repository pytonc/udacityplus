upluschat
=========

Collaborative Social Network Realtime Chat

#Readme
This is a realtime chat server and client designed to run on Google App Engine.
It is part of the collaborative Udacity Plus project.

## Bugs
- privmsg don't show for the sender (not sure whether to implement at client or server level)
  - probably server
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
