from boilerplate.handlers import BaseHandler

class Forbidden(BaseHandler):
    def get(self):
        self.render_template("forbidden_resource.html")