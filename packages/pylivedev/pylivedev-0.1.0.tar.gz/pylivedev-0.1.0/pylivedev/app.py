# coding=utf8
""" App

Handles the class passed around with all data related to a single script
"""

__author__		= "Chris Nasr"
__copyright__	= "Ouroboros Coding Inc."
__version__		= "1.0.0"
__email__		= "chris@ouroboroscoding.com"
__created__		= "2021-06-05"

# Python imports
import os
import subprocess
import sys

# Pip imports
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Local imports
from . import imports

class App(FileSystemEventHandler):
	"""App

	class to hold all relevant data for running a single application

	Extends
		object
	"""

	def __init__(self, name, command, \
					additional_files=None, arguments=None, mode=None, \
					python=None, unbuffered=True, verbose=False):
		"""Constructor

		Handles instantiating the App instance

		Arguments:
			name (str): The name of the app
			command (str): The command to run to start the script
			additional_files (str[]): Additional files to watch that aren't python imports
			arguments (str[]): Additional arguments to pass to the script
			mode (str): The mode of script, 'script' or 'module'
			python (str): The full path to the python to use
			unbuffered (bool): If true, script will run in unbuffered mode for stdout/stderr
			verbose (bool): If true, additional data will be displayed when running script

		Returns:
			App
		"""

		# Init configurable members
		self._name = name
		self._command = command
		self._additional_files = additional_files
		self._arguments = arguments
		self._mode = mode and mode or 'script'
		self._python = python or sys.executable
		self._unbuffered = unbuffered
		self._verbose = verbose

		# Init internal members
		self._files = []
		self._fresh_line = True

		# Create a new observer
		self._observer = Observer()
		self._observer.start()

		# Generate the arguments to run the script/module
		self._generate_args()

	def __del__(self):
		"""Deconstructor

		Cleans up after the instance

		Returns
			None
		"""

		# Stop the observer
		if self._observer:
			self._observer.stop()
			self._observer.join()
			del self._observer

	def _generate_args(self):
		"""Generate Args

		Private method to generate the full list of arguments based on the data
		associated with the app

		Returns:
			None
		"""

		# Init the list with the python executable
		self._args = [self._python]

		# If we are running unbuffered
		if self._unbuffered:
			self._args.append('-u')

		# If we are running a module
		if self._mode == 'module':
			self._args.append('-m')

		# Add the script/module
		self._args.append(self._command)

		# If there's additional arguments to the script
		if self._arguments and isinstance(self._arguments, list):
			self._args.extend(self._arguments)

		# If verbose, display list of arguments
		if self._verbose:
			print('The following args were generated: %s' % str(self._args))

	def dispatch(self, event):
		"""Dispatch

		Called whenever there's an event on any of the watched files

		Returns:
			None
		"""

		# If it's a modified file and it's in our list
		if not event.is_directory and \
			event.event_type == 'modified' and \
			event.src_path in self._files:

			# If verbose mode is on, notify of a file change
			if self._verbose:
				print('%s has been modified' % event.src_path)

			# Stop the app
			self.stop()

			# Start the app
			self.start()

	def join(self):
		"""Join

		Passes join message along to observer

		Returns:
			None
		"""
		self._observer.join()

	def start(self):
		"""Start

		Starts the app by first parsing the imports and adding observers for
		them, then running the actual process.

		Returns
			None
		"""

		# If verbose mode is on
		if self._verbose:
			print('Starting %s' % self._name)

		# Clear the files
		self._files = self._additional_files and self._additional_files[:] or []

		# If it's a module
		if self._mode == 'module':

			if self._verbose:
				print('\tobserving module')

			# Convert . to /
			sFile = self._command.replace('.', '/')

			# Does the file exist as is?
			if os.path.exists('%s.py' % sFile):
				self._files.append('%s.py' % sFile)

			# Else, look for special python module file(s)
			else:

				# Check for an __init__.py file
				if os.path.exists('%s/__init__.py' % sFile):
					self._files.append('%s/__init__.py' % sFile)

				# Check for a __main__.py file
				if os.path.exists('%s/__main__.py' % sFile):
					self._files.append('%s/__main__.py' % sFile)

		# Else, it's a script
		else:

			if self._verbose:
				print('\tobserving script')

			# Check for the command as is
			if os.path.exists(self._command):
				self._files.append(self._command)

		# If we have no files
		if not self._files:

			# Print error
			print('\tCan not find anything to load for %s' % self._name, file=sys.stderr)

			# Return error
			return False

		# Go through each found file
		for sFile in list(self._files):

			# Look for more files within it
			imports.find(sFile, self._files)

		# If verbose mode is on
		if self._verbose:
			print('\tthe following imports were found:')
			for s in self._files:
				print('\t\t%s' % s)

		# For each file, add a schedule
		for s in self._files:
			self._observer.schedule(self, s)

		# Create the subprocess
		try:
			if self._verbose:
				print('\tcreating subprocess...', end='')

			self._process = subprocess.Popen(
				self._args,
				bufsize=0,
				cwd=os.getcwd(),
				env=os.environ,
				stdout=sys.stdout,
				stderr=sys.stderr
			)

			if self._verbose:
				print(' done')

		except OSError as e:
			print('%s: invalid process\n%s' % (self._name, str(e.args)), file=sys.stderr)
			return False

		except ValueError as e:
			print('%s: invalid arguments\n%s' % (self._name, str(e.args)), file=sys.stderr)
			return False

		# Return OK
		return True

	def stop(self):
		"""Stop

		Stops the app, first by removing all observers, then by stopping the
		actual process

		Returns:
			None
		"""

		# If verbose mode is on
		if self._verbose:
			print('Stopping %s' % self._name)

		# Stop watching all associated files
		if self._verbose:
			print('\tstop observing files...', end='')
		self._observer.unschedule_all()
		if self._verbose:
			print(' done')

		# Send a signal to the process to terminate
		if self._verbose:
			print('\tterminating process...', end='')
		self._process.terminate()

		# Wait for the process to terminate
		try:
			self._process.wait(10)

		# If it won't shut down, kill it
		except subprocess.TimeoutExpired:
			if self._verbose:
				print('Processing not terminating, attempting to kill...', end='')
			self._process.kill()

		if self._verbose:
			print(' done')

		# Delete the process
		del self._process
