#!/usr/bin/python
import argparse, fnmatch, json, os, subprocess, zipfile
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
	def parse_xml(x):
		guid = str(x.getElementsByTagName('em:id')[0].firstChild.data.strip())
		version = str(x.getElementsByTagName('em:version')[0].firstChild.data.strip())
		return guid, version

	def parse_json(j):
		o = json.loads(j)
		if 'applications' in o:
			guid = str(o['applications']['gecko']['id'])
		else:
			path_parts = path.split('/')
			if 'betterimageviewer' in path_parts:
				guid = 'betterimageviewer@darktrojan.net'
			if 'openwith' in path_parts:
				guid = 'openwith@darktrojan.net'
			if 'newtabtools' in path_parts:
				guid = 'newtabtools@darktrojan.net'
		version = str(o['version'])
		return guid, version

	if path.endswith('.xpi'):
		with zipfile.ZipFile(path, 'r') as z:
			if 'install.rdf' in z.namelist():
				i = z.read('install.rdf')
				x = parseString(i)
				return parse_xml(x)
			j = z.read('manifest.json')
			return parse_json(j)
	elif os.path.exists(os.path.join(path, 'install.rdf')):
		with open(os.path.join(path, 'install.rdf'), 'r') as f:
			x = parse(f)
			return parse_xml(x)
	elif os.path.exists(os.path.join(path, 'manifest.json')):
		with open(os.path.join(path, 'manifest.json'), 'r') as f:
			j = f.read()
			return parse_json(j)
	else:
		raise Exception('omg wtf')


def get_amo_stub(guid):
	with open(os.path.join(os.path.dirname(__file__), '.amorc'), 'r') as f:
		j = json.load(f)
	return j['slugs'][guid]


def package(basepath):
	excluded_files = [
		'*.list',
		'*.xpi',
		'*.zip',
		'.eslintrc',
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
			if i.endswith('/*') and (path == i[:-2] or path.startswith(i[:-1])):
				return True
		return False

	def package_directory(path):
		for p in sorted(os.listdir(path)):
			f = os.path.join(path, p)
			r = os.path.relpath(f, basepath)
			if is_excluded(p):
				print _yellow('%s skipped' % r)
				continue
			if is_excluded(r):
				print _yellow('%s skipped' % r)
				continue
			if is_included(r):
				# print r
				zipped_files.append(r)
				z.write(f, r)
				if os.path.isdir(f):
					package_directory(f)
			else:
				print _red('%s not included' % r)

	if os.path.exists(os.path.join(basepath, '.xpiignore')):
		with open(os.path.join(basepath, '.xpiignore'), 'r') as f:
			for l in f:
				excluded_files.append(l.strip())

	if os.path.exists(os.path.join(basepath, 'xpi.list')):
		with open(os.path.join(basepath, 'xpi.list'), 'r') as f:
			included_files = []
			for l in f:
				included_files.append(l.strip())

	if os.path.isdir(os.path.join(basepath, '.git')):
		branches = subprocess.check_output(['git', 'branch']).splitlines()
		for b in branches:
			if b[0] == '*':
				branch = b[2:]

		if args.chrome:
			if branch != 'chrome':
				print _red('WARNING: not on the chrome branch')
				print
			zipfile_name = '%s-%s_chrome.zip'
		elif args.opera:
			if branch != 'opera':
				print _red('WARNING: not on the opera branch')
				print
			zipfile_name = '%s-%s_opera.zip'
		else:
			if branch != 'master':
				print _red('WARNING: not on the master branch')
				print
			zipfile_name = '%s-%s.xpi'
	else:
		zipfile_name = '%s-%s.xpi'

	zipfile_name = os.path.join(os.getcwd(), zipfile_name % get_guid_and_version(basepath))
	z = zipfile.ZipFile(zipfile_name, 'w', zipfile.ZIP_DEFLATED)
	package_directory(basepath)
	z.close()

	if included_files is not None:
		for i in included_files:
			if not i.endswith('/*') and i not in zipped_files:
				print _red('%s missing' % i)

	if not args.lint or subprocess.call(['addons-linter', zipfile_name]) == 0:
		print ''
		print _green('Created ' + os.path.relpath(zipfile_name, os.getcwd()))
	else:
		print ''
		print _red('Failed linting')

args = None

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--lint', action='store_true')
	parser.add_argument('--chrome', action='store_true')
	parser.add_argument('--opera', action='store_true')
	parser.add_argument('path', nargs='?')
	args = parser.parse_args()

	path = os.getcwd()
	if args.path is None:
		if not os.path.exists('install.rdf') and os.path.exists('webextension'):
			path = os.path.join(path, 'webextension')
	else:
		path = os.path.join(path, args.path)

	package(path)
