#UdacityPlus Chat
This is a realtime chat server and client designed to run on Google App Engine.
This is part of the collaborative Udacity Plus project.

## Bugs
- currently, tabs have the id of the tabname, which could be !server or #channel.
  - this is a problem because $("#channel") won't find
  - have to remove the # or ! for the id field only, and then ensure there are no duplicates
  - OR: find some other way to highlight tabs (e.g. associative array) -- this is probably best

## Todos (not yet implemented features)
- fix bugs
- connect to channel on join
- name changing
- ping/pong/timeouts
- topics, op, voice
- options pane below the chatarea
  - scrolling (to new content): always, never, auto


## Dependencies
### Server
Jinja2
Webapp2
Google AppEngine API

### Client
Twitter Bootstrap
jQuery
