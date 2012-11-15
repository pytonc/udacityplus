from google.appengine.api.app_identity import get_default_version_hostname
from google.appengine.api import mail
from google.appengine.api import memcache
from hashlib import sha1
from settings import MSG_NOTIFY_EMAIL_DISP

def create_new_user_confirmation(baseurl):
    token = sha1.hexdigest()
#    memcache.add()


def new_message_notify(email, conv_id, message):
#    url = uri_for('messages', conv_id, message.key.id())
    host = get_default_version_hostname()
    url = "/".join([host, 'messages', str(conv_id),str(message.key.id())])

    if not mail.is_email_valid(email):
        return None
    else:

        sender_address = MSG_NOTIFY_EMAIL_DISP
        subject = "You have a new message from %s" % message.sender
        body = """
        %s

        ------
        To view the message, go to:
        %s
        """ % (message.content, url)

        mail.send_mail(sender_address, email, subject, body)