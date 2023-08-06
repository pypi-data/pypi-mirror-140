from unittest import TestCase
from unittest.mock import patch, Mock

from box import Box

from pycarlo.common.errors import GqlError
from pycarlo.common.settings import MCD_API_ENDPOINT
from pycarlo.core import Session, Client, Query

MOCK_MCD_ID = 'foo'
MOCK_MCD_TOKEN = 'bar'
MOCK_SESSION_ID = 'qux'
MOCK_TRACE_ID = 'baz'
MOCK_HEADERS = {
    'x-mcd-id': MOCK_MCD_ID,
    'x-mcd-session-id': MOCK_SESSION_ID,
    'x-mcd-token': MOCK_MCD_TOKEN,
    'x-mcd-trace-id': MOCK_TRACE_ID
}
MOCK_TIMEOUT = 16
MOCK_EMAIL = 'dresden@montecarlodata.com'
MOCK_GET_USER_QUERY = """
query {
  getUser {
    email
  }
}
"""
MOCK_GOOD_RESPONSE = {'data': {'getUser': {'email': MOCK_EMAIL}}}
MOCK_BAD_RESPONSE = {'errors': 'Life is a journey. Time is a river. The door is ajar.'}


class MockRequest:
    def __init__(self, url, base_headers, timeout):
        assert url == MCD_API_ENDPOINT
        assert base_headers == MOCK_HEADERS
        assert timeout == MOCK_TIMEOUT

    def __call__(self, query, *args, **kwargs):
        assert str(query).strip() == MOCK_GET_USER_QUERY.strip()


class MockGoodRequest(MockRequest):
    def __init__(self, url, base_headers, timeout):
        super().__init__(url, base_headers, timeout)

    def __call__(self, *args, **kwargs):
        super(MockGoodRequest, self).__call__(*args, **kwargs)
        return MOCK_GOOD_RESPONSE


class MockBadRequest(MockRequest):
    def __init__(self, url, base_headers, timeout):
        super().__init__(url, base_headers, timeout)

    def __call__(self, *args, **kwargs):
        super(MockBadRequest, self).__call__(*args, **kwargs)
        return MOCK_BAD_RESPONSE


class ClientTest(TestCase):
    def setUp(self) -> None:
        self._session = Mock(autospec=Session)
        self._session.endpoint = MCD_API_ENDPOINT
        self._client = Client(session=self._session)

    def test_get_session_id(self):
        self._session.id = MOCK_MCD_ID
        self.assertEqual(self._client.session_id, MOCK_MCD_ID)

    def test_get_session_name(self):
        self._session.session_name = MOCK_SESSION_ID
        self.assertEqual(self._client.session_name, MOCK_SESSION_ID)

    def test_get_session_endpoint(self):
        endpoint = 'test.com'
        self._session.endpoint = endpoint
        self.assertEqual(self._client.session_endpoint, endpoint)

    @patch('pycarlo.core.client.uuid')
    def test_get_headers(self, mock_uuid):
        self._session.id = MOCK_MCD_ID
        self._session.token = MOCK_MCD_TOKEN
        self._session.session_name = MOCK_SESSION_ID
        mock_uuid.uuid4.return_value = MOCK_TRACE_ID

        self.assertEqual(self._client._get_headers(), MOCK_HEADERS)

    @patch('pycarlo.core.client.RequestsEndpoint', MockGoodRequest)
    @patch.object(Client, '_get_headers')
    def test_call(self, mock_headers):
        mock_headers.return_value = MOCK_HEADERS
        self.assertEqual(
            self._client(query=MOCK_GET_USER_QUERY, timeout_in_seconds=MOCK_TIMEOUT),
            Box(MOCK_GOOD_RESPONSE, camel_killer_box=True).data
        )
        mock_headers.assert_called_once_with()

    @patch('pycarlo.core.client.RequestsEndpoint', MockGoodRequest)
    @patch.object(Client, '_get_headers')
    def test_call_with_object(self, mock_headers):
        query = Query()
        query.get_user.__fields__('email')

        mock_headers.return_value = MOCK_HEADERS
        self.assertEqual(self._client(query=query, timeout_in_seconds=MOCK_TIMEOUT).get_user.email, MOCK_EMAIL)
        mock_headers.assert_called_once_with()

    @patch('pycarlo.core.client.RequestsEndpoint', MockBadRequest)
    @patch.object(Client, '_get_headers')
    def test_call_with_errors(self, mock_headers):
        mock_headers.return_value = MOCK_HEADERS
        with self.assertRaises(GqlError):
            self._client(query=MOCK_GET_USER_QUERY, timeout_in_seconds=MOCK_TIMEOUT)
        mock_headers.assert_called_once_with()
