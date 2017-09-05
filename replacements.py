#!/usr/bin/python
# coding=utf-8
import json, math, os, random, sys


def subs(value):
	value = value.replace('$ORIGINAL$', '$1')
	value = value.replace('$VERSION$', '$1')
	value = value.replace('$LOCATION$', '$2')

	n = ''
	i = 0
	while i < len(value):
		c = value[i]
		if c in replacements:
			r = replacements[c]
			p = int(math.floor(random.random() * len(r)))
			n += r[p]
		else:
			n += c
		i += 1
	return n

replacements = {
	'A': u'ÀÁÂÃÄÅĀĂĄ',
	'C': u'ÇĆĈĊČ',
	'E': u'ÈÉÊËĒĔĖĘĚ',
	'I': u'ÌÍÎÏĨĪĬĮI',
	'L': u'ĹĻĽĿŁ',
	'N': u'ÑŃŅŇŊ',
	'O': u'ÒÓÔÕÖØŌŎŐ',
	'U': u'ÙÚÛÜŨŪŬŮŰŲ',
	'a': u'àáâãäåāăą',
	'c': u'çćĉċč',
	'e': u'èéêëēĕėęě',
	'i': u'ìíîïĩīĭįı',
	'l': u'ĺļľŀł',
	'n': u'ñńņňŉŋ',
	'o': u'òóôõöøōŏő',
	'u': u'ùúûüũūŭůűų'
}

if __name__ == '__main__':
	if len(sys.argv) == 2:
		os.chdir(sys.argv[1])
	if os.path.isdir('webextension'):
		os.chdir('webextension')
	if os.path.isdir('_locales'):
		os.chdir('_locales')

	with open('en/messages.json') as f:
		j = json.load(f)

	a = {}
	for k, v in j.iteritems():
		a[k] = {
			'message': subs(v['message'])
		}

	if not os.path.isdir('xyz'):
		os.mkdir('xyz')
	with open('xyz/messages.json', 'w') as f:
		json.dump(a, f, sort_keys=True, indent=4, separators=(',', ': '))
