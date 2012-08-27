upluschat
=========

Collaborative Social Network Realtime Chat

#Readme
This is a realtime chat server and client designed to run on Google App Engine.
It is part of the collaborative Udacity Plus project.

## Bugs
- the Channel will expire after 2 hours, must add a reconnect feature

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
