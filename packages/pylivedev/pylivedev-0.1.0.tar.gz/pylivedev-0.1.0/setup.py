from setuptools import setup

setup(
	name='pylivedev',
	version='0.1.0',
	url='https://github.com/ouroboroscoding/pylivedev',
	description='PyLiveDev is used to keep track of files associated with your script so it can be re-started if any file is updated.',
	keywords=['python','live', 'development'],
	author='Chris Nasr - OuroborosCoding',
	author_email='chris@ouroboroscoding.com',
	license='Apache-2.0',
	packages=['pylivedev'],
	install_requires=[
		'watchdog>=2.1.2'
	],
	entry_points={
		'console_scripts': ['pylivedev=pylivedev.__main__:cli']
	},
	zip_safe=True
)
