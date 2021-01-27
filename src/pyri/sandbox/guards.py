from RestrictedPython.Guards import safe_builtins as safe_builtins_zope, guarded_iter_unpack_sequence
from RestrictedPython.Utilities import utility_builtins
import copy
import builtins
import math
import random
import string

# TODO: Do implicit conversions and iterators need to be guarded? Currently unguarded

# Builtins that are unsafe for use on an untrusted user on a server
# but are necessary for robotics software

_pyri_safe_names = [
    'dict',
    'iter',
    'list',
    'max',
    'min',
    'sum',
    'all',
    'any',
    'bytearray',
    'bytes'
]

class PyriGuards:
    def __init__(self):
        self.safe_builtins = copy.deepcopy(safe_builtins_zope)

        for name in _pyri_safe_names:
            self.safe_builtins[name] = getattr(builtins, name)

        self.safe_builtins.update(utility_builtins)   
        del self.safe_builtins['whrandom']
        del self.safe_builtins['same_type']
        del self.safe_builtins['test']
        del self.safe_builtins['reorder']

        self.safe_builtins['setattr'] = self.guarded_setattr
        self.safe_builtins['delattr'] = self.guarded_delattr
        self.safe_builtins['_getattr_'] = self.guarded_getattr
        self.safe_builtins['getattr'] = self.guarded_getattr
        self.safe_builtins['hasattr'] = self.guarded_hasattr
        self.safe_builtins['_getitem_'] = self.guarded_getitem
        self.safe_builtins['_getiter_'] = self.guarded_getiter
        self.safe_builtins['_write_'] = self.full_write_guard()
        self.safe_builtins['_check_return_'] = self.check_return
        self.safe_builtins['_check_unary_op_allowed_'] = self.check_unary_op_allowed
        self.safe_builtins['_check_binary_op_allowed_'] = self.check_binary_op_allowed
        self.safe_builtins['_check_bool_op_allowed_'] = self.check_bool_op_allowed
        self.safe_builtins['_check_compare_allowed_'] = self.check_compare_allowed
        self.safe_builtins['_iter_unpack_sequence_'] = guarded_iter_unpack_sequence
        del self.safe_builtins["__build_class__"]
                
        self.safetypes = {dict, list, int, float, complex, str, set, frozenset, bool, bytes, bytearray, tuple,math,random,string}

    def _is_safe(self, ob):
        # Don't bother wrapping simple types, or objects that claim to
        # handle their own write security.
        return ob is None or type(ob) in self.safetypes or ob in self.safetypes or hasattr(ob, '_pyri_object')

    # Taken from RestrictedPython _full_write_guard, modified for use here
    def _write_wrapper(self):
        # Construct the write wrapper class
        def _handler(secattr, error_msg):
            # Make a class method.
            def handler(self1, *args):
                try:
                    f = getattr(self1.ob, secattr)
                except AttributeError:
                    raise TypeError(error_msg)
                f(*args)
            return handler

        class Wrapper(object):
            def __init__(self, ob):
                self.__dict__['ob'] = ob

            __setitem__ = _handler(
                '_pyri_setitem_',
                'object does not support item or slice assignment')

            __delitem__ = _handler(
                '_pyri_delitem_',
                'object does not support item or slice assignment')

            __setattr__ = _handler(
                '_pyri_setattr_',
                'attribute-less object (assign or del)')

            __delattr__ = _handler(
                '_pyri_delattr_',
                'attribute-less object (assign or del)')
        return Wrapper

    # Taken from RestrictedPython _full_write_guard, modified for use here
    def full_write_guard(self):
        # Nested scope abuse!
        # safetypes and Wrapper variables are used by guard()
        Wrapper = self._write_wrapper()

        def guard(ob):
            if self._is_safe(ob):
                return ob
            # Hand the object to the Wrapper instance, then return the instance.
            return Wrapper(ob)
        return guard


    def guarded_setattr(self, object, name, value):
        setattr(self, self.full_write_guard(object), name, value)

    def guarded_delattr(self, object, name):
        delattr(self.full_write_guard(object), name)

    def guarded_hasattr(self, ob, name, hasattr=hasattr):
        """Getattr implementation which prevents using format on string objects.
        format() is considered harmful:
        http://lucumr.pocoo.org/2016/12/29/careful-with-str-format/
        """
        if isinstance(ob, str) and name == 'format':
            raise NotImplementedError(
                'Using format() on a %s is not safe.' % ob.__class__.__name__)
        if name.startswith('_'):
            raise AttributeError(
                '"{name}" is an invalid attribute name because it '
                'starts with "_"'.format(name=name)
            )
        
        if self._is_safe(ob):
            return hasattr(ob, name)

        try:
            f = getattr(ob, '_pyri_getattr_')
        except AttributeError:
            return False
        try:
            f(name)
            return True
        except AttributeError:
            return False

    def guarded_getattr(self, ob, name, default=None, getattr=getattr):
        """Getattr implementation which prevents using format on string objects.
        format() is considered harmful:
        http://lucumr.pocoo.org/2016/12/29/careful-with-str-format/
        """
        if isinstance(ob, str) and name == 'format':
            raise NotImplementedError(
                'Using format() on a %s is not safe.' % ob.__class__.__name__)
        if name.startswith('_'):
            raise AttributeError(
                '"{name}" is an invalid attribute name because it '
                'starts with "_"'.format(name=name)
            )
        
        if self._is_safe(ob):
            return getattr(ob, name, default)

        try:
            f = getattr(ob, '_pyri_getattr_')
        except AttributeError:
            raise TypeError('attribute-less object (get)')

        return f(name, default)
    

    def guarded_getitem(self, ob, index):
        if self._is_safe(ob):
            return ob[index]

        try:
            f = getattr(ob, '_pyri_getitem_')
        except AttributeError:
            raise TypeError('attribute-less object (get)')

        return f(index)

    def guarded_getiter(self,ob):
        # No retrictions
        return ob

    def check_return(self, val):
        return val

    def check_unary_op_allowed(self, ob):
        if self._is_safe(ob):
            return ob
        if hasattr(ob, '_pyri_compare_op_'):
            return ob
        raise TypeError('object does not support compare operators')

    def check_binary_op_allowed(self, ob):
        if self._is_safe(ob):
            return ob
        if hasattr(ob, '_pyri_binary_op_'):
            return ob
        raise TypeError('object does not support binary operators')

    def check_bool_op_allowed(self, ob):
        if self._is_safe(ob):
            return ob
        if hasattr(ob, '_pyri_bool_op_'):
            return ob
        raise TypeError('object does not support boolean operators')

    def check_compare_allowed(self, ob):
        if self._is_safe(ob):
            return ob
        if hasattr(ob, '_pyri_compare_op_'):
            return ob
        raise TypeError('object does not support compare')


def get_pyri_bultins():
    guards = PyriGuards()
    return guards.safe_builtins

def get_assign_name_guard(protected_names):
    def _check_assign_name(name):
        if name in protected_names:
            raise AssertionError("Attempt to overwrite reserved name {0}".format(name))

    return _check_assign_name

def append_assign_name_guard(builtins_, extra_protected_names):

    names = []
    for n in builtins_.keys():
        if not n.startswith('_'):
            names.append(n)

    names.extend(extra_protected_names)
    builtins_['_check_assign_name_'] = get_assign_name_guard(names)
    return builtins_

def get_pyri_builtins_with_name_guard(extra_protected_names = []):
    builtins_ = get_pyri_bultins()
    return append_assign_name_guard(builtins_, extra_protected_names)