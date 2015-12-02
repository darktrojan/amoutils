#!/usr/bin/python
import json, jwt, os, random, time


def token():
	with open(os.path.join(os.path.dirname(__file__), '.amorc'), 'r') as f:
		j = json.load(f)
		user = j['user']
		secret = j['secret']

	issuedAt = int(time.time())
	payload = {
		'iss': user,
		'jti': random.random(),
		'iat': issuedAt,
		'exp': issuedAt + 60,
	}

	return jwt.encode(payload, secret, algorithm='HS256')

if __name__ == '__main__':
	print token()
