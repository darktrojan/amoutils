import json, os

strings = dict()
for l in os.listdir('.'):
	if os.path.isdir(l):
		with open(os.path.join(l, 'messages.json')) as f:
			j = json.load(f)
			for s in j:
				if s not in strings:
					strings[s] = dict()
				strings[s][l] = j[s]['message']

with open('values', 'w') as f:
	json.dump(strings, f, sort_keys=True, indent=4, separators=(',', ': '))
