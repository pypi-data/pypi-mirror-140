from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import *

from pyhocon import ConfigException, ConfigTree, ConfigWrongTypeException

from dataclasses_config.util import dump_config

# noinspection PyUnreachableCode
if (False):
    # This module is always loaded after `dataclasses_config.config`
    # and thus this import statement cannot be called properly.
    # However, here it's required only for type annotations, so this is fine.
    from .config import Config

@dataclass(frozen=True)
class DataclassExceptionABC(Exception, ABC):
    """
    Base *abstract* exception class used inside this package.
    """
    
    @property
    @abstractmethod
    def message(self) -> str:
        """ An exception message. """
        pass
    
    def __post_init__(self):
        super(DataclassExceptionABC, self).__init__(self.message)
    
    def __hash__(self):
        return hash(self.message)


@dataclass(frozen=True)
class ConfigInvalidError(ConfigException, DataclassExceptionABC):
    """
    Base exception class used inside this package for Config classes.
    """
    
    cls: Type['Config']
    """ A `dataclasses_config.config.Config` which caused an exception. """
    
    config: ConfigTree
    """ A `pyhocon.ConfigTree` which caused an exception. """
    
    @property
    def dump(self) -> str:
        """ A config string representation. """
        return dump_config(self.config)
    
    @property
    def message(self) -> str:
        return f"Config for class {self.cls.__name__!r} is invalid. {self.dump}"

@dataclass(frozen=True)
class ConfigMissingKeyError(ConfigInvalidError):
    """
    This exception is raised when the config key is requested but missing.
    This exception **is not** a successor of `KeyError`
    due to the way `KeyError`s are represented.
    """
    
    key: str
    """ A config key which caused an exception. """
    
    @property
    def message(self) -> str:
        return f"Config for class {self.cls.__name__!r} does not contain a required field {self.key!r}. {self.dump}"

@dataclass(frozen=True)
class ConfigWrongPropertyTypeError(ConfigInvalidError, ConfigWrongTypeException, TypeError):
    """
    This exception is raised when the config key is requested with wrong associated type,
    i.e. when a string was discovered when integer was expected.
    This also respects `dataclasses_config.decorations.deserialize_with()` decoration.
    """
    
    key: str
    """ A config key which caused an exception. """
    
    expected_type: type
    """ The type that was expected to be extracted. """
    
    actual_value: Any
    """ Actual extracted value. Type is calculated dynamically. """
    
    @property
    def message(self) -> str:
        return f"Config for class {self.cls.__name__!r} has wrong value type for field {self.key!r}. Expected: {self.expected_type.__name__!r}, got: {type(self.actual_value).__name__!r} ({self.actual_value!r})"

@dataclass(frozen=True)
class UnsupportedTypeWarning(ConfigInvalidError, Warning, DataclassExceptionABC):
    """
    This warning is raised when Config class unsuccessfully discovered the field type
    and thus was forced to use generic, non-type-safe loader for value.
    """
    
    key: str
    """ A config key which caused an exception. """
    
    tp: Optional[type] = None
    """
    Optional.
    The type that was expected to be extracted.
    `None` means that no types were associated with that field.
    """
    
    @property
    def message(self) -> str:
        base = f"Config for class {self.cls.__name__!r} was unable to discover proper loader for field {self.key!r}."
        if (self.tp is None):
            return base + ' ' + f"No types were associated with that field."
        else:
            return base + ' ' + f"Type {self.tp.__name__!r} has no associated loader."


__all__ = \
[
    'DataclassExceptionABC',
    'ConfigWrongPropertyTypeError',
    'ConfigInvalidError',
    'ConfigMissingKeyError',
    'UnsupportedTypeWarning',
]
