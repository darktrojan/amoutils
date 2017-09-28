#!/usr/bin/python
import json, os, sys

if len(sys.argv) == 2:
	os.chdir(sys.argv[1])
if os.path.isdir('webextension'):
	os.chdir('webextension')
if os.path.isdir('_locales'):
	os.chdir('_locales')

languages = dict()
strings = dict()
for l in os.listdir('.'):
	if os.path.isdir(l):
		languages[l] = 0
		with open(os.path.join(l, 'messages.json')) as f:
			j = json.load(f)
			for s in j:
				if s not in strings:
					strings[s] = dict()
				strings[s][l] = j[s]['message']
				languages[l] += 1

for s in strings:
	for l in languages:
		if l not in strings[s]:
			if 'missing' not in strings[s]:
				strings[s]['missing'] = list()
			strings[s]['missing'].append(l)

with open('values', 'w') as f:
	json.dump(strings, f, sort_keys=True, indent=4, separators=(',', ': '))

for l in sorted(languages, key=lambda l: languages[l], reverse=True):
	percent = float(languages[l]) / len(strings) * 100
	print '\033[9%dm%-5s %3d/%3d %3d%%\033[m' % (
		2 if percent > 90 else 3 if percent > 66.66 else 1, l, languages[l], len(strings), percent
	)
