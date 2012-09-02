from google.appengine.ext import db

class Message(db.Model):
    sender    = db.StringProperty(required=True)
    receiver  = db.StringProperty(required=True)
    title     = db.StringProperty(required=True)
    content   = db.TextProperty(required=True)
    timestamp = db.DateTimeProperty(auto_now_add=True)

    @staticmethod
    def received(username):
        return Message.gql("WHERE receiver=:1", username)

    @staticmethod
    def sent(username):
        return Message.gql("WHERE sender=:1", username)


