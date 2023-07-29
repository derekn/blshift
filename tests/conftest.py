import pytest


def pytest_addoption(parser):
	parser.addoption('--user', action='store')
	parser.addoption('--passwd', action='store')

@pytest.fixture
def user_and_passwd(request):
	user = request.config.getoption('--user')
	passwd = request.config.getoption('--passwd')

	if not (user and passwd):
		pytest.skip('--user/--passwd not supplied')

	return (user, passwd)
