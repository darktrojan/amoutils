#!/usr/bin/python
import os, os.path, sys
from codecs import open as codecsopen
from xml.sax.saxutils import escape
from Parser import getParser, DTDParser, PropertiesParser


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


def check(root_dir):
	base_locale = os.path.join(root_dir, 'en-US')
	locales = [f for f in os.listdir(root_dir) if f != 'en-US']
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
			path = os.path.join(root_dir, locale, string_file)
			if os.path.exists(path):
				parser.readFile(path)
				locale_entities = {e.get_key(): e for e in parser}
			else:
				locale_entities = {}
			output = codecsopen(path, 'w', 'utf-8')

			for entity in entities:
				key = entity.get_key()
				val = entity.get_val()
				locale_val = locale_entities[key].get_val() if key in locale_entities else None

				if locale_val is None:
					added = added + 1
				elif locale_val == val:
					same = same + 1
				else:
					val = locale_val
					translated = translated + 1

				if isinstance(parser, DTDParser):
					output.write('%s%s<!ENTITY %s "%s">%s' % (
						entity.get_pre_ws(), entity.get_pre_comment(), key,
						escape(val, entities={'"': '&quot;'}),
						entity.get_post()
					))
				elif isinstance(parser, PropertiesParser):
					output.write('%s%s%s = %s\n%s' % (
						entity.get_pre_ws(), entity.get_pre_comment(), key,
						val, entity.get_post()
					))

			output.close()
			print _green('%s: %d new, %d same, %d translated' % (locale, added, same, translated))

if __name__ == '__main__':
	root_dir = os.getcwd()
	if len(sys.argv) == 2:
		root_dir = os.path.join(root_dir, sys.argv[1])

	check(root_dir)
