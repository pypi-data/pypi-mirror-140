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

from contextlib import contextmanager
from functools import cached_property
from itertools import chain
from .exceptions import WebServiceDefinitionError
from .request import FrozenRequest

class AddressableChain:
    """
    Wrapper class around ``itertools.chain`` that casts it as a list when
    necessary in order to support ``__len__()`` and ``__getitem__()``.
    """

    def __init__(self, iterable):
        self.iterable = chain.from_iterable(iterable)

    def __len__(self):
        return len(self.list())

    def __getitem__(self, index):
        return self.list()[index]

    def __iter__(self):
        yield from self.list()

    def list(self):
        if not isinstance(self.iterable, list):
            self.iterable = list(self.iterable)
        return self.iterable

class Response:
    def __init__(self, client, request, response=None):
        self.client = client
        self.request = FrozenRequest(request)
        self.response = response

class JsonResponse(Response):
    @cached_property
    def json(self):
        return self.response.json() if self.response else {}

class RestResponseMixin:
    """
    Mixin for all response types that are capable of converting response data
    into Python representations of REST objects.
    """
    REST_CLASS = NotImplemented

    def get_instance_args(self):
        return ()

    def create_instance(self, **kwargs):
        return self.REST_CLASS(*self.get_instance_args(), **kwargs)

class JsonRestResponse(RestResponseMixin, JsonResponse):
    @cached_property
    def instance(self):
        return self.create_instance(**self.json)

class SequenceResponseMixin:
    """
    Mixin for all response types that need to iterate over a series.
    """
    def __len__(self):
        return len(self.get_series_from_response())

    def __getitem__(self, index):
        return self.get_series_from_response()[index]

    def __iter__(self):
        yield from self.get_series_from_response()

    def pages(self):
        """
        This is a placeholder method that can be overridden in subclasses that
        need to implement real paging.
        """
        yield self.get_series_from_response()

    def get_series_from_response(self):
        """
        This method should return a sequence from the response content.
        """
        raise NotImplementedError('Subclasses must implement this method.')

class CachingSequenceResponseMixin(SequenceResponseMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # This can be deactivated via the no_cache() context manager
        self._cache_response = True
        self._cache = None

    def __len__(self):
        if self._cache_response:
            if self._cache is None:
                self.cache_response()
            return len(self._cache)
        else:
            return super().__len__()

    def __getitem__(self, index):
        if self._cache_response:
            if self._cache is None:
                self.cache_response()
            return self._cache[index]
        else:
            return super().__getitem__(index)

    def __iter__(self):
        if self._cache_response:
            if self._cache is None:
                self.cache_response()
            yield from self._cache
        else:
            yield from super().__iter__()

    def cache_response(self):
        if self._cache is None:
            assert self._cache_response, 'Cannot cache the response in this context.'
            self._cache = AddressableChain(self.pages())

    @contextmanager
    def no_cache(self):
        """
        Activates a context in which the parsed sequence will not be cached.
        """
        prev = self._cache_response
        try:
            self._cache_response = False
            yield
        finally:
            self._cache_response = prev

class JsonSequenceRestResponse(SequenceResponseMixin, RestResponseMixin, JsonResponse):
    """
    Helper class that defines a usable ``get_series_from_response()`` method,
    provided the class-level ``CONTAINER_PROPERTY`` attribute is defined
    correctly.
    """
    CONTAINER_PROPERTY = None

    def get_series_from_response(self):
        if self.CONTAINER_PROPERTY is None:
            raise WebServiceDefinitionError(
                'This class must define a value for the CONTAINER_PROPERTY attribute.'
            )
        return [self.create_instance(**data) for data in self.json[self.CONTAINER_PROPERTY]]

class CachingJsonSequenceRestResponse(CachingSequenceResponseMixin, JsonSequenceRestResponse):
    pass

class PagingMixin:
    def __init__(self, *args, **kwargs):
        self.request_history = None
        # Note that the limit determines the point at which the client will
        # stop making new requests, but the iterator will always return all
        # the response content. In other words, if the entire series contains
        # 15 or more items, with a limit of 13 and the page size of 5, the
        # iterator will yield 15 instances.
        self.limit = kwargs.pop('limit', None)
        if self.limit is not None and not (isinstance(self.limit, int) and self.limit > 0):
            raise ValueError(
                'The limit, if specified, must be an integer greater than zero.'
            )
        super().__init__(*args, **kwargs)

    def pages(self):
        """
        Defines the basic logic for paging through API responses.
        """
        self.request_history = []
        # The request attribute here is an instance of FrozenRequest. We want
        # to work with the actual Request instance so it can be cloned
        # properly.
        request = self.request.wrapped
        count = 0
        is_json_response = isinstance(self, JsonResponse)
        while True:
            self.client.request(request, self)
            self.request_history.append(request)
            if is_json_response:
                # The JSON is cached upon access in order to make it easier to
                # work with it as a property that exposes a dict, but that
                # means that it won't be updated between pages if we don't
                # take care to uncache it.
                try:
                    del self.__dict__['json']
                except KeyError:
                    pass
            page = self.get_series_from_response()
            count += len(page)
            yield page
            if self.limit and count >= self.limit:
                break
            request = self.get_next_request(request, count)
            if not request:
                break

    def get_next_request(self, request, count):
        """
        Given the previous request and a count of the number of instances
        retrieved so far, returns the request to be performed to retrieve the
        next page of results, or None if no additional page exists.
        """
        raise NotImplementedError('Subclasses must implement this method.')