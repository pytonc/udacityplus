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

from boilerplate.lib.basehandler import BaseHandler as bh

class BaseHandler(bh):
    def get_params(self, params):
        return [self.request.get(param) for param in params]

    def get_params_dict(self, params):
        return {param : self.request.get(param) for param in params}
