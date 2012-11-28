from web.controllers.BaseHandler import *

class Forbidden(BaseHandler):
    def get(self):
        self.render("forbidden_resource.html")