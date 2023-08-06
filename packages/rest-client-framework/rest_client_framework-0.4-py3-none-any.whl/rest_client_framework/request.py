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

import json
from copy import copy, deepcopy
from hashlib import sha1
from urllib.parse import urlencode, urljoin, urlparse, urlunparse
from .datastructures import BaseFrozenObject

class Request:
    def __init__(self, client, path, *, method='GET', body=None, headers=None, **kwargs):
        if body is not None and not self.method_supports_body(method):
            raise ValueError('The request method "{}" does not support a request body.'.format(method))
        self.client = client
        self.path = path
        self.method = method
        self.body = body
        self.headers = headers or {}
        self.kwargs = kwargs
        self.basic_auth = None

    def __str__(self):
        str_ = '{} request to {}'.format(self.method, self.get_printable_url())
        if self.body is not None:
            str_ += ' with body {}'.format(self.get_printable_body())
        return str_

    @classmethod
    def method_supports_body(cls, method):
        return method == 'POST' or method == 'PUT' or method == 'PATCH'

    def get_digest(self):
        return sha1()

    def update_digest(self, digest, obj):
        if isinstance(obj, dict):
            for key, value in sorted(zip(obj.keys(), obj.values())):
                self.update_digest(digest, '{}='.format(key).encode('utf-8'))
                self.update_digest(digest, value)
        elif isinstance(obj, (list, tuple)):
            # The order may be significant, so don't attempt to sort
            for value in obj:
                self.update_digest(digest, value)
        else:
            digest.update(str(obj).encode('utf-8'))

    def clone(self, **kwargs):
        clone_kwargs = deepcopy(self.kwargs)
        clone_kwargs.update(kwargs)
        clone = self.__class__(
            self.client,
            self.path,
            method=self.method,
            body=deepcopy(self.body),
            headers=deepcopy(self.headers),
            **clone_kwargs
        )
        clone.basic_auth = self.basic_auth
        return clone

    def format_kwargs(self, kwargs):
        """
        Returns a dict containing request keyword arguments formatted as
        required for the service.
        """
        return copy(kwargs)

    def get_printable_url(self):
        """
        This method should return a version of this instance's URL that
        excludes any sensitive information such as API keys. The base
        implementation returns the URL as is.
        """
        return self.url

    def get_serializable_args(self):
        """
        This method should return a version of this instance's keyword
        arguments (i.e. the arguments that will be added to the request URL's
        query string ) suitable for signature evaluation, which may mean the
        removal of temporary authentication tokens or the like.
        """
        return self.kwargs

    def get_printable_body(self):
        """
        This method should return a version of this instance's body suitable
        for printing in log files or in debug contexts.
        """
        return self.body

    def get_serializable_body(self):
        """
        This method should return a version of this instance's body suitable
        for signature evaluation, which may mean the removal of temporary
        authentication tokens or the like.
        """
        return self.body

    def get_formatted_body(self):
        """
        This method should process the body in any way required for the
        service (e.g. if the body is a Python object and the service expects
        a JSON string, this method must handle the conversion).
        """
        if self.body is not None:
            assert self.method_supports_body(self.method), \
                'A body was set for a {} request.'.format(self.method)
        return self.body

    def get_headers(self):
        """
        Returns the headers. This method serves as a hook for subclasses to
        modify their contents.
        """
        return self.headers

    def get_base_url(self):
        return self.client.base_url

    def set_basic_authentication(self, user, password):
        self.basic_auth = (user, password)

    @property
    def kwargs(self):
        return self._kwargs

    @kwargs.setter
    def kwargs(self, kwargs):
        self._kwargs = self.format_kwargs(kwargs)

    @property
    def url(self):
        # There's an edge case for path fragments containing colons with no
        # preceding slash; these cause urljoin() to mistake them for a scheme
        # and thus discard the base URL. Many Google APIs use literal colons in
        # path components, despite the fact that this technically violates RFC-
        # 3986.
        colon_pos = self.path.find(':')
        slash_pos = self.path.find('/')
        if colon_pos > -1 and (slash_pos == -1 or slash_pos > colon_pos):
            # We'll have to roll some our own logic for this
            base_url_components = urlparse(self.get_base_url())
            if base_url_components.path:
                partitioned_path = base_url_components.path.rpartition('/')
                if partitioned_path[-1]:
                    # The base URL doesn't end in a slash, which means that the
                    # combined URL should be relative to the parent directory.
                    # This is possibly not what the user meant to do, but this
                    # is consistent with how urljoin() would work.
                    path = '{}/{}'.format(partitioned_path[0], self.path)
                else:
                    path = base_url_components.path + self.path
            else:
                # THe base URL is a bare domain
                path = '/' + self.path
            url = urlunparse((
                base_url_components.scheme,
                base_url_components.netloc,
                path,
                base_url_components.params,
                base_url_components.query,
                base_url_components.fragment
            ))
        else:
            url = urljoin(self.get_base_url(), self.path)
        if self.kwargs:
            url_components = urlparse(url)
            url = urlunparse((
                url_components.scheme,
                url_components.netloc,
                url_components.path,
                url_components.params,
                urlencode(self.kwargs),
                url_components.fragment
            ))
        return url

    @property
    def signature(self):
        """
        Returns a hash representing this request's arguments for deduplication
        purposes.
        """
        digest = self.get_digest()
        self.update_digest(digest, self.get_serializable_args())
        self.update_digest(digest, self.get_serializable_body())
        return digest.digest()

    @property
    def type(self):
        """
        Returns a reasonable assumption of this request's type based on its
        method. Subclasses may override this for more nuanced behavior.
        """
        return self.client.REQUEST_TYPE_READ if self.method == 'GET' else self.client.REQUEST_TYPE_WRITE

class JsonRequest(Request):
    def get_formatted_body(self):
        if self.body:
            return json.dumps(super().get_formatted_body())

    def get_headers(self):
        headers = super().get_headers()
        if self.body is not None:
            headers['Content-Type'] = 'application/json'

class FrozenRequest(BaseFrozenObject, Request):
    def __init__(self, request):
        # Capture the request's URL here to ensure it doesn't change as the
        # result of a changing context or the like.
        self._url = request.url
        super().__init__(request)

    @property
    def url(self):
        return self._url