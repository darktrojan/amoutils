#!/usr/bin/python
import fnmatch, os, sys, zipfile
from xml.dom.minidom import parse, parseString


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


def get_guid_and_version(path):
	if path.endswith('.xpi'):
		with zipfile.ZipFile(path, 'r') as z:
			i = z.read('install.rdf')
			x = parseString(i)
	elif not os.path.exists(os.path.join(path, 'install.rdf')):
		raise Exception('omg wtf')
	else:
		with open(os.path.join(path, 'install.rdf'), 'r') as f:
			x = parse(f)

	guid = str(x.getElementsByTagName('em:id')[0].firstChild.data.strip())
	version = str(x.getElementsByTagName('em:version')[0].firstChild.data.strip())

	return guid, version


def get_xpi_filename(path):
	return '%s-%s.xpi' % get_guid_and_version(path)


def package(basepath):
	excluded_files = [
		'*.list',
		'*.xpi',
		'*.zip',
		'.git',
		'.gitignore',
		'.hg',
		'.hgignore',
		'.hgtags',
		'.jscsrc',
		'.jshintrc',
		'.xpiignore',
	]
	included_files = None
	zipped_files = []

	def is_excluded(path):
		if path in excluded_files:
			return True
		for e in excluded_files:
			if fnmatch.fnmatch(path, e):
				return True
		return False

	def is_included(path):
		if included_files is None or path in included_files:
			return True
		for i in included_files:
			if i.endswith('/*') and path.startswith(i[:-2]):
				return True
		return False

	def package_directory(path):
		for p in sorted(os.listdir(path)):
			if is_excluded(p):
				print _yellow('%s skipped' % p)
				continue
			f = os.path.join(path, p)
			r = os.path.relpath(f, basepath)
			if is_excluded(r):
				print _yellow('%s skipped' % r)
				continue
			if is_included(r):
				print r
				zipped_files.append(r)
				z.write(f, r)
				if os.path.isdir(f):
					package_directory(f)
			else:
				print _red('%s not included' % p)

	if os.path.exists(os.path.join(basepath, '.xpiignore')):
		with open(os.path.join(basepath, '.xpiignore'), 'r') as f:
			for l in f:
				excluded_files.append(l.strip())

	if os.path.exists(os.path.join(basepath, 'xpi.list')):
		with open(os.path.join(basepath, 'xpi.list'), 'r') as f:
			included_files = []
			for l in f:
				included_files.append(l.strip())

	z = zipfile.ZipFile(os.path.join(basepath, get_xpi_filename(basepath)), 'w', zipfile.ZIP_DEFLATED)
	package_directory(basepath)
	z.close()

	if included_files is not None:
		for i in included_files:
			if not i.endswith('/*') and i not in zipped_files:
				print _red('%s missing' % i)


if __name__ == '__main__':
	path = os.getcwd()
	if len(sys.argv) > 1:
		path = os.path.join(path, sys.argv[1])

	package(path)
