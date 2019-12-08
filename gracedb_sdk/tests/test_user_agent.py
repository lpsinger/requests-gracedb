from .. import __version__
from .. import Client
from .. import _version


def test_user_agent(socket_enabled, httpserver):
    expected_user_agent = f'gracedb_sdk/{__version__}'

    httpserver.expect_oneshot_request(
        '/', headers={'User-Agent': expected_user_agent}
    ).respond_with_data(
        'OK'
    )

    url = httpserver.url_for('/')
    client = Session(url)
    with httpserver.wait():
        client.get(url)
