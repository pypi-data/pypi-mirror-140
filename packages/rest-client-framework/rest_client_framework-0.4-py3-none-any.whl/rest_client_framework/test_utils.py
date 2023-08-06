# Copyright 2021 Performics
#
# This file is part of rest-client-framework.
#
# rest-client-framework is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# rest-client-framework is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with rest-client-framework.  If not, see <https://www.gnu.org/licenses/>.

import requests
from rest_client_framework.request import Request

def get_mock_response(request, status_code=200, content=None,
    encoding='utf-8', url=None, headers=None
):
    """
    Returns an instance of ``requests.Response`` containing the given
    attributes.
    """
    response = requests.Response()
    if isinstance(request, Request):
        response.request = requests.Request(
            request.method,
            request.url,
            headers=request.get_headers(),
            data=request.get_formatted_body()
        ).prepare()
    elif request:
        response.request = request.prepare()
    response.encoding = encoding
    if status_code:
        response.status_code = status_code
    if content:
        if not isinstance(content, bytes):
            content = content.encode('utf-8')
        response._content = content
    if response.request and not url:
        url = response.request.url
    response.url = url
    if headers:
        response.headers.update(headers)
    return response

class WebServiceResponseSimulator:
    """
    Helper for tests that need to test the behavior of a web service client
    class in reaction to specific response content. An instance of this class
    is intended to be be patched in place of the transport's ``request()``
    method.
    """
    def __init__(self, **mock_response_args):
        self.mock_response_args = mock_response_args
        # If any argument is a list, they all most be lists of the same
        # length, and the behavior of this instance when called will be to
        # return a series of responses.
        self.iterate = None
        self.iterator = None
        self.length = None
        for param in self.mock_response_args.values():
            if isinstance(param, list):
                if self.iterate is False:
                    raise TypeError(
                        'Cannot pass a mix of list and non-list arguments.'
                    )
                self.iterate = True
                if self.length is None:
                    self.length = len(param)
                elif len(param) != self.length:
                    raise ValueError(
                        'All lists passed as arguments must have equal lengths.'
                    )
            elif self.iterate:
                raise ValueError(
                    'Cannot pass a mix of list and non-list arguments.'
                )

    def __call__(self, method, url, **kwargs):
        # Some keyword arguments that may be passed to requests.request() are
        # inappropriate for the Request constructor itself.
        kwargs = {k: v for k, v in kwargs.items() if k in (
            'headers', 'files', 'data', 'params', 'auth', 'cookies', 'hooks', 'json'
        )}
        if self.iterate:
            if not self.iterator:
                def iterator(method, url, **kwargs):
                    for i in range(self.length):
                        yield get_mock_response(requests.Request(
                            method, url, **kwargs
                        ), **{k: v[i] for k, v in self.mock_response_args.items()})
                self.iterator = iterator(method, url, **kwargs)
            return next(self.iterator)
        else:
            return get_mock_response(requests.Request(
                method, url, **kwargs
            ), **self.mock_response_args)