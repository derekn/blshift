"""Blshift tests
"""

import pytest
from blshift.shift import Shift, ShiftException


def test_shift_login_success(user_and_passwd):
	with Shift('xboxlive') as shift:
		assert shift.login(user_and_passwd[0], user_and_passwd[1]) == True
		assert '_session_id' in shift.session.cookies

def test_shift_login_fail():
	shift = Shift('xboxlive')
	with pytest.raises(ShiftException):
		shift.login('foo', 'bar123')

def test_get_codes():
	codes = Shift('xboxlive').get_codes()
	assert isinstance(codes, list)
	assert len(codes)

def test_check_login_decorator():
	shift = Shift('xboxlive')
	with pytest.raises(ShiftException):
		shift.redeem('abc-1234')

@pytest.mark.parametrize('code, expect', [
	('abc-123', False),
	('T3FJT-SBZZT-93BFC-3B3TB-3BTRB', True),
])
def test_redeem(user_and_passwd, code, expect):
	shift = Shift('xboxlive', user_and_passwd[0], user_and_passwd[1])
	status, _ = shift.redeem(code)
	assert status == expect

def test_auth_token():
	shift = Shift('xboxlive')
	assert shift.get_auth_token()
