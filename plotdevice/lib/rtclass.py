
from __future__ import print_function

import objc, warnings

OBJ_COLON = '_'

class RTClass(object):
    class __metaclass__(type):
        """ Subclass RTClass using the name of an Objective-C class
            to generate a pythonic wrapper (if you like your syntax sweet)
        """
        def __new__(cls, name, bases, attrs):
            create = super(RTClass, cls).__new__
            try:
                cls.__rtbase__ = objc.lookUpClass(name)
            except objc.nosuchclass_error:
                warnings.warn("RTClass: Objective-C class '%s' not found" % name)
                return create(name, bases, attrs)
            return create(name, tuple([cls.__rtbase__] + list(bases)), attrs)
    
    def __new__(cls, *args, **kwargs):
        """ Allow PyObjC-based RTClass subclasses to initialize pythonically e.g.
            
                nsarray = NSArray() # or:
                nsarray = NSArray(other_nsarray,
                    init='initWithArray')
            
            rather than having to do the ObjC allocation/initialization dance:
            
                nsarray = NSArray.alloc().initWithArray_(other_nsarray) # bah
        """
        if hasattr(cls, '__rtbase__'):
            init_method_name = kwargs.pop('init', 'init')
            instance = cls.alloc()
            init_method = getattr(instance, init_method_name)
            return init_method(*args)
        return super(RTClass, cls).__new__(cls, *args, **kwargs)
    
    def __getattr__(self, attr):
        """ For unknown attributes that don't end in underscores,
            look for their underscored counterpart before bailing. """
        if not attr.endswith(OBJ_COLON):
            alt_attr = attr + OBJ_COLON
            if hasattr(self, alt_attr):
                return getattr(self, alt_attr)
            raise AttributeError('%s (tried with underscore)' % attr)
        raise AttributeError(attr)
    
    def __repr__(self):
        # This may be a bad idea, let's find out
        return "(%s) ->> %s" % (
            self.__class__.__name__,
            super(RTClass, self).__repr__())

