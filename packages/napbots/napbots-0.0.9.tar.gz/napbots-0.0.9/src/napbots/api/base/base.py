__author__ = "Hugo Inzirillo"

import json
import logging

from authlib.integrations.requests_client import OAuth2Session
from requests import Response
from requests.exceptions import HTTPError

from napbots.api.authentication.auth import ClientCredentials
from napbots.api.data.serializable import Formatter


class BaseClient:
    _base_url = None

    def __init__(self):
        self._client_credentials = None
        pass

    @property
    def credentials(self) -> ClientCredentials:
        return self._client_credentials

    @credentials.setter
    def credentials(self, _credentials: ClientCredentials):
        if isinstance(_credentials, ClientCredentials):
            self._client_credentials = _credentials

    @property
    def session(self) -> OAuth2Session:
        _session = OAuth2Session(
            self.credentials.client_id,
            self.credentials.client_secret,
            scope=self.credentials.scope,
        )

        _session.fetch_token(self._get_url("/oauth/token"))
        return _session

    def _get_url(self, url: str):
        return self._base_url + url

    @property
    def headers(self):
        return {"Content-type": "application/json", "Accept": "application/json"}

    @staticmethod
    def _handle_response(response: Response) -> Response:
        if response.status_code == 200:
            print(response.json())
            return response.json()
        else:
            print(response.json())
            return response

    def _get(self, route, **kwargs):
        url = self._get_url(route)
        response = self.session.get(url, headers=self.headers, **kwargs)
        return self._handle_response(response)

    def _post(self, route, data=None, **kwargs) -> Response:
        url = self._get_url(route)
        dumps = format(data, Formatter.JSON)
        print(f"send : {dumps}")
        response = self.session.post(url, data=dumps, headers=self.headers, **kwargs)
        return self._handle_response(response)
