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

class RestRuntimeError(RuntimeError):
    pass

class ServiceResponseError(RestRuntimeError):
    def __init__(self, request, msg):
        from rest_client_framework.request import FrozenRequest
        self.request = FrozenRequest(request)
        if isinstance(msg, requests.Response):
            self.response = msg
            msg = 'The request failed with HTTP status {}.'.format(
                self.response.status_code
            )
        super().__init__(msg)

class MaximumAttemptsExceeded(RestRuntimeError):
    def __init__(self, request, responses, attempts):
        from rest_client_framework.request import FrozenRequest
        self.request = FrozenRequest(request)
        self.responses = responses
        self.attempts = attempts
        super().__init__('Failed to complete {} request to {} after {} attempts.'.format(
            request.method, request.get_printable_url(), attempts
        ))

class ConfigurationError(RuntimeError):
    pass

class WebServiceDefinitionError(ConfigurationError):
    pass

class RestDefinitionError(ConfigurationError):
    pass

class AttributeCollisionError(RestDefinitionError):
    def __init__(self, attr_name, *rest_paths):
        super().__init__('Multiple REST properties map to the attribute "{}" ({}).'.format(
            attr_name, ', '.join(str(p) for p in rest_paths)
        ))

class AmbiguousDatetimeFormatError(RestDefinitionError):
    pass

class AmbiguousOrderedSequenceError(RestDefinitionError):
    pass