"""Blshift command line
"""

import sys
from multiprocessing.pool import ThreadPool
from pathlib import Path
from tempfile import gettempdir

import click as cl
from diskcache import Cache

from . import Shift, __copyright__, __url__, __version__


def redeem_code_init(shift):
	redeem_code.shift = shift

def redeem_code(code):
	success, msg = redeem_code.shift.redeem(code['code'])
	return code, success, msg

@cl.command(no_args_is_help=True, epilog=__url__)
@cl.version_option(version=__version__, message=f"%(prog)s version %(version)s, {__copyright__}\n{__url__}")
@cl.option('-u', '--user', required=True, help='shift username.', envvar='SHIFT_USERNAME')
@cl.option('-p', '--pass', 'password', required=True, help='shift password.', envvar='SHIFT_PASSWORD')
@cl.option('-l', '--platform', required=True, help='redemption platform.', envvar='SHIFT_PLATFORM',
           type=cl.Choice([x.name for x in Shift.Platforms], case_sensitive=False))
@cl.option('-c', '--code', 'codes', help='redeem single shift code, can be used multiple times.', multiple=True)
@cl.option('--no-cache', is_flag=True, default=False, help='disable shift code caching.')
@cl.option('--cache-dir', default=gettempdir(), help='cache directory, default system temp.', envvar='SHIFT_CACHE_DIR',
           type=cl.Path(exists=True, file_okay=False, writable=True))
def main(user, password, platform, codes, no_cache, cache_dir):
	"""redeem all active or individual shift codes for Borderlands"""

	no_cache = True if codes else no_cache
	platform = Shift.Platforms[platform]

	try:
		cache = Cache(str(Path(cache_dir, 'blshift.cache')), eviction_policy='none') if not no_cache else {}
		redeemed = cache.get(user, set())

		with Shift(platform, user, password) as shift:
			if codes:
				# codes = [{'code': x['code'], 'reward': x['offer_title_text']} for x in (shift.info(y) for y in codes) if x]
				codes = [{'code': x, 'reward': ''} for x in codes]
			else:
				codes = shift.get_codes()

			if redeemed.issuperset(x['code'] for x in codes):
				if sys.stdout.isatty():
					cl.echo('No new codes found')
				raise SystemExit(0)
			width = max(len(x['reward']) + len(x['code']) for x in codes if x['code'] not in redeemed)

			try:
				with ThreadPool(8, redeem_code_init, (shift,)) as pool:
					for code, success, msg in pool.imap_unordered(redeem_code, (x for x in codes if x['code'] not in redeemed)):
						pad = width - (len(code['code']) + len(code['reward']))
						msg = f"{cl.style('Success', fg='green') if success else cl.style(msg.replace('_', ' ').title(), fg='red')}"
						cl.echo(f"{cl.style(code['code'], bold=True)} {code['reward']}: {' ' * pad}{msg}", err=(not success))
						redeemed.add(code['code'])

			finally:
				cache[user] = redeemed.intersection(x['code'] for x in codes)

	except Exception as err:
		cl.echo(f"{cl.style('Error', fg='red')}: {str(err)}", err=True)

if __name__ == '__main__':
	main()
