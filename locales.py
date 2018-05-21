#!/usr/bin/python
import io, json, os

os.chdir('webextension/_locales')
for l in os.listdir('.'):
	if not os.path.isdir(l):
		continue

	p = os.path.join(l, 'messages.json')
	with open(p) as f:
		j = json.load(f)

	with io.open(p, 'w', encoding='utf-8') as f:
		s = json.dumps(j, sort_keys=True, indent=4, separators=[',', ': '], ensure_ascii=False, encoding='utf-8')
		f.write(unicode(s.replace('    ', '\t') + '\n'))
