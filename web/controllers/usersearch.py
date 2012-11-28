from web.util.searching import find_users
import webapp2
import urllib2
import json
import logging


class Search(webapp2.RequestHandler):
    def get(self):
        """Returns a jsonp object containing user search results
        """
        term = urllib2.unquote(self.request.get('q'))
        #TODO: grant access only to queries that provide an API key and originate from a known domain
        api_key = urllib2.unquote(self.request.get('apikey'))

        query = '(tokenized_un:{}) OR (tokenized_rn:{})'.format(term, term)
        logging.info("SEARCH: {}".format(term))
        # match the query only on username or real_name fields
        search_results = find_users(query)
        logging.info("SEARCH - results count: {}".format(search_results.number_found))

        results = {'people': []}

        #TODO: this should be made faster
        for doc in search_results:
            person = {}
            for field in doc.fields:
                if field.name == 'username':
                    person[field.name] = field.value
                if field.name == 'real_name':
                    person[field.name] = field.value
                if field.name == 'avatar_url':
                    person[field.name] = field.value
            results['people'].append(person)

        self.response.out.write("%s(%s)" %
                                (urllib2.unquote(self.request.get('callback')),
                                 json.dumps(results)))