# type(name, bases, attrs) | 
#   name: class name, 
#   bases: tuple of parent class (may be empty), 
#   attrs: a dict containing class attributes (members)
# this function can be used to create classes without the class keyword ex.:
# BaseCls = type('SomeCls', (), {})
# ConcreteCls = type('ConcreteCls', (BaseCls,), {})
# Metaclasses is a callable with all data required to create a class object
# the type function is a metaclass used to create all classes behind the scenes.
# see foo.__class__.__class__ for class of class for any object
# It is possible to create your own metaclass instead of using type
# Adding metaclass=SomeMetaCls to class parameters 
# instructs Python to use that custom metaclass for that class or fallback to type.
# 
class UpperAttrMetaclass(type):
    def __new__(upper_attr_metaclass, future_cls_name, future_cls_parents, future_cls_attrs):
        modified_attrs = {
            key if key.startswith("__") else key.upper(): value
            for key, value in future_cls_attrs.items()
        }
        # for improper OOP: not overriding the parent's __new__
        return type(future_cls_name, future_cls_parents, modified_attrs)
        # for proper OOP: overriding the parent's __new__
        return type.__new__(upper_attr_metaclass, future_cls_name, future_cls_parents, modified_attrs)
        # for proper OOP: supports any tier in inheritance hierarchy of metaclasses
        return super(UpperAttrMetaclass, cls).__new__(
            upper_attr_metaclass, future_cls_name, future_cls_parents, modified_attrs)
        
