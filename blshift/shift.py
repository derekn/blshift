"""shift api wrapper class
"""

from functools import wraps
from time import sleep

import requests

from .__version__ import __version__


class ShiftException(Exception):
	pass

def get_codes():
	"""get active codes from orcicorn.com"""

	resp = requests.get('https://shift.orcicorn.com/tags/xbox/index.json', timeout=5)
	resp.raise_for_status()
	yield from resp.json()[0].get('codes', [])

def check_login(func):
	@wraps(func)
	def wrapper(self, *args, **kwargs):
		if 'X-SESSION' not in self.session.headers:
			raise ShiftException('not logged in')
		return func(self, *args, **kwargs)

	return wrapper

class Shift:
	"""borderlands shift api wrapper"""

	def __init__(self, user=None, passwd=None):
		self.session = requests.Session()
		self.session.headers.update({
			'User-Agent': f"blshift/{__version__}",
			'Origin': 'https://borderlands.com',
			'Pragma': 'no-cache',
			'Cache-Control': 'no-cache'
		})

		if user and passwd:
			self.login(user, passwd)

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.logout()

	def login(self, user, passwd):
		"""authenticate"""

		resp = self.session.post(
			'https://api.2k.com/borderlands/users/authenticate',
			headers={'Referer': 'https://borderlands.com/en-US/'},
			json={'username': user, 'password': passwd},
			timeout=5
		)
		resp.raise_for_status()

		self.session.headers.update({'X-SESSION': resp.headers['X-SESSION-SET']})
		return resp.json()

	@check_login
	def redeem(self, code):
		"""redeem shift code"""

		resp = self.session.post(
			f"https://api.2k.com/borderlands/code/{code}/redeem/xboxlive",
			headers={'Referer': 'https://borderlands.com/en-US/profile/'},
			timeout=5
		)
		resp.raise_for_status()
		resp = resp.json()

		sleep(resp['min_wait_milliseconds'] / 1000)

		try:
			resp = self.session.get(
				f"https://api.2k.com/borderlands/code/{code}/job/{resp['job_id']}",
				headers={'Referer': 'https://borderlands.com/en-US/profile/'},
				timeout=5
			)
			resp = resp.json()
			return resp.get('success', False), next(iter(resp.get('errors', [])), None)

		except Exception as err:
			return False, str(err)

	def logout(self):
		"""logout and delete session"""

		try:
			if 'X-SESSION' in self.session.headers:
				self.session.delete(
					'https://api.2k.com/borderlands/users/me',
					headers={'Referer': 'https://borderlands.com/en-US/'},
					timeout=5
				)
				del self.session.headers['X-SESSION']

		except Exception:
			pass

		finally:
			self.session.close()
