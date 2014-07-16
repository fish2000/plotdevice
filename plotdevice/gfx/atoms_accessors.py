

class Attribute(object):
    
    default = None
    
    def __init__(self, name):
        self.name = name
    
    def __get__(self, instance=None, cls=None):
        ''' Either instance or cls gets passed,
            depending on whether the attribute is accessed
            as a class property or an instance property. '''
        if instance is None:
            # accessed off of the attributes' owner class,
            # return the default (which is None if unspecified)
            return cls.default
        return self.get_base(instance)
    
    def __set__(self, instance, value):
        self.set_base(instance, value)
    
    def get_base(self, instance):
        if hasattr(self, 'get'):
            return self.get(instance) # undefined in base class
        return getattr(instance, self.name)
    
    def set_base(self, instance, value):
        if hasattr(self, 'set'):
            self.set(instance, value) # undefined in base class
        setattr(instance, self.name, value)

class ContextAttribute(Attribute):
    pass

class StateAttribute(Attribute):
    pass

# e.g.
class ColorAttribute(ContextAttribute):
    default = Color("#000000")
    def set(self, instance, value):
        ''' This can be whatever (doesn't have to inspect the instance) '''
        setattr(instance, self.name, Color(value))

class Grob(object):
    ''' INSERT ALL THAT GROB SHIT HERE '''
    pass

class ColorMixin(Grob):
    
