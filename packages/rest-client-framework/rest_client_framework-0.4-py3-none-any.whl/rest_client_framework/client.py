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

import logging, requests
from contextlib import contextmanager
from importlib import import_module
from .exceptions import *
from .response import Response, PagingMixin

logger = logging.getLogger(__name__)

class SimulationContextError(RuntimeError):
    """
    Client implementations may raise this exception upon an attempt to perform
    an operation that is impossible in the current simulation context (e.g. a
    request that changes remote data during a context that simulates write
    requests).
    """

class NoOpTransport:
    def request(self, method, url, **kwargs):
        logger.debug('Skipped {} request to {}'.format(method, url))
        request = requests.Request(method, url, **kwargs)
        response = requests.Response()
        response.status_code = 200
        response.request = request
        return response

class Client:
    RETRY = 1
    REQUEST_TYPE_READ = 2
    REQUEST_TYPE_WRITE = 4
    base_url = None
    # This attribute controls automatic repetition of requests that fail due to
    # remote errors that may be temporary.
    max_attempts = 3
    # Subclasses may set a Response subclass here, which will be used to
    # instantiate responses when no specific response class is provided.
    response_class = None
    # Level at which to log basic information about each request (the request
    # URL, HTTP method, and attempt number).
    request_log_level = logging.DEBUG
    # Level at which to log request HTTP headers
    request_verbose_log_level = logging.NOTSET
    # Level at which to log basic information about each response (response
    # size and HTTP status).
    response_log_level = logging.DEBUG
    # Level at which to log response content and HTTP headers
    response_verbose_log_level = logging.NOTSET
    verbose_name = None

    def __init__(self):
        self.transport = self.create_transport()
        self.logger = self.get_logger()
        self.attempt_count = 0
        self.responses = []
        if not self.response_class:
            # If the concrete implementation defines its own response module,
            # use its Response class as a default when instantiating responses;
            # otherwise use the generic one.
            try:
                self.response_class = import_module('..response', self.__class__.__module__).Response
            except (ImportError, AttributeError, ValueError):
                self.response_class = Response
        self.simulation_context = 0

    @classmethod
    def get_verbose_name(cls):
        return cls.verbose_name or cls.__module__

    def create_transport(self):
        return requests

    def get_transport(self):
        """
        Returns a transport, which should be an object implementing a
        ``request()`` method. Normally this is the value of the ``transport``
        attribute, but this may need to be something else in simulated request
        contexts.
        """
        return self.transport

    def get_logger(self):
        return logging.getLogger(self.__class__.__module__)

    def handle_response(self, request, response, response_class_or_instance,
        **response_class_kwargs
    ):
        """
        Examines a ``requests.Response`` instance and determines how to
        proceed. If this method raises an error, it will halt execution of the
        request immediately, and no more retries will be attempted. If it
        returns an instance of the specified response type, the execution of
        the request will be considered complete. If it returns
        ``Client.RETRY``, the request will be retried if eligible.
        """
        # The response could be None, which is OK
        if response is not None and not response.ok:
            raise ServiceResponseError(request, response)
        if isinstance(response_class_or_instance, Response):
            response_class_or_instance.response = response
            return response_class_or_instance
        return response_class_or_instance(
            self, request, response, **response_class_kwargs
        )

    def prepare_for_retry(self, request):
        """
        This hook will be executed prior to retrying a request. This may be
        used to delay the retry for a certain amount of time, for example.
        """

    def should_skip_request(self, request):
        """
        If this method returns True, the request will be skipped, and the
        client's ``handle_response()`` method will be called immediately.
        """
        return False

    def request(self, request, response_class_or_instance=None,
        **response_class_kwargs
    ):
        if response_class_or_instance is None:
            response_class_or_instance = self.response_class
        # If the response is paged, instantiate and return it so that an
        # external request can iterate over it.
        try:
            if issubclass(response_class_or_instance, PagingMixin):
                return response_class_or_instance(
                    self, request, **response_class_kwargs
                )
        except TypeError:
            # The response parameter is not a class; proceed as usual
            pass
        if self.should_skip_request(request):
            return self.handle_response(
                request, None, response_class_or_instance, **response_class_kwargs
            )
        self.attempt_count = 0
        self.responses = []
        request_kwargs = {
            'headers': request.get_headers(),
            'data': request.get_formatted_body()
        }
        if request.basic_auth:
            request_kwargs['auth'] = request.basic_auth
        for i in range(self.max_attempts):
            self.attempt_count += 1
            self.logger.log(self.request_log_level, 'Attempting {} (attempt {} of {})...'.format(
                request, self.attempt_count, self.max_attempts
            ))
            response = self.get_transport().request(
                request.method, request.url, **request_kwargs
            )
            self.responses.append(response)
            self.logger.log(self.request_verbose_log_level, 'Request trace:\n\n{} {}\n\n{}'.format(
                response.request.method, response.request.url, '\n'.join(
                    ['{}: {}'.format(header, value) for header, value in response.request.headers.items()]
                )
            ))
            response_length = 0 if response.content is None else len(response.content)
            self.logger.log(self.response_log_level, 'Got {}-byte response with code {}.'.format(
                response_length, response.status_code
            ))
            self.logger.log(self.response_verbose_log_level, 'Response headers:\n\n{}'.format('\n'.join(
                ['{}: {}'.format(header, value) for header, value in response.headers.items()]
            )))
            self.logger.log(self.response_verbose_log_level, 'Response content: {}'.format(response.text))
            result = self.handle_response(
                request, response, response_class_or_instance, **response_class_kwargs
            )
            if result != self.RETRY:
                self.finalize_request(request)
                return result
            if self.attempt_count <= self.max_attempts:
                self.prepare_for_retry(request)
        raise MaximumAttemptsExceeded(request, self.responses, self.attempt_count)

    def finalize_request(self, request):
        """
        This hook is called after a completed request that will not be retried.
        """

    @contextmanager
    def simulate_requests(self, request_type=REQUEST_TYPE_WRITE):
        """
        Activates a context in which requests of the given type (which may be
        a bitmask of multiple types) are simulated. It is the concrete
        subclass's responsibility to actually implement the simulation.
        """
        prev = self.simulation_context
        try:
            self.simulation_context = request_type
            yield
        finally:
            self.simulation_context = prev