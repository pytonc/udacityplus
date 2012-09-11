from google.appengine.ext import db


class Message(db.Model):
    # TODO: does receivers here badly affect performance?
    receivers   = db.StringListProperty(required=True)
    sender      = db.StringProperty(required=True)
    title       = db.StringProperty(required=True)
    content     = db.TextProperty(required=True)
    timestamp   = db.DateTimeProperty(auto_now_add=True)

    @staticmethod
    def received(username, offset, limit):
        offset = offset or 0
        limit  = limit  or 10
        offset, limit = int(offset), int(limit)

        keys = db.GqlQuery(
            "SELECT __key__ FROM MessageIndex WHERE receivers = :1", username
        ).fetch(limit, offset)
        return db.get([k.parent() for k in keys])

    @staticmethod
    def sent(username, offset, limit):
        offset = offset or 0
        limit  = limit  or 10
        offset, limit = int(offset), int(limit)
        q = db.Query(Message)
        q.filter('sender', username)
        q.order("-timestamp")
        return q.fetch(offset=offset, limit=limit)

class MessageIndex(db.Model):
    receivers   = db.StringListProperty(required=True)
