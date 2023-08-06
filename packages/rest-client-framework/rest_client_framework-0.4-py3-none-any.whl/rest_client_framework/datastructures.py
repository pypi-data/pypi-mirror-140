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

from collections.abc import Mapping, Sequence, MutableSequence

def unpack_flat_structure(flat_structure, separator='.'):
    """
    Given a dict that associates structured paths (e.g. dotted paths) with
    values, unpacks these into a dict structure. For example, given the
    following...

    {
        'foo': 'bar',
        'baz.foo': 1,
        'baz.bar': None
    }

    ...this function returns the following:

    {
        'foo': 'bar',
        'baz': {
            'foo': 1,
            'bar': None
        }
    }
    """
    structure = {}
    for arg, val in flat_structure.items():
        path = arg.split(separator)
        leaf = path.pop(-1)
        prop = structure
        for path_name in path:
            try:
                prop = prop[path_name]
            except KeyError:
                prop[path_name] = {}
                prop = prop[path_name]
        prop[leaf] = val
    return structure

class FrozenMixin:
    INTERNAL_ATTRIBUTE_NAMES = ('wrapped', '_memo')

    def __init__(self, wrapped):
        self.wrapped = wrapped
        self._memo = {}

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.wrapped == other.wrapped
        return self.wrapped == other

    @classmethod
    def get_frozen_type(cls, item):
        # This method returns the appropriate wrapper type for the given item,
        # if any. The idea is to ensure that frozen items don't provide direct
        # access to mutable items. This is made a bit complex by Python's
        # orientation around duck-typing. For example, both tuples and strings
        # have characteristics of a sequence and descend from
        # collections.abc.Sequence, but where we want to wrap tuples with
        # FrozenSequence to ensure the immutability of their members, there's
        # no reason to do so with strings. This logic doesn't cover absolutely
        # every contingency but it should handle the most common cases.
        if isinstance(item, (MutableSequence, tuple)):
            return FrozenSequence
        if isinstance(item, Mapping):
            return FrozenMapping

class FrozenIndexableMixin(FrozenMixin):
    def __getitem__(self, key):
        try:
            return self._memo[key]
        except KeyError:
            item = self.wrapped[key]
            frozen_type = self.get_frozen_type(item)
            if frozen_type:
                item = frozen_type(item)
                self._memo[key] = item
            return item

    def __len__(self):
        return len(self.wrapped)

class FrozenSequence(FrozenIndexableMixin, Sequence):
    """
    A wrapper around a list-like object that delegates access calls to it but
    prevents calls that would modify it.
    """

class FrozenMapping(FrozenIndexableMixin, Mapping):
    """
    A wrapper around a dict-like object that delegates access calls to it but
    prevents calls that would modify it.
    """
    def __iter__(self):
        yield from self.wrapped

class BaseFrozenObject(FrozenMixin):
    """
    A wrapper around an arbitrary object that delegates attribute access calls
    to it but prevents calls that would set them.
    """
    def __getattr__(self, name):
        if name in self.INTERNAL_ATTRIBUTE_NAMES:
            # This would happen during initialization when something is
            # attempting to refer to an internal attribute that hasn't been
            # set yet.
            raise AttributeError(name)
        try:
            return self._memo[name]
        except KeyError:
            attr = getattr(self.wrapped, name)
            frozen_type = self.get_frozen_type(attr)
            if frozen_type:
                attr = frozen_type(attr)
                self._memo[name] = attr
            return attr

    def __setattr__(self, name, value):
        # This is slightly tricky because the internals need to set certain
        # attributes in the constructor. The last attribute that should be set
        # is _memo, so once that exists we'll begin to interrupt these calls.
        if hasattr(self, '_memo'):
            raise NotImplementedError('Cannot set attributes on frozen objects.')
        object.__setattr__(self, name, value)