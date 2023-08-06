import json

import requests


class Client(object):
    """Rockefeller Archive Center API client class"""

    def __init__(self, session=None):
        """A :class:`Client` object for interacting with the RAC's API.

        A Client object with session, optional auth handler, and options.

        """
        self.base_url = 'https://api.rockarch.org'
        self.page_size = 50
        self.session = session or requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'User-Agent': 'rac-api-client/0.1'
        })

    def request(self, method, path, params=None):
        """Dispatches a request to the RAC HTTP API"""
        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        # Convert booleans to JSON values
        if params:
            for key, val in params.items():
                if isinstance(val, bool):
                    params[key] = json.dumps(val)
        response = getattr(self.session, method)(url, params=params)
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return response.text

    def get(self, path, **kwargs):
        """Dispatches a GET request."""
        return self.request('get', path, params=kwargs.get("params", {}))

    def get_paged(self, path, **kwargs):
        """GET paged content."""

        params = {}

        if "params" in kwargs:
            params.update(**kwargs['params'])
            del kwargs['params']

        params.update(limit=self.page_size, offset=0)

        current_page = self.get(path, params=params, **kwargs)

        while len(current_page["results"]):
            for obj in current_page["results"]:
                yield obj
            if current_page.get("next"):
                params["offset"] += self.page_size
                current_page = self.get(path, params=params)
            else:
                break
