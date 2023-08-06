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

import logging, re
from contextlib import contextmanager
from copy import copy, deepcopy
from datetime import datetime
from importlib import import_module
from .datastructures import unpack_flat_structure
from .exceptions import (AmbiguousDatetimeFormatError,
    AmbiguousOrderedSequenceError, AttributeCollisionError, RestDefinitionError)

logger = logging.getLogger(__name__)
# This pattern is borrowed from django.utils.text
re_camel_case = re.compile(r'(((?<=[a-z])[A-Z])|([A-Z](?![A-Z]|$)))')

def camel_case_to_python(value):
    # Prevent capitalized values from ending up with a leading underscore
    try:
        value = value[0].lower() + value[1:]
    except IndexError:
        # Presumably this is an empty string, or else something that will cause
        # the regex substitution to fail.
        pass
    return re_camel_case.sub(r'_\1', value).lower()

class AttributeInfo:
    def __init__(self, *, rest_property_path=None, expected_type=None, default_value=None):
        self.rest_property_path = rest_property_path
        self.expected_type = expected_type
        self.default_value = default_value

    def __str__(self):
        return self.rest_property_path

    @property
    def expected_type(self):
        if isinstance(self._expected_type, tuple):
            self._expected_type = getattr(
                import_module(self._expected_type[0]),
                self._expected_type[1]
            )
        return self._expected_type

    @expected_type.setter
    def expected_type(self, expected_type):
        self._expected_type = expected_type

class MetadataKey:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return "{}('{}')".format(self.__class__.__name__, self.name)

    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        return self

class RestObjectMetaclass(type):
    def __new__(cls, *args, **kwargs):
        new_class = super().__new__(cls, *args, **kwargs)
        cls.resolve_null_inclusions(new_class)
        cls.resolve_property_map(new_class)
        return new_class

    @classmethod
    def resolve_null_inclusions(cls, new_class):
        try:
            # The wildcard is a special case
            if new_class.include_null_properties[0] == '*':
                new_class.resolved_null_inclusions = {'*': None}
                return
        except IndexError:
            pass
        try:
            new_class.resolved_null_inclusions = deepcopy(
                new_class.__mro__[1].resolved_null_inclusions
            )
        except AttributeError:
            new_class.resolved_null_inclusions = {}
        new_class_inclusions = unpack_flat_structure(
            {prop: None for prop in new_class.include_null_properties}
        )
        # Merge the two dicts with a depth-first approach so that things like
        # "foo.bar" and "foo.baz" can coexist without one clobbering the other.
        cls.merge_dicts_depth_first(new_class_inclusions, new_class.resolved_null_inclusions)

    @classmethod
    def reverse_node(cls, new_class, node):
        """
        Given a node from a property map, returns a mapping of its Python
        attribute names to ``AttributeInfo`` instances specifying fully-
        qualified REST property paths.
        """
        reversed_node = {}
        # Skip metadata keys
        for external, internal in filter(
            lambda i: not isinstance(i[0], MetadataKey),
            node.items()
        ):
            if isinstance(internal, dict):
                for node_internal, node_external in cls.reverse_node(new_class, internal).items():
                    resolved_path = '{}.{}'.format(external, node_external.rest_property_path)
                    if node_internal in reversed_node:
                        raise AttributeCollisionError(
                            node_internal,
                            reversed_node[node_internal],
                            resolved_path
                        )
                    reversed_node[node_internal] = AttributeInfo(rest_property_path=resolved_path)
            else:
                if internal is None:
                    internal = new_class._get_attribute_name(external)
                if internal in reversed_node:
                    raise AttributeCollisionError(
                        internal,
                        reversed_node[internal],
                        external
                    )
                reversed_node[internal] = AttributeInfo(rest_property_path=external)
        return reversed_node

    @classmethod
    def merge_ordered_sequences(cls, metadata_key, child_sequence, parent_sequence):
        # If both of the sequences fail to evaluate as true, there's nothing to
        # do.
        if not (child_sequence and parent_sequence):
            return child_sequence or parent_sequence
        assert isinstance(child_sequence, (list, tuple)) and isinstance(parent_sequence, (list, tuple)), \
            'Ordered sequences for merging must be lists or tuples.'
        merged_sequence = list(parent_sequence)
        pointer = 0
        sequence_length = len(child_sequence)
        last_merge_position = 0
        while True:
            try:
                value = child_sequence[pointer]
            except IndexError:
                break
            merge_slice = None
            try:
                merge_position = merged_sequence.index(value)
                pointer += 1
            except ValueError:
                # Find the position of the next item in child_sequence that's
                # also in merged_sequence.
                next_source_position = None
                merge_position = None
                for i in range(pointer + 1, sequence_length):
                    try:
                        merge_position = merged_sequence.index(child_sequence[i])
                        next_source_position = i
                        break
                    except ValueError:
                        pass
                if merge_position is None:
                    merge_position = len(merged_sequence)
                    next_source_position = sequence_length
                merge_slice = child_sequence[pointer:next_source_position]
                # Skip the next source position because we know that's in there
                # already.
                pointer = next_source_position + 1
            # If the current merge position is less than the previous one, we
            # have an order conflict.
            if merge_position < last_merge_position:
                raise AmbiguousOrderedSequenceError(metadata_key)
            last_merge_position = merge_position
            if merge_slice is not None:
                merged_sequence[merge_position:merge_position] = merge_slice
        return merged_sequence

    @classmethod
    def merge_dicts_depth_first(cls, new_dict, target_dict):
        for key, val in new_dict.items():
            try:
                target_dict_type = type(target_dict[key])
            except KeyError:
                target_dict_type = None
            if target_dict_type is dict and isinstance(val, dict):
                cls.merge_dicts_depth_first(val, target_dict[key])
            else:
                target_dict[key] = val

    @classmethod
    def standardize_meta_attribute_property_names(cls, new_class, map,
        qualified_path=''
    ):
        """
        Resolves the ambiguity created by the fact that meta properties in
        property map configurations may refer to REST property names or to
        internal Python attribute names (which may or may not match). This
        allows the user to be unconcerned with the internal implementation
        details of which style is preferred so long as the user intent is
        clear.
        """
        for required_attr_name in ('_resolved_property_map', '_reversed_property_map'):
            assert new_class.__dict__.get(required_attr_name) is not None, \
                '{}.standardize_meta_attribute_property_names() was called before {}.{} was created.'.format(
                    cls.__name__, new_class.__name__, required_attr_name
                )
        for map_key, map_value in map.items():
            if map_key is new_class.__order__ or map_key is new_class.__readonly__:
                # We ultimately want these to be REST property names defined in
                # the same node that we're examining.
                processed_value = []
                for item in map_value:
                    if item in map:
                        # This confirms the item corresponds to a REST property
                        # name at this node level.
                        processed_value.append(item)
                    else:
                        # Presumably the item is a Python property name. There
                        # are some nuances to the rules here. Setting an item
                        # as read-only by Python property name is always
                        # allowed at the top node; it's also allowed if the
                        # qualified path to the associated REST property
                        # matches the qualified path we're currently handling.
                        # However, it's not allowed to declare a Python
                        # property read-only in an arbitrary node somewhere
                        # else in the structure. Ordering must always be
                        # declared at the same node level as the corresponding
                        # REST property.
                        try:
                            rest_path = new_class._reversed_property_map[item].rest_property_path
                        except KeyError:
                            raise RestDefinitionError(
                                'Property map for {} contains unrecognized item '
                                '"{}" in {} configuration.'.format(
                                    new_class.__name__, item, map_key
                                )
                            )
                        else:
                            rest_branch, _, rest_leaf = rest_path.rpartition('.')
                            if not (
                                (rest_branch == qualified_path and rest_leaf in map) or \
                                (qualified_path == '' and map_key is new_class.__readonly__)
                            ):
                                raise RestDefinitionError(
                                    'Property map for {} specifies Python '
                                    'attribute "{}" in {} configuration at the '
                                    'incorrect node level.'.format(
                                        new_class.__name__,
                                        item,
                                        map_key
                                    )
                                )
                            if rest_branch == qualified_path:
                                processed_value.append(rest_leaf)
                            else:
                                assert map_key is new_class.__readonly__, \
                                    'Metadata property is {}; expected __readonly__'.format(map_key)
                                # Move the item to where it really belongs
                                target = map
                                for rest_key in rest_branch.split('.'):
                                    target = target[rest_key]
                                try:
                                    if not isinstance(target[map_key], set):
                                        target[map_key] = set(target[map_key])
                                except KeyError:
                                    target[map_key] = set()
                                target[map_key].add(rest_leaf)
                # Finish up by setting the processed value in the map,
                # preserving the original type.
                map[map_key] = type(map_value)(processed_value)
            elif map_key is new_class.__defaults__ or map_key is new_class.__types__:
                # It's most convenient to associate these with the Python
                # properties in the reverse property map.
                for attr_name, value in map_value.items():
                    if attr_name not in new_class._reversed_property_map:
                        try:
                            # It's possible for a REST property that maps to a
                            # Python attribute in a parent class to map instead
                            # to a deeper node in this class. If that's the
                            # case, we'll exclude this property from whichever
                            # metadata we're handling.
                            if isinstance(map[attr_name], dict):
                                continue
                            attr_name = map[attr_name] or new_class._get_attribute_name(attr_name)
                        except KeyError:
                            raise RestDefinitionError(
                                'Property map for {} specifies property name '
                                '"{}" in {} configuration at the incorrect '
                                'node level.'.format(new_class.__name__, attr_name, map_key)
                            )
                    if map_key is new_class.__types__ and isinstance(value, str):
                        # The configuration may declare the expected type as a
                        # string due to simplify the order of declarations.
                        # We can't necessarily resolve the real type yet,
                        # because the import of the defining module could still
                        # be in progress.
                        defining_module, _, target_class = value.rpartition('.')
                        value = (defining_module or new_class.__module__, target_class)
                    setattr(
                        new_class._reversed_property_map[attr_name],
                        'expected_type' if map_key is new_class.__types__ else 'default_value',
                        value
                    )
            elif isinstance(map_value, dict):
                # Recurse
                cls.standardize_meta_attribute_property_names(
                    new_class,
                    map_value,
                    qualified_path=qualified_path + ('.' if qualified_path else '') + map_key
                )

    @classmethod
    def resolve_property_map(cls, new_class):
        """
        Resolves the property map declared on ``new_class`` against its
        parents.
        """
        try:
            new_class._resolved_property_map = deepcopy(
                new_class.__mro__[1]._resolved_property_map
            )
        except AttributeError:
            new_class._resolved_property_map = {}
        # A conflicting preference for the use of Pythonic attribute names
        # between any subclass and its parent is prohibited if the parent has a
        # property map, as this creates difficult-to-resolve conflicts in
        # metadata declarations. For example, if the parent class uses Pythonic
        # attribute names but the child class doesn't, and the parent class
        # uses the Python attribute name to declare a certain default attribute
        # value, that declaration would look like a configuration error to the
        # child, because its attribute name would be resolved differently.
        if new_class._resolved_property_map and \
            new_class.use_pythonic_attribute_names != new_class.__mro__[1].use_pythonic_attribute_names:
            raise RestDefinitionError(
                '{} may not employ a different preference for Pythonic '
                'attribute names than its parent.'.format(new_class.__name__)
            )
        if new_class.property_map:
            property_map = deepcopy(new_class.property_map)
            # Merge the meta properties, attempting to preserve the order
            # implied throughout the inheritance chain if the property
            # value is an ordered sequence.
            for meta_key in filter(
                lambda k: isinstance(k, MetadataKey) and k in new_class._resolved_property_map,
                list(property_map.keys())
            ):
                meta_value = property_map.pop(meta_key)
                if isinstance(meta_value, dict):
                    new_class._resolved_property_map[meta_key].update(meta_value)
                elif isinstance(meta_value, (list, tuple)):
                    try:
                        new_class._resolved_property_map[meta_key] = cls.merge_ordered_sequences(
                            meta_key, meta_value, new_class._resolved_property_map[meta_key]
                        )
                    except AmbiguousOrderedSequenceError as e:
                        raise RestDefinitionError(
                            'Could not merge {}.{} with parents due to order conflict.'.format(
                                new_class.__name__, e
                            )
                        )
                elif isinstance(meta_value, set):
                    new_class._resolved_property_map[meta_key] |= meta_value
            new_class._resolved_property_map.update(property_map)
            # The final step will require the reversed property map. In
            # addition to making that available, this step will raise an error
            # if the configuration results in collisions of multiple REST
            # properties resolving to the same Python attribute.
            new_class._reversed_property_map = cls.reverse_node(
                new_class, new_class._resolved_property_map
            )
            cls.standardize_meta_attribute_property_names(
                new_class, new_class._resolved_property_map
            )

class RestObject(metaclass=RestObjectMetaclass):
    """
    Base class for Python representations of objects returned from REST APIs.
    """
    __order__ = MetadataKey('__order__')
    __readonly__ = MetadataKey('__readonly__')
    __defaults__ = MetadataKey('__defaults__')
    __types__ = MetadataKey('__types__')
    use_pythonic_attribute_names = True
    # This attribute controls whether scalar properties whose value is None or
    # mapping/list properties in which every value is None are included in
    # REST representations. By default, such properties are excluded, but any
    # property named in this tuple will be included regardless of value.
    # Specify nested properties using dotted path syntax. To always include
    # all such properties, populate this attribute with the value '*'.
    include_null_properties = ()
    # When a string is passed to set_datetime_attribute(), the method will
    # iterate through the formats specified here to attempt to parse it,
    # stopping the first time the parse attempt doesn't raise a ValueError.
    datetime_formats = ()
    # The property_map attribute controls the way that RESTful data structures
    # are translated into Python objects.
    property_map = None

    def __init__(self, **kwargs):
        self._attr_datetime_formats = {}
        defaults = {attr: attr_info.default_value for attr, attr_info in filter(
            lambda item: item[1].default_value is not None,
            self._reversed_property_map.items()
        )}
        self._set_data(kwargs or {}, self._resolved_property_map, defaults)
        # Where necessary, getters can check the value of this flag (which is
        # set by the _as_rest() context manager) to vary their output.
        self.__rest__ = False
        self._exclusion_context = None
        self._include_readonly = False

    def __eq__(self, other):
        if isinstance(other, RestObject):
            return self.__class__ is other.__class__ and self.as_rest() == other.as_rest()
        elif isinstance(other, dict):
            return self.as_rest() == other
        return False

    def __setattr__(self, name, value):
        # Bypass this behavior for underscore-prefixed internal attribute names
        target_type = None
        if name[0] != '_':
            target_type = self.get_expected_type(name)
        if target_type:
            name = '_' + name
            if issubclass(target_type, RestObject):
                self.set_rest_attribute(name, value, target_type)
            else:
                getattr(
                    self, 'set_{}_attribute'.format(target_type.__name__.lower())
                )(name, value)
        else:
            super().__setattr__(name, value)

    def __getattr__(self, name):
        # Also bypass this behavior for internal attribute names
        target_type = None
        if name[0] != '_':
            # Getting isn't as strict as setting; there may not be a special
            # getter to invoke.
            target_type = self.get_expected_type(name)
        if not target_type:
            # No special behavior is defined for this attribute
            raise AttributeError(name)
        name = '_' + name
        try:
            getter = getattr(
                self, 'get_{}_attribute'.format(target_type.__name__.lower())
            )
        except AttributeError:
            pass
        else:
            return getter(name)
        return getattr(self, name)

    @classmethod
    def _get_attribute_name(cls, external_name):
        return camel_case_to_python(external_name) if cls.use_pythonic_attribute_names else external_name

    @classmethod
    def get_properties(cls, node):
        """
        Returns a list of two-tuples representing properties from ``node`` in
        the appropriate order. Each tuple contains the property name as used
        externally and the name of the corresponding Python attribute, in that
        order.
        """
        try:
            props = copy(node[cls.__order__])
        except KeyError:
            props = []
        props.extend(list(set(props) ^ set(filter(
            lambda k: not isinstance(k, MetadataKey),
            node.keys()
        ))))
        resolved_props = []
        for prop in props:
            attr_name = node[prop]
            if attr_name is None or isinstance(attr_name, dict):
                attr_name = cls._get_attribute_name(prop)
            resolved_props.append((prop, attr_name))
        return resolved_props

    @classmethod
    def get_expected_type(cls, attr):
        """
        Returns the type expected as the value for the given attribute of
        instances of this class, if any.
        """
        try:
            return cls._reversed_property_map[attr].expected_type
        except KeyError:
            pass

    @classmethod
    def hasattr(cls, attr):
        return attr in cls._reversed_property_map

    def _set_data(self, data, node, defaults):
        """
        Sets properties from ``data`` as defined in ``node``, one level at a
        time, and returns a list containing the attribute names that were set
        in the order in which they were set.
        """
        set_attrs = []
        for key, attr_name in self.get_properties(node):
            # If the data is None, we will never have an explicit value for
            # anything in this node.
            got_explicit_value = data is not None
            # Upon first reading it may appear that this could be condensed;
            # however, this logic will raise a TypeError upon an attempt to
            # address a subscript of a non-subscriptable value other than None,
            # which is desirable.
            if data is None:
                val = None
            else:
                try:
                    val = data[key]
                except KeyError:
                    val = None
                    got_explicit_value = False
            if isinstance(node[key], dict):
                if val is not None and not isinstance(val, dict):
                    raise TypeError(
                        'Expected a dict as the value of the property "{}" but observed {} instance instead.'.format(
                            key, val.__class__.__name__
                        )
                    )
                set_attrs += self._set_data(val, node[key], defaults)
            else:
                if not got_explicit_value:
                    try:
                        val = defaults[attr_name]
                    except KeyError:
                        pass
                    else:
                        got_explicit_value = True
                setattr(self, attr_name, val)
                if got_explicit_value:
                    set_attrs.append(attr_name)
        return set_attrs

    def _get_data(self, node, exclusions, null_inclusions, namespace=None):
        excluded_props = [k for k, v in exclusions.items() if v is None]
        if not self._include_readonly:
            try:
                excluded_props.extend(node[self.__readonly__])
            except KeyError:
                pass
        obj = {}
        for prop, attr_name in self.get_properties(node):
            if prop in excluded_props:
                continue
            qualified_prop = '{}.{}'.format(namespace, prop) if namespace else prop
            if isinstance(node[prop], dict):
                prop_val = self._get_data(
                    node[prop],
                    exclusions.get(prop, {}),
                    null_inclusions if '*' in null_inclusions else null_inclusions.get(prop, {}),
                    qualified_prop
                )
            else:
                prop_val = getattr(self, attr_name)
                if self.__rest__:
                    prop_val = self.format_rest_property(prop, prop_val)
            if not self.is_empty(qualified_prop, prop_val) or \
                '*' in null_inclusions or (
                    # If the property is in this node of the null inclusions,
                    # but it maps to a dict, it's just providing information
                    # about a deeper node and doesn't signify anything in and
                    # of itself.
                    prop in null_inclusions and null_inclusions[prop] is None
                ):
                obj[prop] = prop_val
        if obj:
            return obj

    @contextmanager
    def _as_rest(self):
        prev = self.__rest__
        self.__rest__ = True
        try:
            yield
        finally:
            self.__rest__ = prev

    @contextmanager
    def exclude_properties(self, *names, merge_contexts=False):
        """
        Activates a context in which certain properties are excluded from the
        REST representation of this instance, even if they would normally be
        included. Nested properties should be specified using a dotted path
        syntax.
        """
        prev = self._exclusion_context
        try:
            self._exclusion_context = (deepcopy(prev) if prev else {}) if merge_contexts else {}
            self._exclusion_context.update(unpack_flat_structure(
                {name: None for name in names}
            ))
            yield
        finally:
            self._exclusion_context = prev

    @contextmanager
    def include_readonly(self):
        """
        Activates a context in which read-only properties are included in the
        REST representation of this instance.
        """
        prev = self._include_readonly
        try:
            self._include_readonly = True
            yield
        finally:
            self._include_readonly = prev

    def is_empty(self, prop, val):
        """
        Returns a boolean indicating whether the value of the given property
        should be considered empty. This implementation does not refer to
        ``prop``, but it is passed so that subclasses can take it into account.
        """
        return val is None or (isinstance(val, (list, dict)) and not val)

    def format_rest_property(self, name, value):
        """
        Formats a property for REST representation.
        """
        # If the value is a dict prior to REST formatting, ensure this method
        # gets called on all of its values.
        if isinstance(value, dict):
            for key in value:
                value[key] = self.format_rest_property(key, value[key])
        # Whether or not the object is an instance of RestObject, if it has an
        # as_rest() method, use it.
        try:
            return value.as_rest()
        except AttributeError:
            pass
        if isinstance(value, list):
            resolved_list = []
            for item in value:
                try:
                    item = item.as_rest()
                except AttributeError:
                    pass
                # Lists are something of a special case. I can't
                # see a use case for loading up a list with nulls,
                # regardless of what the null inclusions say.
                if item is not None:
                    resolved_list.append(item)
            return resolved_list
        return value

    def as_dict(self):
        return self._get_data(
            self._resolved_property_map,
            self._exclusion_context or {},
            self.resolved_null_inclusions
        ) or {}

    def as_rest(self):
        with self._as_rest():
            return self.as_dict()

    def cast_as_rest_type(self, val, rest_type):
        if isinstance(val, dict):
            return rest_type(**val)
        elif isinstance(val, list):
            return [self.cast_as_rest_type(item, rest_type) for item in val]
        elif isinstance(val, rest_type):
            return val
        raise TypeError('Unable to cast object of type {}.'.format(val.__class__.__name__))

    def handle_datetime_value(self, raw_val, parsed_val):
        """
        This method is a no-op in this context. It exists to provide
        subclasses a chance to do things like set the time zone of a parsed
        datetime.
        """
        return parsed_val

    def get_list_attribute(self, attr_name):
        if getattr(self, attr_name, None) is None:
            setattr(self, attr_name, [])
        return getattr(self, attr_name)

    def set_list_attribute(self, attr_name, val, rest_type=None, sort=None):
        if isinstance(val, tuple):
            val = list(val)
        elif val is not None and not isinstance(val, list):
            raise TypeError('The attribute "{}" requires a list value.'.format(attr_name.lstrip('_')))
        if rest_type and val:
            val = self.cast_as_rest_type(val, rest_type)
        if val and sort:
            if sort is True:
                val.sort()
            else:
                val.sort(key=sort)
        setattr(self, attr_name, val)

    def get_dict_attribute(self, attr_name):
        if getattr(self, attr_name, None) is None:
            setattr(self, attr_name, {})
        return getattr(self, attr_name)

    def get_datetime_attribute(self, attr_name):
        value = getattr(self, attr_name)
        if value and self.__rest__:
            try:
                value = value.strftime(self._attr_datetime_formats[attr_name])
            except KeyError:
                # We don't know the datetime format that was originally used
                # to parse this value. Default to the first format declared
                # for the class.
                try:
                    value = value.strftime(self.datetime_formats[0])
                except IndexError:
                    raise AmbiguousDatetimeFormatError(
                        'Cannot format a datetime in a REST context without '
                        'a format declaration.'
                    )
        return value

    def set_dict_attribute(self, attr_name, val):
        if val is not None and not isinstance(val, dict):
            raise TypeError('The attribute "{}" requires a dict value.'.format(attr_name.lstrip('_')))
        setattr(self, attr_name, val)

    def set_rest_attribute(self, attr_name, val, rest_type):
        if val is not None:
            try:
                val = self.cast_as_rest_type(val, rest_type)
            except TypeError:
                logger.debug('Caught error attempting to set value of "{}" to {!r}.'.format(
                    attr_name, val
                ))
                raise
        setattr(self, attr_name, val)

    def set_bool_attribute(self, attr_name, val):
        setattr(self, attr_name, bool(val))

    def set_int_attribute(self, attr_name, val):
        if val is not None and not isinstance(val, int):
            try:
                val = int(val)
            except ValueError:
                raise TypeError('The attribute "{}" requires an int value.'.format(attr_name.lstrip('_')))
        setattr(self, attr_name, val)

    def set_float_attribute(self, attr_name, val):
        if val is not None and not isinstance(val, float):
            try:
                val = float(val)
            except ValueError:
                raise TypeError('The attribute "{}" requires a float value.'.format(attr_name.lstrip('_')))
        setattr(self, attr_name, val)

    def set_datetime_attribute(self, attr_name, val):
        if val is not None:
            raw_val = val
            if not isinstance(val, datetime):
                for datetime_format in self.datetime_formats:
                    try:
                        val = datetime.strptime(val, datetime_format)
                    except ValueError:
                        pass
                    else:
                        # Make a note of the format that worked
                        self._attr_datetime_formats[attr_name] = datetime_format
                        break
            if isinstance(val, datetime):
                val = self.handle_datetime_value(raw_val, val)
            else:
                raise ValueError(
                    'Could not parse the value "{}" as a datetime instance.'.format(raw_val)
                )
        setattr(self, attr_name, val)

    def set_excluded_properties(self, *names):
        """
        Flags certain properties as excluded in the same way as the
        ``exclude_properties()`` context manager, but in a non-contextual way.
        """
        self._exclusion_context = unpack_flat_structure({name: None for name in names}) or None
