import requests

from sugarcrm import exception
from sugarcrm.enumerator import ErrorEnum


class Client(object):
    VERSIONS = {
        '7.7': 'rest/v10/',
        '7.8': 'rest/v10/',
        '7.9': 'rest/v10/',
        '7.10': 'rest/v11/',
        '7.11': 'rest/v11/',
        '8.0': 'rest/v11_1/',
        '8.1': 'rest/v11_2/',
        '8.2': 'rest/v11_3/',
        '8.3': 'rest/v11_4/'
    }

    def __init__(self, url, username, password, version, requests_session=None, requests_hooks=None):

        if not url.endswith('/'):
            url += '/'
        if any((v in version for v in self.VERSIONS.keys())):
            url += self.VERSIONS[version]
        else:
            raise exception.UnsupportedVersion('The version {} is not supported by this library.'.format(version))

        self.version = version
        self.url = url
        self.username = username
        self.password = password
        self.requests_session = requests_session
        if requests_hooks and not isinstance(requests_hooks, dict):
            raise Exception(
                'requests_hooks must be a dict. e.g. {"response": func}. http://docs.python-requests.org/en/master/user/advanced/#event-hooks')
        self.requests_hooks = requests_hooks

        self.access_token = None

    def get_token(self, username, password, client_id='sugar', client_secret='', platform='base'):
        data = {
            'grant_type': 'password',
            'client_id': client_id,
            'client_secret': client_secret,
            'username': username,
            'password': password,
            'platform': platform
        }
        return self._post('oauth2/token', json=data)

    def refresh_token(self, refresh_token, client_id='sugar', client_secret=''):
        data = {
            'grant_type': 'refresh_token',
            'client_id': client_id,
            'client_secret': client_secret,
            'refresh_token': refresh_token
        }
        return self._post('oauth2/token', json=data)

    def set_access_token(self, access_token):
        self.access_token = access_token

    def get_leads(self, **kwargs):
        return self._get('Leads', **kwargs)

    def create_lead(self, **kwargs):
        return self._post('Leads', **kwargs)

    def _get(self, endpoint, **kwargs):
        return self._request('GET', endpoint, **kwargs)

    def _post(self, endpoint, **kwargs):
        return self._request('POST', endpoint, **kwargs)

    def _request(self, method, endpoint, headers=None, **kwargs):
        _headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        if self.access_token:
            _headers['Authorization'] = 'Bearer {}'.format(self.access_token)

        if headers:
            _headers.update(headers)

        kwargs['headers'] = _headers

        if self.requests_hooks:
            kwargs.update({'hooks': self.requests_hooks})

        if self.requests_session:
            client = self.requests_session
        else:
            client = requests

        return self._parse(client.request(method, self.url + endpoint, **kwargs))

    def _parse(self, response):
        if 'application/json' in response.headers['Content-Type']:
            r = response.json()
        else:
            try:
                r = response.json()  # Una version anterior de SugarCRM no utiliza los headers adecuadamente.
            except Exception:
                return response.text

        if 'name' in r and 'description' in r and 'number' in r:
            code = r['number']
            message = r['description']

            try:
                error_enum = ErrorEnum(code)
            except Exception:
                raise exception.UnknownError('Error: {}. Message {}'.format(code, message))
            if error_enum == ErrorEnum.InvalidLogin:
                raise exception.InvalidLogin(message)
        return r
