from web.models.User import User
from boilerplate.handlers import BaseHandler

class RPCPage(BaseHandler):
	
	def get(self):
		username, email = self.get_params(["username", "email"])
		if username:
			self.checkUsernameAvailability(username)
		elif email:
			self.checkEmailAvailability(email)

	def checkUsernameAvailability(self, username):
		users = User.get_user(username)
		self.response.out.write(users != None)

	def checkEmailAvailability(self, email):
		emails = User.gql("WHERE email=:1", email).get()
		self.response.out.write(emails != None)