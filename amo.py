#!/usr/bin/python
import certifi, httplib, json, os, sys, token, urllib3, xpifile

http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())


def upload(filepath):
	if not filepath.endswith('.xpi'):
		print 'Refusing to upload a non-xpi'
		exit(1)

	guid, version = xpifile.get_guid_and_version(filepath)

	method = 'PUT'
	path = 'https://addons.mozilla.org/api/v3/addons/%s/versions/%s/' % (guid, version)
	headers = {
		'Authorization': 'JWT %s' % token.token()
	}
	fields = {
		'upload': (os.path.basename(filepath), open(filepath, 'rb').read())
	}

	# print method
	# print path
	# print headers
	# return

	response = http.request_encode_body(method, path, headers=headers, fields=fields)

	print response.status
	# print response.getheaders()
	print response.data


def check_status(filepath):
	guid, version = xpifile.get_guid_and_version(filepath)

	method = 'GET'
	path = 'https://addons.mozilla.org/api/v3/addons/%s/versions/%s/' % (guid, version)
	headers = {
		'Authorization': 'JWT %s' % token.token()
	}

	# print path
	# print headers

	return http.request(method, path, headers=headers)


def download(filepath):
	response = check_status(filepath)
	if response.status != httplib.OK:
		print response.status
		print response.data
		exit(1)

	method = 'GET'
	path = json.loads(response.data)['files'][0]['download_url']
	headers = {
		'Authorization': 'JWT %s' % token.token()
	}

	response = http.request(method, path, headers=headers)
	print response.status
	print response.getheaders()
	with open(os.path.basename(path).replace('?src=api', ''), 'wb') as f:
		f.write(response.data)


def relnotes(filepath):
	(guid, version,) = xpifile.get_guid_and_version(filepath)
	stub = xpifile.get_amo_stub(guid)

	path = 'https://addons.mozilla.org/api/v3/addons/addon/%s/versions/' % stub
	response = http.request('GET', path)
	for result in json.loads(response.data)['results']:
		if result['version'] == version:
			print result['edit_url']
			return


if __name__ == '__main__':
	path = os.getcwd()
	if len(sys.argv) < 2:
		print 'Not enough arguments'
		exit(1)
	elif len(sys.argv) == 3:
		path = os.path.join(path, sys.argv[2])

	if sys.argv[1] == 'upload':
		upload(path)
	elif sys.argv[1] == 'check':
		response = check_status(path)
		print response.status
		print response.data
	elif sys.argv[1] == 'download':
		download(path)
	elif sys.argv[1] == 'relnotes':
		relnotes(path)
	else:
		print 'Argument 1 not understood'
		exit(1)
