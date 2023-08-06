# REST Client Framework

This package attempts to simplify the process of connecting to REST APIs by providing a flexible and extensible framework that handles most of the common and/or tedious tasks involved in performing the necessary HTTP requests and working with responses. Its goal is to minimize the time you must spend reinventing the wheel while providing sufficient flexibility to handle the sorts of quirks one sees in the real world. Useful features that this library either supports outright or provides hooks to facilitate your implementation include the following:

* Configurable logging of request and response content
* Automatic repetition of failed requests
* Simulation/interruption of requests in selected contexts (e.g. test environments)
* Automatic JSON encoding/decoding
* Conversion of REST objects into rich Python object instances (and back again)
* Consuming paged API responses

## Quickstart

Here's an example of a quick-and-dirty client for the [Google Chrome UX Report API](https://developers.google.com/web/tools/chrome-user-experience-report/api/reference) built using this framework:

```python
from rest_client_framework import Client
from rest_client_framework.request import JsonRequest as BaseRequest
from rest_client_framework.response import JsonResponse

class ChromeUXReportAPIClient(Client):
    base_url = 'https://chromeuxreport.googleapis.com/v1/'
    response_class = JsonResponse

    def __init__(self, key):
        self.key = key
        super().__init__()

class Request(BaseRequest):
    def __init__(self, client, *args, **kwargs):
        kwargs['key'] = client.key
        super().__init__(client, *args, **kwargs)
```

This code accomplishes the following:

* It declares the API's base URL by setting `ChromeUXReportAPIClient.base_url`
* It specifies the default response class for the API client by setting `ChromeUXReportAPIClient.response_class`
* It overrides `Client.__init__()` to accept an API key, which is stored as an attribute of the client instance
* It overrides `Request.__init__()` to retrieve the API key from the client instance and pass it to the parent constructor as a keyword argument

We can now create and use an instance of this client:

```
>>> key = 'my API key'
>>> client = ChromeUXReportAPIClient(key)
>>> response = client.request(Request(
...     client,
...     'records:queryRecord',
...     method='POST',
...     body={'url': 'https://www.python.org/'}
... ))
>>> type(response)
<class 'rest_client_framework.response.JsonResponse'>
>>> # The underlying HTTP response is available
>>> response.response.status_code
200
>>> # The response's JSON is available as a property
>>> response.json['record']['metrics']['largest_contentful_paint']['percentiles']
{'p75': 2539}
>>> # A response code outside the 200 range triggers an exception
>>> response = client.request(Request(
...     client,
...     'asdf',
...     method='POST',
...     body={'url': 'https://www.python.org/'}
... ))
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/rest_client_framework/client.py", line 166, in request
    result = self.handle_response(
  File "/rest_client_framework/client.py", line 96, in handle_response
    raise ServiceResponseError(request, response)
rest_client_framework.exceptions.ServiceResponseError: The request failed with HTTP status 404.
>>> response = client.request(Request(
...     client,
...     'records:queryRecord',
...     method='POST',
...     body={'url': 'https://foo.bar/'}
... ))
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/rest_client_framework/client.py", line 166, in request
    result = self.handle_response(
  File "/rest_client_framework/client.py", line 96, in handle_response
    raise ServiceResponseError(request, response)
rest_client_framework.exceptions.ServiceResponseError: The request failed with HTTP status 404.
```

Of course, this isn't all that much easier than simply using the `requests` library directly. The real benefits of using this framework come from going a bit deeper. For simplicity's sake, all of the following definitions will take place in the same scope, although in the real world it may be desirable to create separate modules for the `Client` subclass, the `Request` subclass(es), and the `Response` subclass(es).

```python
from rest_client_framework import Client
from rest_client_framework.request import JsonRequest
from rest_client_framework.response import JsonRestResponse
from rest_client_framework.rest import RestObject

class HistogramBin(RestObject):
    property_map = {
        'start': None,
        'end': None,
        'density': None
    }

class Metric(RestObject):
    property_map = {
        RestObject.__types__: {
            'histogram': HistogramBin
        },
        'histogram': None,
        'percentiles': {
            'p75': 'percentile75'
        }
    }

class ChromeUXRecord(RestObject):
    property_map = {
        RestObject.__types__: {
            'first_contentful_paint': Metric,
            'largest_contentful_paint': Metric,
            'cumulative_layout_shift': Metric,
            'first_input_delay': Metric
        },
        'record': {
            'key': {
                'url': None,
                'formFactor': None,
                'effectiveConnectionType': None
            },
            'metrics': {
                'first_contentful_paint': None,
                'largest_contentful_paint': None,
                'cumulative_layout_shift': None,
                'first_input_delay': None
            }
        }
    }

class QueryRecordRequest(JsonRequest):
    def __init__(self, client, url, *args, **kwargs):
        kwargs['key'] = client.key
        super().__init__(client, 'records:queryRecord', method='POST', body={
            'url': url
        }, *args, **kwargs)

class QueryRecordResponse(JsonRestResponse):
    REST_CLASS = ChromeUXRecord

class ChromeUXReportAPIClient(Client):
    base_url = 'https://chromeuxreport.googleapis.com/v1/'

    def __init__(self, key):
        self.key = key
        super().__init__()

    def query_record(self, url):
        return self.request(QueryRecordRequest(self, url), QueryRecordResponse)
```

In this version of the client, we've added a `query_record()` method that eliminates the need to deal with `request()` directly. We've also simplified the process of making the request by defining `QueryRecordRequest`, which always uses the appropriate request URL and HTTP verb, so the user only needs to pass the URL for which she wants to obtain a record. We also implemented `QueryRecordResponse`, which will not only convert the response JSON data to a `dict`, but also use that data to instantiate a `ChromeUXRecord` instance, which provides access to the response data as Python attributes. Here's how that ends up working out:

```
>>> from pprint import pprint
>>> key = 'my API key'
>>> client = ChromeUXReportAPIClient(key)
>>> response = client.query_record('https://www.cnn.com')
>>> response.instance.url
'https://www.cnn.com/'
>>> # This property was not in the response, so it was initialized as None
>>> response.instance.form_factor
>>> # The value of this attribute is a Metric instance
>>> response.instance.first_contentful_paint
<__main__.Metric object at 0x103dfee50>
>>> response.instance.first_contentful_paint.percentile75
3162
>>> # The value of this attribute is a list of HistogramBin instances
>>> pprint(response.instance.first_contentful_paint.histogram)
[<__main__.HistogramBin object at 0x103e1d1f0>,
 <__main__.HistogramBin object at 0x103e1d190>,
 <__main__.HistogramBin object at 0x103e1d220>]
>>> response.instance.first_contentful_paint.histogram[0].start
0
>>> response.instance.first_contentful_paint.histogram[0].density
0.45352676338169273
>>> pprint(response.instance.first_contentful_paint.as_rest())
{'histogram': [{'density': 0.45352676338169273, 'end': 1800, 'start': 0},
               {'density': 0.2813406703351688, 'end': 3000, 'start': 1800},
               {'density': 0.26513256628313814, 'start': 3000}],
 'percentiles': {'p75': 3162}}
```

With just a little more code than in the quick-and-dirty version, we have a more semantically friendly API client. The goal of this framework is to let you easily implement REST objects in the Python domain that have features like rich typing, default values, or anything else you can do with Python.

## Exceptions

Other than Python built-in exceptions, all exceptions raised by `rest_client_framework` are defined in `rest_client_framework.exceptions`. The base class for all of these is `RuntimeError`. The class hierarchy is as follows:

```
RuntimeError
 +-- RestRuntimeError
      +-- ServiceResponseError
      +-- MaximumAttemptsExceeded
 +-- ConfigurationError
      +-- WebServiceDefinitionError
      +-- RestDefinitionError
           +-- AttributeCollisionError
           +-- AmbiguousDatetimeFormatError
           +-- AmbiguousOrderedSequenceError
```

### `ServiceResponseError`

This is the error raised by `rest_client_framework.Client` when the remote service responds with an HTTP status of 400 or greater.

### `MaximumAttemptsExceeded`

This is the error raised by `rest_client_framework.Client` after retrying a failing request the maximum allowable number of times without receiving a successful response.

### `WebServiceDefinitionError`

This error is raised when the user attempts to extend certain base classes without providing required configuration values.

### `RestDefinitionError`

This is the common base class for several more specific errors that may result from misconfiguration of `rest_client_framework.rest.RestObject` subclasses.

## The `Client` class

The `rest_client_framework.client.Client` class handles the mechanics of issuing requests and receiving responses.

### Attributes

The `Client` class has the following class-level attributes that are intended to be user-customizable:

#### `base_url`

Default value: `None`

This should contain the common base portion of the API's URLs, which will be joined with paths specified per-request. Note that it is possible to specify full or root-relative URLs per request, so the value of this attribute can be overridden, though that isn't the general intention.

#### `max_attempts`

Default value: 3

This specifies the maximum number of times that a `Client` instance will attempt a failing request. Note that the default `Client` behavior is to never repeat any requests; subclasses must define the circumstances under which this takes place.

#### `response_class`

Default value: `None`

This specifies the default class that will be used to instantiate responses, which should be a subclass of `rest_client_framework.response.Response`. If this is left unspecified, the client will look for a module named `response` one level up from the module that defines the `Client` subclass. If found, it will attempt to import it and look for an object named `Response` in that module, which will be used as the default response class. If this operation fails, `rest_client_framework.response.Response` will be used as the default response class.

#### `request_log_level`

Default value: `logging.DEBUG`

This specifies the logging level for basic request information, which includes the request method, URL, and body (unless the user overrides this behavior; see the documentation on the `Request` class) as well as the current attempt count.

#### `request_verbose_log_level`

Default value: `logging.NOTSET`

This specifies the level at which to log each request's HTTP headers.

#### `response_log_level`

Default value: `logging.DEBUG`

This specifies the logging level for basic response information, which includes the content length and HTTP status code.

#### `response_verbose_log_level`

Default value: `logging.NOTSET`

This specifies the logging level for detailed response information, including all response HTTP headers and the full body content.

#### `verbose_name`

Default value: `None`

This attribute, if set, will be used as the return value of the `Client.get_verbose_name()` method; otherwise the value of `Client.__module__` will be used. This framework does not use this feature, but users may find it helpful.

### Methods

The behavior of `Client` subclasses may be modified by overriding certain methods, the most important of which are documented here.

#### `__init__()`

Most concrete `Client` subclasses will probably need to override the initializer to accept parameters such as authorization keys, either by accepting them as arguments or extracting them from a configuration object.

#### `get_transport()`

This method should return the mechanism to be used to perform requests, which may be anything that defines a method named `request()` that accepts the same arguments as `requests.request()`. By default, this is the `requests` module, but subclasses may override this to do things like return instances of `requests.Session` containing persistent authorization headers, or even to prevent requests from taking place at all by returning an instance of `rest_client_framework.client.NoOpTransport`.

#### `get_logger()`

This method should return the `logging.Logger` instance that the subclass should use to perform its logging. By default, this instance is identified by the subclass' module, as is standard Python practice.

#### `request(request, response_class_or_instance=None, **response_class_kwargs)`

This method is the centerpiece of the `Client` class. Subclasses may wish to override this to examine or modify requests in some way prior to calling the base method.

#### `should_skip_request(request)`

If this method returns a true value, the request will not take place. The default implementation is a no-op, but subclasses may use this to short-circuit a request based on external factors.

#### `handle_response(request, response, response_class_or_instance, **response_class_kwargs)`

This method is called after the completion of each HTTP request. If it returns an instance of `rest_client_framework.response.Response`, that value is used in turn as the return value of the `Client.request()` method. Subclasses may override this method to return `Client.RETRY` if the response has a certain characteristic (for example, if its HTTP status is in the 500 range); in this scenario, the request will be repeated, provided the total number of attempts has not yet been exceeded. The arguments passed to this method are 1) an instance of `rest_client_framework.request.Request`, 2) an instance of `requests.Response`, 3) a subclass of `rest_client_framework.response.Response` or an instance thereof, and finally any keyword arguments necessary to instantiate the final response (note that these are only used when a class is passed as the third argument, not an instance).

#### `prepare_for_retry(request)`

This hook is called after `Client.handle_response()` returns `Client.RETRY` and the number of attempts has not yet been exhausted. The default implementation is a no-op, but subclasses may use this to do things like implementing delays.

#### `finalize_request(request)`

This hook is called after a completed request that will not be retried. The default implementation is a no-op.

#### `simulate_requests(request_type=Client.REQUEST_TYPE_WRITE)`

This context manager declares a context in which read and/or write requests may be simulated for testing purposes, which means that `Client.request()` will behave as if they succeeded without actually performing any HTTP request (naturally, the response will not contain any content). The argument to this context manager should be a bitmask of the constants `Client.REQUEST_TYPE_READ` and `Client.REQUEST_TYPE_WRITE`, the value of which will be set on the `Client` instance's `simulation_context` attribute. Concrete subclasses must define behavior that examines this attribute and behaves as desired. The principal purpose of this feature is to facilitate testing.

## The `Request` class

The `rest_client_framework.request.Request` class encapsulates the characteristics of an API request.

### Properties

The `Request` class defines the following dynamically-computed properties:

#### `url`

This returns the full request URL, resolved against the base URL specified in the `Client` subclass.

#### `signature`

This returns a binary SHA1 hash incorporating the request's GET parameters (as returned by `Request.get_serializable_args()`) and body (as returned by `Request.get_serializable_body()`). This is intended to facilitate deduplication. Note that by default, the hash does not consider the request URL.

### Methods

The following methods are those most likely to require overriding in subclasses.

#### `__init__(client, path, *, method='GET', body=None, headers=None, **kwargs)`

Instantiates a request. Typically, the value of `path` will be relative to `client.base_url`, but absolute URLs may be passed as well. The value of `body` will be transformed by the `get_formatted_body()` method before it is passed to the client's transport. If `headers` is provided, it will be passed directly to the client's transport, so typically it should be a `dict` instance as expected by `requests.request()`. Any additional keyword arguments will be used as GET parameters.

#### `__str__()`

The default return value of this method includes the request method, the full request URL, and the request body (if present). The latter two attributes are returned by the `Request.get_printable_url()` and `Request.get_printable_body()` methods, which subclasses may override to remove sensitive components such as API keys.

#### `get_serializable_args()`

This method should return the request's GET parameters as suitable for deduplication hash evaluation, which may mean the removal of temporary authentication tokens. The default implementation returns the GET parameters unaltered.

#### `get_serializable_body()`

This method should return the request's body as suitable for deduplication hash evaluation, which may mean the removal of temporary authentication tokens. The default implementation returns the body unaltered.

#### `get_printable_url()`

This method should return a version of the request URL suitable for representation in logs and the like, which may require the removal of sensitive parameters like API keys. The default implementation returns the full unaltered URL.

#### `get_printable_body()`

This method should return the request body as suitable for representation in logs and the like, which may require the removal of sensitive parameters like API keys. The default implementation returns the unaltered body.

#### `get_formatted_body()`

This method should return the request body as suitable for submission in API requests. The default implementation returns the unaltered body, while `rest_client_framework.request.JsonRequest` overrides this method to convert the body to a JSON string.

#### `get_headers()`

This method should return HTTP headers to be included in the request. The default implementation returns the headers provided upon instantiation; subclasses may use this as a hook to modify them.

#### `set_basic_authentication(user, password)`

Sets a username and password for services that use basic HTTP authentication.

## Response classes

The `rest_client_framework.response` module provides a variety of classes and mixins for working with HTTP responses from REST APIs. All concrete response subclasses should inherit from `rest_client_framework.response.Response`. The base class itself does nothing more than serve as a wrapper for the `Client` instance, the `Request` instance, and the underlying HTTP response (a `requests.Response` instance). This package's subclasses provide additional functionality, and users should extend these as needed.

### `JsonResponse`

This class adds the cached property `json`, which provides more convenient access to the underlying `json()` method of the `requests.Response` instance.

### `JsonRestResponse`

In addition to the behavior defined in `JsonResponse`, this class also supports the declaration of a REST type via the `REST_CLASS` class attribute. This should be a subclass of `rest_client_framework.rest.RestObject`, and the cached property `instance` will return an instance of this class constructed from the JSON data in the HTTP response.

### `JsonSequenceRestResponse`

In addition to the behavior defined in `JsonRestResponse`, this class facilitates working with HTTP responses that contain a series of REST objects (as opposed to a single object). Subclasses should set the class attribute `CONTAINER_PROPERTY` to the key that maps to the object series in the JSON data. The `get_series_from_response()` method will iterate through this sequence to create a series of instances of the appropriate `RestObject` subclass. This class also defines `__len__()`, `__getitem__()`, and `__iter__()`.

### `CachingJsonSequenceRestResponse`

Like `JsonSequenceRestResponse`, but caches the instantiated objects in memory.

### `PagingMixin`

This mixin provides some basic logic for handling paged API responses. When a response subclass that includes this mixin is used, no HTTP request takes place until the response's `pages()` method is called. This method is a generator that performs an HTTP request on each iteration. The `get_next_request()` method, which concrete subclasses must define, will be called at the end of each iteration. If it returns a `Request` instance, it will be issued on the next iteration. If it returns `None`, the loop terminates.

## The `RestObject` class

The `rest_client_framework.rest.RestObject` class is the base class for working with REST objects in the Python domain.

### Attributes

The following configuration attributes govern the behavior of `RestObject` subclasses.

#### `property_map`

This is the single most important `RestObject` attribute. It should be a `dict` whose keys correspond to REST objects returned by the API. Each key should map to `None`, a string, or a nested `dict`. When a key maps to a string, it will be used as an instance attribute name whose value will contain the corresponding content in the remote object. If the key maps to `None`, the behavior is the same, but the attribute name will be based on the corresponding key in the remote object; depending on the value of the class-level `use_pythonic_attribute_names` attribute, the attribute name will be either the unaltered key from the remote object or an automatically-generated equivalent with Python semantics. When a key maps to a `dict`, the remote object will also be expected to contain a mapping under the corresponding key; this feature may be used to flatten remote structures. Some examples will make this easier to understand. Suppose a REST service returns the following JSON:

```
{
    "monty": "python",
    "cheeseTypes": [
        "Wensleydale",
        "Gouda",
        "Edam"
    ],
    "parrot": {
        "breed": "Norwegian Blue",
        "plumage": "beautiful",
        "pinesFor": "fjords"
    },
    "extraData": "foo"
}
```

Then, consider the following `RestObject` subclass:

```python
class MyRestObject(RestObject):
    property_map = {
        'monty': 'my_attribute_name',
        'cheeseTypes': None,
        'parrot': {
            'breed': None,
            'plumage': 'feathers',
            'pinesFor': None
        },
        'lumberjackStatus': None
    }
```

When the REST data is converted to a Python `dict` and passed as keyword arguments to `MyRestObject.__init__()` via the `**` operator, we have the following:

```
>>> obj = MyRestObject(**data)
>>> obj.my_attribute_name
'python'
>>> obj.cheese_types
['Wensleydale', 'Gouda', 'Edam']
>>> obj.breed
'Norwegian Blue'
>>> obj.feathers
'beautiful'
>>> obj.pines_for
'fjords'
>>> obj.lumberjack_status
>>> obj.extra_data
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/rest_client_framework/rest.py", line 456, in __getattr__
    raise AttributeError(name)
AttributeError: extra_data
>>> obj.extraData
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/rest_client_framework/rest.py", line 456, in __getattr__
    raise AttributeError(name)
AttributeError: extraData
```

The REST property `monty` maps to the local attribute name `my_attribute_name`, as provided in the `property_map` configuration. Because `cheeseTypes` maps to `None`, and the default value of `RestObject.use_pythonic_attribute_names` is `True`, the camel-cased name is converted to the Pythonic `cheese_types`. Because `parrot` maps to a nested mapping, the contents of the remote property are flattened, and the resulting Python attributes have the same scope as the others. Although the example REST object did not contain the `lumberjackStatus` property, because the `property_map` configuration defines it, it was initialized to a default value of `None` in the `MyRestObject` instance. Finally, although the REST data contained the property `extraData`, because it was omitted from the `property_map` configuration, it was silently discarded.

`RestObject` instances can be converted back to their REST form as well, minus any properties that were discarded upon instantiation, via the `as_rest()` method:

```
>>> from pprint import pprint
>>> pprint(obj.as_rest())
{'cheeseTypes': ['Wensleydale', 'Gouda', 'Edam'],
 'monty': 'python',
 'parrot': {'breed': 'Norwegian Blue',
            'pinesFor': 'fjords',
            'plumage': 'beautiful'}}
```

The `RestObject` class defines a series of objects that have special meanings when used as `property_map` keys.

##### `RestObject.__defaults__`

This should map to a `dict` that associates names with default values. The preferred way to declare these is to map Python attribute names to default values at the top level of `property_map`, but it's possible to nest this in a deeper node or to use remote REST property names. For example:

```python
class MyRestObject(RestObject):
    property_map = {
        RestObject.__defaults__: {
            'lumberjack_status': 'ok'
        },
        'monty': 'my_attribute_name',
        'cheeseTypes': None,
        'parrot': {
            RestObject.__defaults__: {
                'pinesFor': 'Oslo'
            },
            'breed': None,
            'plumage': 'feathers',
            'pinesFor': None
        },
        'lumberjackStatus': None
    }
```

```
>>> obj = MyRestObject(**{
...     'cheeseTypes': ['Cheddar', 'Limburger'],
...     'parrot': {
...         'breed': 'Ex-parrot',
...         'plumage': 'withering'
...     }
... })
>>> obj.lumberjack_status
'ok'
>>> obj.pines_for
'Oslo'
```

##### `RestObject.__types__`

This should map to a `dict` that associates attributes with required types. As with `RestObject.__defaults__`, the preferred practice is to set this at the top level and key it on Python attribute names, but the same flexibility is supported. This is useful for sanity checking on input data. In the examples above, `cheese_types` has been a `list`, because the instantiation data provided it as such, but the configurations we have used so far do not enforce this:

```
>>> obj = MyRestObject(cheeseTypes='Mozzarella')
>>> obj.cheese_types
'Mozzarella'
```

However, we can require that this property be a list as follows:

```python
class MyRestObject(RestObject):
    property_map = {
        RestObject.__types__: {
            'cheese_types': list
        },
        'monty': 'my_attribute_name',
        'cheeseTypes': None,
        'parrot': {
            'breed': None,
            'plumage': 'feathers',
            'pinesFor': None
        },
        'lumberjackStatus': None
    }
```

```
>>> obj = MyRestObject(cheeseTypes='Mozzarella')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/rest_client_framework/rest.py", line 411, in __init__
    set_attrs = self._set_data(kwargs or {}, self._resolved_property_map)
  File "/rest_client_framework/rest.py", line 539, in _set_data
    setattr(self, attr_name, val)
  File "/rest_client_framework/rest.py", line 441, in __setattr__
    getattr(
  File "/rest_client_framework/rest.py", line 694, in set_list_attribute
    raise TypeError('The attribute "{}" requires a list value.'.format(attr_name.lstrip('_')))
TypeError: The attribute "cheese_types" requires a list value.
```

This mechanism can also be used to instantiate nested data via `RestObject` subclasses:

```python
class ParrotInfo(RestObject):
    property_map = {
        'breed': None,
        'plumage': 'feathers',
        'pinesFor': None
    }

class MyRestObject(RestObject):
    property_map = {
        RestObject.__types__: {
            'cheese_types': list,
            'parrot': ParrotInfo
        },
        'monty': 'my_attribute_name',
        'cheeseTypes': None,
        'parrot': None,
        'lumberjackStatus': None
    }
```

```
>>> obj = MyRestObject(cheeseTypes=['Gouda', 'Cheddar'], parrot={
...     'breed': 'African Grey',
...     'pinesFor': 'Serengeti'
... })
>>> obj.parrot
<__main__.ParrotInfo object at 0x102f3bd00>
>>> obj.parrot.pines_for
'Serengeti'
```

In order to avoid circular dependency resolution issues, the REST type name may be provided as a string. If it is not a fully-qualified Python path, the discovery mechanism will look for the class in the current module:

```python
class MyRestObject(RestObject):
    property_map = {
        RestObject.__types__: {
            'cheese_types': list,
            'parrot': 'ParrotInfo'
        },
        'monty': 'my_attribute_name',
        'cheeseTypes': None,
        'parrot': None,
        'lumberjackStatus': None
    }

class ParrotInfo(RestObject):
    property_map = {
        'breed': None,
        'plumage': 'feathers',
        'pinesFor': None
    }
```

```
>>> obj = MyRestObject(parrot={'plumage': 'Majestic'})
>>> obj.parrot.feathers
'Majestic'
```

Nested REST objects are converted back to their REST form when the parent object's `as_rest()` method is executed:

```
>>> obj = MyRestObject(cheeseTypes=['Gouda', 'Cheddar'], parrot={
...     'breed': 'African Grey',
...     'pinesFor': 'Serengeti'
... })
>>> pprint(obj.as_rest())
{'cheeseTypes': ['Gouda', 'Cheddar'],
 'parrot': {'breed': 'African Grey', 'pinesFor': 'Serengeti'}}
```

Note that there is a similar `as_dict()` method, which casts the parent object as a `dict`, but not any nested REST objects:

```
>>> pprint(obj.as_dict())
{'cheeseTypes': ['Gouda', 'Cheddar'],
 'parrot': <__main__.ParrotInfo object at 0x102f41be0>}
```

Internally, to perform type-checking for types other than `RestObject` subclasses, the setter will attempt to execute a method named `set_TYPE_attribute()`, with "TYPE" replaced with the lowercase type name. `RestObject` provides setters for the following types:

* `list`
* `dict`
* `bool`
* `int`
* `float`
* `datetime.datetime`

Users may, of course, implement their own behavior for other types.

##### `RestObject.__readonly__`

This should be a list of REST properties to be treated as read-only, which means that they are excluded from the REST representation. The list may contain any Python attribute name when defined at the top level. The list may also specify REST property names, in which case it should be defined at the same level as the corresponding name in `property_map`. For example:

```python
class MyRestObject(RestObject):
    property_map = {
        RestObject.__readonly__: ['lumberjack_status'],
        'monty': 'my_attribute_name',
        'cheeseTypes': None,
        'parrot': {
            RestObject.__readonly__: ['pinesFor'],
            'breed': None,
            'plumage': 'feathers',
            'pinesFor': None
        },
        'lumberjackStatus': None
    }
```

```
>>> obj = MyRestObject(
...     lumberjackStatus='ok',
...     monty='python',
...     parrot={
...             'breed': 'Norwegian Blue',
...             'pinesFor': 'fjords'
...     }
... )
>>> obj.lumberjack_status
'ok'
>>> obj.pines_for
'fjords'
>>> obj.as_rest()
{'monty': 'python', 'parrot': {'breed': 'Norwegian Blue'}}
```

Note that even though `obj.lumberjack_status` and `obj.pines_for` were initialized with the expected values, they are excluded when converting the object back to its REST form.

##### `RestObject.__order__`

This feature can be used to control the order in which attributes are set. Consider the following `RestObject` subclass:

```python
class MyRestObject(RestObject):
    property_map = {
        'monty': 'my_attribute_name',
        'cheeseTypes': None,
        'parrot': {
            'breed': None,
            'plumage': 'feathers',
            'pinesFor': None
        },
        'lumberjackStatus': None
    }

    @property
    def feathers(self):
        return self._feathers

    @feathers.setter
    def feathers(self, val):
        self._feathers = val
        if self._feathers:
            self.description = 'Lovely bird, the {}! {} plumage.'.format(
                self.breed, self._feathers
            )
```

As a side effect of setting the `feathers` attribute (which is now a Python dynamic property), this object attempts to set the `description` attribute. However, this will fail to work as expected if the `breed` attribute has not been set. Because the order in which attributes are set is non-deterministic by default, this could cause the code to fail. However, we can ensure that `breed` is always set first as follows:

```python
class MyRestObject(RestObject):
    property_map = {
        'monty': 'my_attribute_name',
        'cheeseTypes': None,
        'parrot': {
            RestObject.__order__: ['breed'],
            'breed': None,
            'plumage': 'feathers',
            'pinesFor': None
        },
        'lumberjackStatus': None
    }

    @property
    def feathers(self):
        return self._feathers

    @feathers.setter
    def feathers(self, val):
        self._feathers = val
        if self._feathers:
            self.description = 'Lovely breed, the {}! {} plumage.'.format(
                self.breed, self._feathers
            )
```

In this situation, it isn't necessary to declare where `feathers` should fall in the order, since the only requirement is that it be set after `breed`. `RestObject.__order__` should map to a list or tuple of names. These may be either Python attribute names or REST property names, but in either case, the order must be declared at the same node level as the corresponding REST properties.

#### `use_pythonic_attribute_names`

If true, camel-case REST property names whose names are not specified in `property_map` will be converted to Python-style underscore-separated lowercase names. If false, no such conversion will take place.

#### `include_null_properties`

By default, when `RestObject` instances are converted to their REST form via `as_rest()`, attributes whose value is `None` or an empty `list` or `dict` are excluded:

```python
class MyRestObject(RestObject):
    property_map = {
        RestObject.__types__: {
            'cheeseTypes': list
        },
        'monty': 'my_attribute_name',
        'cheeseTypes': None,
        'parrot': {
            'breed': None,
            'plumage': 'feathers',
            'pinesFor': None
        },
        'lumberjackStatus': None
    }
```

```
>>> MyRestObject().as_rest()
{}
```

However, if a REST property name is declared in `include_null_properties`, it will be included in the output even if its value is empty. To exercise this preference for nested properties, use dotted path syntax. For example:

```python
class MyRestObject(RestObject):
    include_null_properties = ('cheeseTypes', 'parrot.plumage')
    property_map = {
        RestObject.__types__: {
            'cheeseTypes': list
        },
        'monty': 'my_attribute_name',
        'cheeseTypes': None,
        'parrot': {
            'breed': None,
            'plumage': 'feathers',
            'pinesFor': None
        },
        'lumberjackStatus': None
    }
```

```
>>> MyRestObject().as_rest()
{'cheeseTypes': [], 'parrot': {'plumage': None}}
```

#### `datetime_formats`

For `RestObject` subclasses that enforce the `datetime.datetime` type for any attribute values, this tuple should contain one or more `strptime`-compatible format strings. The `set_datetime_attribute()` method will iterate through these to attempt to convert string values to `datetime.datetime` instances, stopping at the first one that succeeds. For example:

```python
from datetime import datetime
class MyRestObject(RestObject):
    datetime_formats = ('%Y-%m-%d', '%m/%d/%Y %H:%M:%S')
    property_map = {
        RestObject.__types__: {
            'timestamp': datetime
        },
        'monty': 'my_attribute_name',
        'cheeseTypes': None,
        'parrot': {
            RestObject.__types__: {
                'birthday': datetime
            },
            'breed': None,
            'plumage': 'feathers',
            'pinesFor': None,
            'birthday': None
        },
        'timestamp': None
    }
```

```
>>> obj = MyRestObject(parrot={'birthday': '1976-04-10'}, timestamp='10/22/2021 13:45:00')
>>> obj.birthday
datetime.datetime(1976, 4, 10, 0, 0)
>>> obj.timestamp
datetime.datetime(2021, 10, 22, 13, 45)
```

When converting back to the REST representation, the same format that was successful at parsing a datetime will be used to convert it back to a string:

```
>>> obj.as_rest()
{'timestamp': '10/22/2021 13:45:00', 'parrot': {'birthday': '1976-04-10'}}
```

### Methods

The following are some of the important `RestObject` methods to know about.

#### `exclude_properties(*names, merge_contexts=False)`

This is a context manager for selectively omitting properties when converting to REST format. Property names should be specified via dotted path syntax. For example:

```python
class MyRestObject(RestObject):
    property_map = {
        'monty': 'my_attribute_name',
        'cheeseTypes': None,
        'parrot': {
            'breed': None,
            'plumage': 'feathers',
            'pinesFor': None
        },
        'lumberjackStatus': None
    }
```

```
>>> obj = MyRestObject(**{
...     "monty": "python",
...     "cheeseTypes": [
...         "Wensleydale",
...         "Gouda",
...         "Edam"
...     ],
...     "parrot": {
...         "breed": "Norwegian Blue",
...         "plumage": "beautiful",
...         "pinesFor": "fjords"
...     },
...     "extraData": "foo"
... })
>>> with obj.exclude_properties('monty', 'parrot.pinesFor'):
...     obj.as_rest()
...
{'cheeseTypes': ['Wensleydale', 'Gouda', 'Edam'], 'parrot': {'breed': 'Norwegian Blue', 'plumage': 'beautiful'}}
```

The `merge_contexts` parameter governs what happens when nesting contexts. By default, the inner context overrides the outer one entirely, but they can also be merged:

```
>>> with obj.exclude_properties('monty', 'parrot.pinesFor'):
...     with obj.exclude_properties('cheeseTypes'):
...         obj.as_rest()
...
{'monty': 'python', 'parrot': {'breed': 'Norwegian Blue', 'pinesFor': 'fjords', 'plumage': 'beautiful'}}
>>> with obj.exclude_properties('monty', 'parrot.pinesFor'):
...     with obj.exclude_properties('cheeseTypes', merge_contexts=True):
...         obj.as_rest()
...
{'parrot': {'breed': 'Norwegian Blue', 'plumage': 'beautiful'}}
```

#### `include_readonly()`

This is a context manager that allows REST properties that would otherwise be read-only to be included in REST representation. For example:

```python
class MyRestObject(RestObject):
    property_map = {
        RestObject.__readonly__: ['lumberjack_status'],
        'monty': 'my_attribute_name',
        'cheeseTypes': None,
        'parrot': {
            RestObject.__readonly__: ['pinesFor'],
            'breed': None,
            'plumage': 'feathers',
            'pinesFor': None
        },
        'lumberjackStatus': None
    }
```

```
>>> obj = MyRestObject(lumberjackStatus='ok', parrot={'breed': 'Norwegian Blue', 'pinesFor': 'fjords'})
>>> obj.as_rest()
{'parrot': {'breed': 'Norwegian Blue'}}
>>> with obj.include_readonly():
...     obj.as_rest()
...
{'lumberjackStatus': 'ok', 'parrot': {'breed': 'Norwegian Blue', 'pinesFor': 'fjords'}}
```

#### `is_empty(prop, val)`

Returns `True` if the given `val` should be considered empty for the given `prop`, `False` otherwise. Subclasses may wish to override this method to take their own nuances into account.

#### `format_rest_property(name, value)`

Formats the property `value` (identified by `name`) for REST representation. Subclasses may wish to override this method to take their own nuances into account.

#### `as_rest()`

Converts the instance to REST representation. Internally, this method activates a context that sets the value of the instance's `__rest__` attribute to `True`; subclasses can refer to this to make decisions about behavior.

#### `set_excluded_properties(*names)`

This method is the non-contextual equivalent of the `exclude_properties()` context manager.

### Inheritance

The configuration resolution in the `RestObject` class offers full support for inheritance. Classes descending from concrete `RestObject` subclasses will respect parents' `property_map` configurations as well as their own. Depending on their types, values in the configuration will either override or be merged with those from their parent class(es). Consider the following two class definitions:

```python
class ParentRestObject(RestObject):
    property_map = {
        RestObject.__defaults__: {
            'lumberjack_status': 'ok'
        },
        RestObject.__order__: ['monty', 'lumberjackStatus'],
        'monty': 'my_attribute_name',
        'cheeseTypes': None,
        'parrot': {
            RestObject.__defaults__: {
                'pinesFor': 'Oslo'
            },
            'breed': None,
            'plumage': 'feathers',
            'pinesFor': None
        },
        'lumberjackStatus': None
    }

class ChildRestObject(ParentRestObject):
    property_map = {
        RestObject.__defaults__: {
            'cheeseTypes': ['Wensleydale']
        },
        RestObject.__order__: ['lumberjackStatus', 'nightActivity', 'dayActivity'],
        'nightActivity': None,
        'dayActivity': None
    }

    @property
    def day_activity(self):
        return self._day_activity

    @day_activity.setter
    def day_activity(self, value):
        self._day_activity = value
        print("""I'm a lumberjack and I'm {}
I {} all night and I {} all day
""".format(self.lumberjack_status, self.night_activity, self.day_activity))
```

```
>>> obj = ChildRestObject(nightActivity='sleep', dayActivity='work', parrot={
...     'pinesFor': 'Saskatchewan'
... })
I'm a lumberjack and I'm ok
I sleep all night and I work all day

>>> obj.cheese_types
['Wensleydale']
>>> obj.my_attribute_name
>>> obj.pines_for
'Saskatchewan'
```

Instances of `ChildRestObject` will have all the attributes defined in `ParentRestObject`'s configuration, plus several others. `ChildRestObject` will apply a default value during instantiation not only for `cheeseTypes`/`cheese_types`, but also `lumberjackStatus`/`lumberjack_status`. Because of the nature of the `RestObject.__order__` configuration attribute, the internal configuration mechanism attempts to compute a merged result that respects the preferences of both the parent and the child; in this case, the ultimate order is `['monty', 'lumberjackStatus', 'nightActivity', 'dayActivity']`. If a child configuration specifies an order incompatible with the parent, an error is raised:

```python
class ParentRestObject(RestObject):
    property_map = {
        RestObject.__defaults__: {
            'lumberjack_status': 'ok'
        },
        RestObject.__order__: ['monty', 'lumberjackStatus'],
        'monty': 'my_attribute_name',
        'cheeseTypes': None,
        'parrot': {
            RestObject.__defaults__: {
                'pinesFor': 'Oslo'
            },
            'breed': None,
            'plumage': 'feathers',
            'pinesFor': None
        },
        'lumberjackStatus': None
    }

class ChildRestObject(ParentRestObject):
    property_map = {
        RestObject.__defaults__: {
            'cheeseTypes': ['Wensleydale']
        },
        RestObject.__order__: ['lumberjackStatus', 'nightActivity', 'monty'],
        'nightActivity': None,
        'dayActivity': None
    }
```

```
Traceback (most recent call last):
  File "/rest_client_framework/rest.py", line 366, in resolve_property_map
    new_class._resolved_property_map[meta_key] = cls.merge_ordered_sequences(
  File "/rest_client_framework/rest.py", line 186, in merge_ordered_sequences
    raise AmbiguousOrderedSequenceError(metadata_key)
rest_client_framework.exceptions.AmbiguousOrderedSequenceError: __order__

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/rest_client_framework/rest.py", line 83, in __new__
    cls.resolve_property_map(new_class)
  File "/rest_client_framework/rest.py", line 370, in resolve_property_map
    raise RestDefinitionError(
rest_client_framework.exceptions.RestDefinitionError: Could not merge ChildRestObject.__order__ with parents due to order conflict.
```