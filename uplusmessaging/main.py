import webapp2
from controllers.home      import HomePage
from controllers.signup    import SignUpPage
from controllers.login     import LoginPage
from controllers.logout    import LogoutPage
from controllers.forbidden import Forbidden
from controllers.messages  import MessagePage
from controllers.RPC       import RPCPage

app = webapp2.WSGIApplication([
        ('/', HomePage),
        ('/signup', SignUpPage),
        ('/login', LoginPage),
        ('/logout', LogoutPage),
        ('/forbidden', Forbidden),
        ('/rpc', RPCPage),
        ('/messages.*', MessagePage)
    ], debug=True)

