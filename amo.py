#!/usr/bin/python
import argparse, certifi, httplib, json, os, token, urllib3, xpifile

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
	parser = argparse.ArgumentParser()
	parser.add_argument('action', choices=('upload', 'check', 'download', 'relnotes',))
	parser.add_argument('path', nargs='?')
	args = parser.parse_args()

	path = os.getcwd()
	if args.path is not None:
		path = os.path.join(path, args.path)

	if args.action == 'upload':
		upload(path)
	elif args.action == 'check':
		response = check_status(path)
		print response.status
		print response.data
	elif args.action == 'download':
		download(path)
	elif args.action == 'relnotes':
		relnotes(path)
