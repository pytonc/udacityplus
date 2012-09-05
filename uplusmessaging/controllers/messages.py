from BaseHandler import *
from controllers.authentication import Authentication
from models.Message import *
from datetime import datetime

class MessagePage(BaseHandler):
    
    @Authentication.do
    def get(self):
        self.render('messages.html')
    def post(self):
    	message, recipient = self.get_params(['message','recipient'])
    	sender = self.request.cookies.get('username')
    	message = scrub_HTML(message)

    	m_db = Message(sender=sender, recipient=recipient, message=message)
    	m_db.put()

    	date = datetime.now()
    	self.render('message_val.html', {'recipient':recipient, 'message':message, 'date':date})