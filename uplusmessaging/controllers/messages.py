from BaseHandler import *
from controllers.authentication import Authentication


class MessagePage(BaseHandler):
    
    @Authentication.do
    def get(self):
        self.response.out.write("Hello World")