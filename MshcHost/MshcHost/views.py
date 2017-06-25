"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import Response
from MshcHost import app
from regex import finditer
from MshcHost.index import index as indie
from os import getcwd	
from os.path import join
from MshcHost import cache as path

regex_string = 'href="(ms-xhelp:///\?id=(.*?))"'
current_dir = getcwd()

def _get_file_from_filecache(filename):
	return join(path, filename)

def _file_contents(path):
	with open(path, "rb") as f:
		text = f.read().decode("utf8", "ignore")
		return text

def _perform_transforms(contents):
	matches = finditer(regex_string, contents)
	for match in matches:
		matched_id = match.group(2)
		contents = contents.replace(match.group(1), indie.get(matched_id, "#"))
	contents = contents.replace('rel="styleSheet"', 'rel="stylesheet"')
	return contents

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def main(path):
	if path.endswith(".html"):
		return _perform_transforms(_file_contents(_get_file_from_filecache(path))) 
	elif path.endswith(".css"):
		content = _file_contents(_get_file_from_filecache(path))
		return Response(content, mimetype="text/css")
	else:
		return _file_contents(_get_file_from_filecache(path))