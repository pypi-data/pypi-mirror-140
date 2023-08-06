__version__ = '0.4.0'

#from typing import TYPE_CHECKING
"""
class _ModuleProxy:
    _module = None
    def __init__(self,name):
        self.__dict__['_module_name'] = name
    def __getattr__(self,name):
        try:
            return getattr(self._module,name)
        except AttributeError:
            if self._module is not None:
                raise
            import_name = 'cco.{}'.format(self._module_name)
            __import__(import_name)
            module = sys.modules[import_name]
            object.__setattr__(self,'module',module)
            globals()[self._module_name] = module
            return getattr(module,name)

    def __setattr__(self,name,value):
        try:
            setattr(self._module,name,value)
        except AttributeError:
            if self._module is not None:
                raise
            import_name = 'cco.{}'.format(self._module_name)
            __import__(import_name)
            module = sys.modules[import_name]
            object.__setattr__(self,'module',module)
            globals()[self._module_name] = module 
            return getattr(module,name)
"""
#if TYPE_CHECKING:
from . import implicit
from . import collision
from . import branch_addition
from . import sv_interface

from .tree import tree,forest
from .implicit.implicit import surface
from .implicit.tests.bumpy_sphere import bumpy_sphere
#else:
#    implicit = _ModuleProxy('implicit')
#    collision = _ModuleProxy('collision')
#    branch_addition = _ModuleProxy('branch_addition')
#    sv_interface = _ModuleProxy('sv_interface')

