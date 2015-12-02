#!/usr/bin/python
import json, os
from urllib2 import urlopen
from xml.dom.minidom import parse

total_downloads = 0
total_users = 0

with open(os.path.join(os.path.dirname(__file__), '.amorc'), 'r') as f:
	j = json.load(f)

for slug in sorted(j['repos'].values()):
	u = urlopen('https://services.addons.mozilla.org/en-US/firefox/api/1.5/addon/%s' % slug)
	d = parse(u)

	downloads = int(d.getElementsByTagName('total_downloads')[0].firstChild.data)
	users = int(d.getElementsByTagName('daily_users')[0].firstChild.data)

	total_downloads = total_downloads + downloads
	total_users = total_users + users

	print '%s: %d downloads, %d users' % (slug, downloads, users)

print 'Total: %d downloads, %d users' % (total_downloads, total_users)
