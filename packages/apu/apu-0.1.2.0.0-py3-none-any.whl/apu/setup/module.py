""" check if a module is installed and import the module if
the module exists """
from importlib.util import find_spec, module_from_spec

try:  # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError:  # for pip <= 9.0.3
    from pip.req import parse_requirements

from apu.exception.module import ModuleNotImportedError


class Module:
    """in this class all module containing functions are placed."""
    @staticmethod
    def check(module_name: str):
        """ check if a module exists without importing it

        Arguments:
            module_name(str): module name

        Returns:
            (ModuleSpec): Module specification

        Raises:
            ModuleNotFoundError: Module not found
            AttributeError: given attribute error

        """
        try:
            module_spec = find_spec(module_name)
        except ModuleNotFoundError as mnfe:
            raise ModuleNotFoundError(f"{module_name} not found") from mnfe
        except AttributeError as ate:
            raise AttributeError(f"{module_name} attribute not valid") from ate

        if module_spec is not None:
            return module_spec

        raise ModuleNotFoundError(f"{module_name} not found")

    @staticmethod
    def import_module_from_spec(module_name: str):
        """If the module is found utilizing check_module

        Arguments:
            module_name(str): name of the module to import

        Returns:
            (module): imported module

        Raises:
            ModuleNotImportedError: cannot import module
            ModuleNotFoundError: cannot find the module.
                                 install the module first
            AttributeError: given attribute for the module
                            check is not valid
        """
        try:
            module_spec = Module.check(module_name)

            if module_spec:
                module = module_from_spec(module_spec)
                module_spec.loader.exec_module(module)
                return module
            raise ModuleNotImportedError(f"{module_name} not imported!!")
        except ModuleNotFoundError as mnf:
            raise ModuleNotFoundError(f"{module_name} not found") from mnf
        except AttributeError as ate:
            raise AttributeError(f"{module_name} attribute not valid") from ate

    # pylint: disable=W0702
    @staticmethod
    def load_requirements(fname):
        """ install missing pip packages """
        reqs = parse_requirements(fname, session=False)
        try:
            return [str(ir.requirement) for ir in reqs]
        except:
            return [str(ir.req) for ir in reqs]
