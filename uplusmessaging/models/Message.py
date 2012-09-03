from google.appengine.ext import db

class Message(db.Model):
    sender    = db.StringProperty(required=True)
    receiver  = db.StringProperty(required=True)
    title     = db.StringProperty(required=True)
    content   = db.TextProperty(required=True)
    timestamp = db.DateTimeProperty(auto_now_add=True)

    @staticmethod
    def received(username, offset, limit):
        return Message.fetch_messages("receiver", username, offset, limit)

    @staticmethod
    def sent(username, offset, limit):
        return Message.fetch_messages("sender", username, offset, limit)

    @staticmethod
    def fetch_messages(role, username, offset, limit):
        # if you change difference between offset and limit here 
        # do the same in temp.js in function getPreviousMessages
        offset = offset or 0
        limit  = limit  or 10
        offset, limit = int(offset), int(limit)
        q = db.Query(Message)
        q.filter(role, username)
        q.order("-timestamp")
        return q.fetch(offset=offset, limit=limit)
