#!/usr/bin/python
import certifi, os, sys, token, urllib3, xpifile

urllib3.disable_warnings()
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

	response = http.request(method, path, headers=headers)

	print response.status
	# print response.getheaders()
	print response.data


# def download(path):
# 	# guid, version = xpifile.get_guid_and_version(path)

# 	method = 'GET'
# 	path = 'https://addons.mozilla.org/api/v3/file/368260/open_with-6.3-sm+tb+fx.xpi?src=api'
# 	headers = {
# 		'Authorization': 'JWT %s' % token.token()
# 	}

# 	response = http.request(method, path, headers=headers)
# 	print response.status
# 	print response.getheaders()


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
		check_status(path)
	# elif sys.argv[1] == 'download':
	# 	download(path)
	else:
		print 'Argument 1 not understood'
		exit(1)
