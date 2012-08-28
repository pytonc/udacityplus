import webapp2
import jinja2
import os

# Basic webapp2 handler with some useful methods
#
# render(template_name, template_vals={})
# - template needs to be in template dir
#
#
# WORKING WITH COOKIES
#
# set_cookie(name, value)
# set_cookies({name1:value1, name2:value2})
# get_cookie(name)
# get_cookies([name1, name2...])      - return [value1, value2...]
# get_cookies_dict([name1, name2...]) - return {name1:value1, name2:value2}
#
#
# RETRIVING REQUEST PARAMS
#
# get_params([param1, param2...])      - return [value1, value2...]
# get_params_dict([param1, param2...]) - return {param1:value1, param2:value2}


head, tail   = os.path.split(os.path.dirname(__file__))
template_dir = os.path.join(head, "templates")

jinja_environment=jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir), autoescape=True)

class BaseHandler(webapp2.RequestHandler):
    def render(self, template, vals={}):
        template = jinja_environment.get_template("%s" % template)
        self.response.out.write(template.render(vals))

    def set_cookie(self, name, value):
        name, value = str(name), str(value)
        self.response.headers.add_header('Set-Cookie', '%s=%s' % (name, value))

    def set_cookies(self, pairs):
        for k, v in pairs.iteritems():
            self.set_cookie(k, v)

    def get_cookie(self, name):
        return self.request.cookies.get(name)

    def get_cookies(self, names):
        return [self.get_cookie(name) for name in names]

    def get_cookies_dict(self, names):
        return {name:self.get_cookie(name) for name in names}

    def get_params(self, params):
        return [self.request.get(param) for param in params]

    def get_params_dict(self, params):
        return {param : self.request.get(param) for param in params}