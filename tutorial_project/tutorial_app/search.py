import json
import urllib, urllib2
import os

BING_API_KEY= os.enviorn.get('BING_API_KEY')

def run_query(search_terms):
	root_url = 'https://api.datamarket.azure.com/Bing/Search/'
	source = 'Web'
	results_per_page = 10
	offset = 0
	query = "'{0}'".format(search_terms)
	query = urllib.quote(query)


	search_url = "{0}{1}?$format=json&$top={2}&$skip={3}&Query={4}".format(
		root_url,
		source,
		results_per_page,
		offset,
		query)

	username = ''
	password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
	password_mgr.add_password(None, search_url, username, BING_API_KEY)
	results = []

	try:
		# Prepare for connecting to Bing's servers.\
		handler = urllib2.HTTPBasicAuthHandler(password_mgr)
		opener = urllib2.build_opener(handler)
		urllib2.install_opener(opener)

		# Connect to the server and read the response generated.
		response = urllib2.urlopen(search_url).read()

		# Convert the string response to a Python dictionary object.
		json_response = json.loads(response)

		# Loop through each page returned, populating out results list.
		for result in json_response['d']['results']:
			results.append({
				'title': result['Title'],
				'link': result['Url'],
				'summary': result['Description']})

	except urllib2.URLError as e:
			print "Error when querying the Bng API: ", e

	return results