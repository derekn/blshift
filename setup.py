from setuptools import find_packages, setup

about = {}
with open('blshift/__version__.py') as fp:
	exec(fp.read(), about)

setup(
	name='blshift',
	description='Borderlands Shift code automated redeemer',
	version=about['__version__'],
	author='Derek Nicol',
	author_email='1420397+derekn@users.noreply.github.com',
	url='https://github.com/derekn/blshift.git',
	license=about['__license__'],
	packages=find_packages(),
	python_requires='>=3.7.0',
	install_requires=[
		'requests',
		'simplejson',
		'click'
	],
	scripts=['bin/blshift']
)
