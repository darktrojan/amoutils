#!/usr/bin/python
import os, os.path, re
from codecs import open as codecsopen
from xml.sax.saxutils import escape
from parser import getParser, DTDParser, PropertiesParser


def _red(string):
	return '\033[91m%s\033[m' % string


def _green(string):
	return '\033[92m%s\033[m' % string


def _yellow(string):
	return '\033[93m%s\033[m' % string


def _blue(string):
	return '\033[94m%s\033[m' % string


def _purple(string):
	return '\033[95m%s\033[m' % string


def _cyan(string):
	return '\033[96m%s\033[m' % string


if __name__ == '__main__':
	root_dir = os.getcwd()
	locale_dir = os.path.join(root_dir, 'locale')
	base_locale = os.path.join(locale_dir, 'en-US')
	locales = [f for f in os.listdir(locale_dir) if f != 'en-US']
	locales.sort()
	files = [f for f in os.listdir(base_locale)]
	files.sort()

	for string_file in files:
		print _blue(string_file)
		parser = getParser(string_file)
		parser.readFile(os.path.join(base_locale, string_file))
		entities = [e for e in parser]

		for locale in locales:
			added = 0
			same = 0
			translated = 0
			path = os.path.join(locale_dir, locale, string_file)
			if os.path.exists(path):
				parser.readFile(path)
				locale_entities = {e.key: e for e in parser}
			else:
				locale_entities = {}
			output = codecsopen(path, 'w', 'utf-8')

			for entity in entities:
				key = entity.key
				val = entity.val
				locale_val = locale_entities[key].val if key in locale_entities else None

				if locale_val is None:
					added = added + 1
				elif locale_val == val:
					same = same + 1
				else:
					val = locale_val
					translated = translated + 1

				if isinstance(parser, DTDParser):
					output.write('%s%s<!ENTITY %s "%s">%s' % (
						entity.pre_ws, entity.pre_comment, key,
						escape(val, entities={'"': '&quot;'}),
						entity.post
					))
				elif isinstance(parser, PropertiesParser):
					output.write('%s%s%s = %s\n%s' % (
						entity.pre_ws, entity.pre_comment, key,
						val, entity.post
					))

			output.close()
			print _green('%s: %d new, %d same, %d translated' % (locale, added, same, translated))

	with open(os.path.join(root_dir, 'chrome.manifest'), 'r') as manifest:
		manifest_locales = []
		for line in manifest:
			if line[0:6] == 'locale':
				manifest_locales.append(re.split(r'\s+', line)[2])

		for l in locales:
			if l not in manifest_locales:
				print _red('%s directory exists, but is not in chrome.manifest' % l)
		for m in manifest_locales:
			if m != 'en-US' and m not in locales:
				print _red('%s is in chrome.manifest, but no directory exists' % m)
