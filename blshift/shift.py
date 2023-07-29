"""Shift api wrapper class
"""

from enum import Enum
from functools import wraps
from time import sleep

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from requests.exceptions import HTTPError
from requests.packages.urllib3.util.retry import Retry

from .__version__ import __version__


class ShiftException(Exception):
	"""blshift exception"""

def check_login(func):
	@wraps(func)
	def wrapper(self, *args, **kwargs):
		if '_session_id' not in self.session.cookies:
			raise ShiftException('Not logged in')
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
			'Origin': 'https://shift.gearboxsoftware.com',
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

	def get_auth_token(self):
		"""get csrf authentication token"""

		resp = self.session.get('https://shift.gearboxsoftware.com/home', timeout=5)
		resp.raise_for_status()

		soup = BeautifulSoup(resp.text, 'html.parser')
		token = soup.select_one('input[name="authenticity_token"]')

		return token['value']

	def login(self, user, passwd):
		"""authenticate"""

		resp = self.session.post(
			'https://shift.gearboxsoftware.com/sessions',
			headers={'Referer': 'https://shift.gearboxsoftware.com/home'},
			data={
				'utf8': '✓',
				'authenticity_token': self.get_auth_token(),
				'user[email]': user,
				'user[password]': passwd,
				'commit': 'SIGN IN',
			},
			timeout=5
		)
		resp.raise_for_status()
		if not resp.history[0].headers['Location'].endswith('/account'):
			raise ShiftException('Unsuccessful login')

		return True

	def get_codes(self):
		"""get active codes from orcicorn.com"""

		resp = requests.get(f"https://shift.orcicorn.com/tags/{self.platform.name.lower()}/index.json", timeout=5)
		resp.raise_for_status()
		return resp.json()[0].get('codes', [])

	@check_login
	def redeem(self, code):
		"""redeem shift code"""

		resp = self.session.get(
			f"https://shift.gearboxsoftware.com/entitlement_offer_codes",
			params={'code': code},
			headers={
				'Referer': 'https://shift.gearboxsoftware.com/rewards',
				'X-Requested-With': 'XMLHttpRequest',
			},
			timeout=5
		)
		resp.raise_for_status()
		status = resp.text.strip()

		if 'does not exist' in status.lower():
			return False, 'NO_SUCH_CODE'

		return True, resp.text.strip()

	def logout(self):
		"""logout and delete session"""

		try:
			if '_session_id' in self.session.headers:
				self.session.get(
					'https://shift.gearboxsoftware.com/logout',
					headers={'Referer': 'https://shift.gearboxsoftware.com/'},
					timeout=5
				)
				del self.session.headers['_session_id']

		except Exception:
			pass

		finally:
			self.session.close()
