#!/usr/bin/python
import json, os, sys

if len(sys.argv) == 2:
	os.chdir(sys.argv[1])
if os.path.isdir('webextension'):
	os.chdir('webextension')
if os.path.isdir('_locales'):
	os.chdir('_locales')

languages = dict()
with open('values') as f:
	strings = json.load(f)

for key, string in strings.items():
	for l in string:
		if l in ['description', 'missing']:
			continue
		if l not in languages:
			languages[l] = {}
		languages[l][key] = {
			'message': string[l],
		}
		if 'description' in string:
			languages[l][key]['description'] = string['description']

for l, data in languages.items():
	with open(os.path.join(l, 'messages.json'), 'w') as f:
		j = json.dumps(data, indent=4, separators=[',', ': '], sort_keys=True, ensure_ascii=False)
		f.write(j.replace('    ', '\t') + '\n')
