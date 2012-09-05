from google.appengine.ext import db
from bs4 import BeautifulSoup

VALID_TAGS = ['strong', 'em', 'u', 'ul', 'ol', 'li', 'blockquote', 'a', 'img', 'code']

def scrub_HTML(html):
	soup = BeautifulSoup(html)
	for tag in soup.findAll(True):
		if tag.name not in VALID_TAGS:
			tag.hidden = True

	return soup.renderContents()

class Message(db.Model):
	sender = db.StringProperty(required=True)
	recipient = db.StringProperty(required=True)
	message = db.TextProperty(required = True)
	date_sent = db.DateTimeProperty(auto_now_add = True)
	# read = db.BooleanProperty(required=True)
	

