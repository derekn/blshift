"""shift api wrapper class
"""

from enum import Enum
from functools import wraps
from time import sleep

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import HTTPError
from requests.packages.urllib3.util.retry import Retry

from .__version__ import __version__


class ShiftException(Exception):
	"""blshift exception"""

def check_login(func):
	@wraps(func)
	def wrapper(self, *args, **kwargs):
		if 'X-SESSION' not in self.session.headers:
			raise ShiftException('Not logged in.')
		return func(self, *args, **kwargs)

	return wrapper

class Shift:
	"""borderlands shift api wrapper"""

	class Platforms(Enum):
		EPIC = 'epic'
		NINTENDO = 'nintendo'
		PLAYSTATION = 'psn'
		STADIA = 'stadia'
		STEAM = 'steam'
		XBOX = 'xboxlive'

	def __init__(self, platform, user=None, passwd=None):
		retry = Retry(
			total=3,
			status_forcelist=(429, 500, 502, 503, 504),
			backoff_factor=5
		)
		adapter = HTTPAdapter(max_retries=retry)

		self.platform = self.Platforms(platform)
		self.session = requests.Session()
		self.session.headers.update({
			'User-Agent': f"blshift/{__version__}",
			'Origin': 'https://borderlands.com',
			'Pragma': 'no-cache',
			'Cache-Control': 'no-cache'
		})
		self.session.mount("http://", adapter)
		self.session.mount("https://", adapter)

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
		if resp.status_code == requests.codes.forbidden:
			raise HTTPError('Unsuccessful login', response=resp)
		resp.raise_for_status()

		self.session.headers.update({'X-SESSION': resp.headers['X-SESSION-SET']})
		return resp.json()

	@check_login
	def get_codes(self):
		"""get active codes from orcicorn.com"""

		resp = requests.get(f"https://shift.orcicorn.com/tags/{self.platform.name.lower()}/index.json", timeout=5)
		resp.raise_for_status()
		return resp.json()[0].get('codes', [])

	@check_login
	def redeem(self, code):
		"""redeem shift code"""

		resp = self.session.post(
			f"https://api.2k.com/borderlands/code/{code}/redeem/{self.platform.value}",
			headers={'Referer': 'https://borderlands.com/en-US/profile/'},
			timeout=5
		)
		if resp.status_code == requests.codes.not_found:
			return False, 'NO_SUCH_CODE'
		if resp.status_code == requests.codes.precondition_failed:
			raise ShiftException('Rate limit exceeded, try again later')
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
			return resp.get('success', False), next(iter(resp.get('errors', [])), 'UNKOWN_ERROR')

		except Exception as err:
			return False, str(err)

	@check_login
	def info(self, code):
		"""get details for code"""

		try:
			resp = self.session.get(f"https://api.2k.com/borderlands/code/{code}/info", timeout=5)
			resp.raise_for_status()
			resp = resp.json()

			return next((x for x in resp['entitlement_offer_codes'] if x['offer_service'] == self.platform.value), None)

		except Exception:
			return None

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
