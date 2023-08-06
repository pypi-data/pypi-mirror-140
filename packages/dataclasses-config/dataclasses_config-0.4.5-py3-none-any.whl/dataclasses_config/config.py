import builtins
import os
from abc import ABC
from dataclasses import fields, dataclass, Field, field, replace, MISSING
from enum import Enum
from functools import wraps
from logging import getLogger
from typing import *
from warnings import warn

import pkg_resources
from dataclasses_json import DataClassJsonMixin
from dataclasses_json.core import Json
from functional import Option
from pyhocon import ConfigTree, ConfigFactory, ConfigException, ConfigMissingException

from ._helpers import extract_generic, extract_optional
from .classes.path import Path, RelPath
from .decorations import *
# noinspection PyProtectedMember
from .decorations import _FIELD_CONSTRUCTOR_POST_INIT, _FIELD_CONSTRUCTOR_ARGUMENT_TYPE, ConstructorDataType
from .errors import *
from .settings import Settings
from .util import get_field, dump_config, wraps_class

logger = getLogger('dataclasses-config')
A = TypeVar('A')

_dataclass = wraps(dataclass)(dataclass)
HIDDEN_FIELD = '__hidden_field__'

@overload
def _hidden_field(*, default=MISSING, default_factory=MISSING, hash: bool = None, metadata: dict = None) -> Field:
    pass
def _hidden_field(*, metadata: dict = None, **kwargs) -> Field:
    metadata = metadata or dict()
    metadata.setdefault(HIDDEN_FIELD, True)
    kwargs.setdefault('init', False)
    kwargs.setdefault('compare', False)
    kwargs.setdefault('repr', False)
    
    return field(metadata=metadata, **kwargs)

T = TypeVar('T')
@dataclass
class FieldExtension(Generic[T]):
    """
    A helper class for dataclass field manipulations.
    Contains the original `dataclasses.Field` object,
    its positional index and type information.
    """
    
    base: Field
    """ An original `dataclasses.Field` object. """
    positional_index: int
    """ Positional index of the field in class (for getting/setting inside `*args`). """
    
    is_optional: bool = field(init=False)
    is_generic: bool = field(init=False)
    tp: Type[T] = field(init=False)
    """
    The unwrapped type.
    It has removed generics (i.e., `MyClass[int]` becomes `MyClass`),
    as well as removed optional (i.e., `Optional[MyClass]` becomes `MyClass`).
    """
    
    def __post_init__(self):
        tp = self.base.type
        self.is_optional, tp = extract_optional(tp)
        self.is_generic, tp, _ = extract_generic(tp)
        self.tp = tp
    
    @classmethod
    def from_class(cls, class_or_instance, filter: Union[Callable[['FieldExtension[T]'], bool], Type[T], None] = None) -> Iterator['FieldExtension[T]']:
        """
        Extracts the `dataclasses_config.config.FieldExtension`s from the given class.
        Returns an iterator.
        Ignores non-init fields.
        
        Args:
            class_or_instance: A DataClass type or DataClass instance.
             
            filter: Any of the following:
                
                - `None` *(default)*
                Nothing is filtered.
                
                - `Callable` with the signature:
                `dataclasses_config.config.FieldExtension` => `bool`
                This case, this function applies as a filter.
        
        """
        
        fields_seq = builtins.filter(lambda f: f.init, fields(class_or_instance))
        seq = (FieldExtension(f, i) for i, f in enumerate(fields_seq))
        
        if (filter is None):
            return seq
        
        elif (isinstance(filter, type)):
            _base = filter
            filter = lambda f: isinstance(f.tp, type) and issubclass(f.tp, _base)
        elif (callable(filter)):
            pass
        else:
            raise TypeError(f"Invalid type of filter argument: {filter!r} ({type(filter)!r}). Expected: type, callable or None")
        
        return builtins.filter(filter, seq)
del T

def config_class(cls: Type['Config'] = None, **kwargs):
    kwargs.setdefault('frozen', Settings.frozen)
    return dataclass(cls, **kwargs)

T = TypeVar('T')
CONFIG_TREE_READERS: List[Tuple[Type[T], ConstructorDataType]] = \
[
    (dict, ConstructorDataType.Config),
    (list, ConstructorDataType.List),
    (bool, ConstructorDataType.Boolean),
    (int,  ConstructorDataType.Integer),
    (float,ConstructorDataType.Float),
    (str,  ConstructorDataType.String),
]
"""
A global mapping storing registered basic readers for ConfigTree for basic types.
Each is a function `get_T(self: ConfigTree, key: str) -> T`.
"""
del T

@config_class
# noinspection PyDataclass
class Config(DataClassJsonMixin, ABC):
    """
    A base class for the configuration.
    Could be automatically parsed from dict, json string and `pyhocon.ConfigTree`.
    
    Automatically processes the nested classes.
    Automatically post-processes classes marked with the `dataclasses_config.decorations.deserialize_with()` decorator.
    """
    
    _config: ConfigTree = _hidden_field(default=None)
    _config_kwargs: Dict[str, Any] = _hidden_field(default_factory=dict)
    
    @classmethod
    def from_config(cls: Type[A], config: ConfigTree, **kwargs) -> A:
        """
        Class-method.
        Parses the given `pyhocon.ConfigTree` and returns the new instance of this class.
        """
        
        cls: Config
        res = cls.from_dict(config, config_kwargs=kwargs)
        object.__setattr__(res, '_config', config)
        object.__setattr__(res, '_config_kwargs', kwargs)
        return res
    
    @classmethod
    def from_dict(cls: Type[A], kvs: Json, *, config_kwargs: Dict[str, Any] = None, **kwargs) -> A:
        """
        Class-method.
        Parses the given parsed JSON-object and returns the new instance of this class.
        
        Args:
            kvs: `Dict[str, Any]`
            config_kwargs: Optional. `Dict[str, Any]`. Internal.
                `config_kwargs` are passed directly to the `dataclasses_config.config.Config.from_config()` calls
                while parsing the nested `Config`s.
            **kwargs: Extra options from the original `dataclasses_json.DataClassJsonMixin.from_dict()`.
        
        Raises:
            ConfigMissingKeyError: Raised when the config key is required but missing.
        
        """
        
        if (config_kwargs is None):
            config_kwargs = dict()
        
        config_tree: Optional[ConfigTree]
        if (isinstance(kvs, ConfigTree)):
            config_tree = kvs
        else:
            config_tree = ConfigTree(kvs)
        
        kvs = dict()
        for f in FieldExtension.from_class(cls):
            tp = f.tp
            if (isinstance(tp, type)):
                cdt: ConstructorDataType = getattr(f.tp, _FIELD_CONSTRUCTOR_ARGUMENT_TYPE, None)
                if (cdt is not None):
                    for t, _cdt in CONFIG_TREE_READERS:
                        if (cdt is _cdt):
                            tp = t
                            break
                
                if (issubclass(tp, Config)):
                    tree = config_tree.get_config(f.base.name, ConfigTree())
                    kvs[f.base.name] = tp.from_config(tree, **config_kwargs)
                    continue
                
                elif (issubclass(tp, Enum)):
                    value = kvs.get(f.base.name, None)
                    if (value is None):
                        continue
                    
                    updated = None
                    if (isinstance(value, str)):
                        try:
                            # noinspection PyUnresolvedReferences
                            updated = tp[value]
                        except ValueError:
                            pass
                    
                    if (updated is None):
                        # noinspection PyArgumentList
                        updated = tp(value)
                    
                    kvs[f.base.name] = updated
                    continue
                
                else:
                    if (cdt is None):
                        for t, _cdt in CONFIG_TREE_READERS:
                            if (issubclass(tp, t)):
                                cdt = _cdt
                                break
                    
                    if (cdt is not None):
                        try:
                            cdt: Callable[[ConfigTree, str], T]
                            v = cdt(config_tree, f.base.name)
                        except ConfigException as e:
                            try:
                                actual = config_tree.get(f.base.name)
                            except ConfigMissingException:
                                pass
                            else:
                                raise ConfigWrongPropertyTypeError(cls, config_tree, f.base.name, tp, actual) from e
                            raise
                        else:
                            kvs[f.base.name] = v
                            continue
            
            warn(UnsupportedTypeWarning(cls, config_tree, f.base.name, tp), 2)
            kvs[f.base.name] = config_tree.get(f.base.name)
        
        try:
            kvs['_config_kwargs']=config_kwargs
            return super().from_dict(kvs, **kwargs)
        except KeyError as e:
            # noinspection PyArgumentList, PyTypeChecker
            raise ConfigMissingKeyError(cls, kvs, e.args[0]) from e
    
    def __post_init__(self):
        for f in FieldExtension.from_class(self, lambda fld: hasattr(fld.tp, _FIELD_CONSTRUCTOR_ARGUMENT_TYPE)):
            v = getattr(self, f.base.name)
            
            # ToDo:
            #  - Pass self._config_kwargs through dataclasses constructor
            #  - Remove Enum workaround
            if (v is None and (f.is_optional or self._config_kwargs.get('infer_missing', False) or issubclass(f.tp, Enum))):
                continue
            
            # ToDo: Check ConstructorDataType
            cdt: ConstructorDataType = getattr(f.tp, _FIELD_CONSTRUCTOR_ARGUMENT_TYPE)
            post: PostInitFunctionType = getattr(f.tp, _FIELD_CONSTRUCTOR_POST_INIT)
            
            v = f.tp(v)
            if (post is not None):
                x = post(v, f.base.type)
                if (x is not None):
                    v = x
            
            object.__setattr__(self, f.base.name, v)
    
    # noinspection PyDataclass
    def replace(self, **changes):
        """
        Return a new object replacing specified fields with new values.
        
        This is especially useful for frozen classes.
        
        Note:
            Hidden fields (like `Config`'s `._config`) are kept as-is,
            without any modification, so try to avoid using them mindlessly.
        
        Example:
            ```python
            @dataclass(frozen=Settings.frozen)
            class C(Config):
                x: int
                y: int
            
            c = C(1, 2)
            c1 = c.replace(x=3)
            assert c1.x == 3 and c1.y == 2
            ```
        """
        
        result: Config = replace(self, **changes)
        # ToDo:
        #  (?) Create copies hidden fields, instead of copying the links
        #  (?) Update values of hidden fields according to **changes
        
        for f in fields(result): # type: Field
            if (f.metadata.get(HIDDEN_FIELD, False)):
                object.__setattr__(result, f.name, getattr(self, f.name))
        
        return result
    
    D = TypeVar('D', bound=dict)
    def asdict(self, *, dict_factory: Type[D] = dict) -> D:
        """
        Return the fields of a dataclass instance as a new dictionary mapping
        field names to field values.
        
        Args:
            dict_factory: `Type[dict]`.
                If given, `dict_factory` will be used instead of built-in dict.
                The function applies recursively to field values that are
                dataclass instances. This will also look into built-in containers:
                tuples, lists, and dicts.
                
                Default: `dict`
        
        Example:
            ```python
            @dataclass(frozen=Settings.frozen)
            class C(Config):
                x: int
                y: int
            
            c = C(1, 2)
            assert c.asdict() == { 'x': 1, 'y': 2 }
            ```
        """
        
        return dict_factory(self._asdict_iter())
    
    def _asdict_iter(self) -> Iterator[Tuple[str, Any]]:
        for f in FieldExtension.from_class(self, filter=lambda fld: fld.base.init):
            yield f.base.name, getattr(self, f.base.name)
    
    del D

T = TypeVar('T', bound=Config)
def main_config \
(
    *args,
    resources_directory: str = 'resources/',
    default_config_name: str = 'application.conf',
    reference_config_name: str = 'reference.conf',
    env_variable_name: Optional[str] = 'PYTHON_APPLICATION_CONFIG_PATH',
    root_config_path: str = None,
    module: str = None,
    log_config: bool = True,
) -> Callable[[Type[T]], Type[T]]:
    """
    Decorates the given `dataclasses_config.config.MainConfig` class with the default overrides.
    Multiple `dataclasses_config.config.main_config` directives override each other,
    and only the last is used.
    
    Args:
        *args:
        resources_directory: `str`.
            Defines where to look for the config files.
            This applies for both current directory lookup and module resources directory lookup.
            
            *Default: `resources/`*
        
        default_config_name: `str`
            Defines the default application config filename.
            It is searched in current directory and prioritized over the reference config
            when loading configuration via `dataclasses_config.config.MainConfig.default()`.
            
            *Default: `application.conf`*
        
        reference_config_name: `str`
            Defines the default reference config filename.
            It is searched in both current directory and resources directory
            when loading configuration via `dataclasses_config.config.MainConfig.default()`.
            Reference config values are fallback for values missing in the application config.
            
            *Default: `reference.conf`*
        
        env_variable_name: `Optional[str]`
            Defines the environment variable name to be used for searching default configuration.
            Could be set to None if this config could not be loaded via the environment variable.
            
            *Default: `PYTHON_APPLICATION_CONFIG_PATH`*
             
        root_config_path: Optional. `str`
            Defines the offset from the config root when loading the default and/or reference values.
            Ignored when calling `dataclasses_config.config.Config.from_config`
            
            By default, the root is used.
        
        module: Optional. `str`
            The module name resources are loaded from.
            (Reference config is loaded from the resources directory -- see above.)
            
            By default, the module from this class is used (which is get by `cls.__module__`).
        
        log_config: `bool`.
            If `True` (default), the config is logged to the `'dataclasses-config'` log
            with the INFO logging level.
    
    """
    
    def decorator(cls: Type[T]) -> Type[T]:
        @wraps_class(cls)
        @dataclass(frozen=Settings.frozen)
        class wrapper(dataclass(frozen=Settings.frozen)(cls)):
            _resources_directory: str = _hidden_field(default=resources_directory)
            _default_config_name: str = _hidden_field(default=default_config_name)
            _reference_config_name: str = _hidden_field(default=reference_config_name)
            _env_variable_name: str = _hidden_field(default=env_variable_name)
            _root_config_path: str = _hidden_field(default=root_config_path)
            _module: str = _hidden_field(default=module)
            _log: bool = _hidden_field(default=log_config)
        
        return wrapper
    
    if (args):
        return decorator(*args)
    else:
        return decorator

@main_config
class MainConfig(Config, ABC):
    """
    A `dataclasses_config.config.Config` extension which should be used
    for an application and/or module root config.
    
    This class **always** tries to load the reference config,
    whether the default config is loaded or the specific one.
    
    This reference config is then looked in current directory
    and module resources directory as a fallback.
    When loaded, it is merged with the loaded application config,
    with the application config's values prioritized.
    
    This works very similarly to the Scala's [lightbend/config](https://github.com/lightbend/config)
    
    ## See Also:
    1. Lightbend Config: https://github.com/lightbend/config
    2. Its Standard Behaviour: https://github.com/lightbend/config#standard-behavior
    """
    
    @classmethod
    def _get_module(cls) -> str:
        module: Optional[str] = get_field(cls, '_module').default
        if (module is None):
            module: str = cls.__module__
        
        return module
    
    @classmethod
    def _get_default_config_name(cls) -> str:
        return get_field(cls, '_default_config_name').default
    
    @classmethod
    def _get_reference_config_name(cls) -> str:
        return get_field(cls, '_reference_config_name').default
    
    @classmethod
    def _get_resources_directory(cls) -> str:
        return get_field(cls, '_resources_directory').default
    
    @classmethod
    def _get_env_variable_name(cls) -> Optional[str]:
        return get_field(cls, '_env_variable_name').default
    
    @classmethod
    def _get_log(cls) -> bool:
        return get_field(cls, '_log').default
    
    @classmethod
    def _get_root_config_path(cls) -> Optional[str]:
        return get_field(cls, '_root_config_path').default
    
    @classmethod
    def default(cls: Type[A]) -> A:
        """
        Tries to load the default config and merge reference config into it.
        
        If the `PYTHON_APPLICATION_CONFIG_PATH` environment variable exists and non-empty,
        then this would try to load config from this variable.
        Path might be relative and absolute.
        Raises an exception if config is missing.
        
        If such variable does not exist (or has empty value),
        then the default application config is searched.
        Search includes only resources directory in current working directory.
        Does not raise an exception if nothing is found.
        
        See `dataclasses_config.config.main_config()` for more information.
        
        Returns:
            `MainConfig`
        """
        
        cls: MainConfig
        default_config_name: str = cls._get_default_config_name()
        resources_directory: str = cls._get_resources_directory()
        
        env_var_name = cls._get_env_variable_name()
        application_conf_path = None
        if (env_var_name is not None):
            application_conf_path = os.environ.get(env_var_name, None)
        if (application_conf_path):
            ignore_missing = False
        else:
            application_conf_path = os.path.join(resources_directory, default_config_name)
            ignore_missing = True
        
        return cls.load_config(application_conf_path, ignore_missing=ignore_missing)
    
    @classmethod
    @overload
    def load_config(cls: Type[A], path: str, *, ignore_missing: bool = False, use_reference_conf: bool = True) -> A:
        pass
    
    @classmethod
    def load_config(cls: Type[A], path: str, *, ignore_missing: bool = False, use_reference_conf: bool = MISSING) -> A:
        """
        Loads the given application config and merges the reference config into it.
        Applies root config offset if any.
        
        Args:
            path: `str`.
                A path to load config from.
                Path might be relative and absolute.
            
            ignore_missing: `bool`.
                Defines whether to raise an exception if config could not be loaded (`False`, default) or not (`True`).
            
            use_reference_conf: `bool`.
                 If set to `True` (default behaviour), reference config will be merged into the config before instantiating
        
        Returns:
            `MainConfig`
        """
        
        cls: MainConfig
        kwargs = dict()
        if (use_reference_conf is not MISSING):
            kwargs['use_reference_conf'] = use_reference_conf
        
        root_config_path: Optional[str] = cls._get_root_config_path()
        
        # application.conf
        # It is environment-dependent
        try:
            application_conf: ConfigTree = ConfigFactory.parse_file(path)
        except FileNotFoundError:
            if (ignore_missing):
                application_conf = ConfigTree()
            else:
                raise
        
        if (root_config_path is not None):
            application_conf = application_conf.get_config(root_config_path, ConfigTree())
        
        return cls.from_config(application_conf, **kwargs)
    
    @classmethod
    def reference_config(cls) -> ConfigTree:
        """
        Returns the `pyhocon.ConfigTree` representing the content of reference config.
        Reference config is searched in resources directories at
        current working directory (first) and module directory (next).
        Returns empty config if nothing found.
        Applies root config offset if any.
        
        Returns:
            `pyhocon.ConfigTree`
        """
        
        reference_config_name: str = cls._get_reference_config_name()
        module: str = cls._get_module()
        resources_directory: str = cls._get_resources_directory()
        root_config_path: Optional[str] = cls._get_root_config_path()
        
        # reference.conf
        # It is built inside package resources
        try:
            expected = os.path.join(resources_directory, reference_config_name)
            reference_conf_path: str = pkg_resources.resource_filename(module, expected)
            if (not os.path.isfile(reference_conf_path)):
                reference_conf_path = expected
            reference_conf: ConfigTree = ConfigFactory.parse_file(reference_conf_path)
        except FileNotFoundError:
            reference_conf = ConfigTree()
        else:
            del reference_conf_path, expected
        
        if (root_config_path is not None):
            reference_conf = reference_conf.get_config(root_config_path, ConfigTree())
        
        return reference_conf
    
    @classmethod
    def from_config(cls: Type[A], config: ConfigTree, *, use_reference_conf: bool = True, **kwargs) -> A:
        """
        Same as the super-class' `dataclasses_config.config.Config.from_config()`,
        but merges the reference config.
        
        Optionally logs the config if such option was provided in
        `dataclasses_config.config.main_config()` parameters.
        """
        
        log: bool = cls._get_log()
        
        if (use_reference_conf):
            reference_conf = cls.reference_config()
            # The resulting config is the result of merging of reference config and application config
            config = ConfigTree.merge_configs(reference_conf, config, copy_trees=True)
        
        if (log):
            logger.info(dump_config(config))
        return super().from_config(config, **kwargs)

@dataclass(frozen=Settings.frozen)
class ConfigWithRoot(Config, ABC):
    """
    Extension to the `dataclasses_config.config.Config` which
    allows `dataclasses_config.classes.path.RelPath` post-processing.
    """
    
    root: Optional[Path]
    """ Optional. `str`. Current root directory which is used for `dataclasses_config.classes.path.RelPath` instances. """
    
    def with_root(self: A, root: Optional[Path] = None, *, default_path: str = '.', **kwargs) -> A:
        """
        Creates a copy of this class, with all instances of
        `dataclasses_config.classes.path.RelPath` transformed to their absolute path form.
        (But still remain instances of `dataclasses_config.classes.path.RelPath`)
        
        Overrides `root` field in the resulting instance.
        Should work fine with the frozen dataclasses (potentially).
        
        The first available root is applied:
        1. `root` argument.
        2. `root` field.
        3. `default_path` argument.
        
        Args:
            root: `str`.
                A first-priority root to apply.
            
            default_path: `str`.
                A fallback root to apply.
                
                *Default: `.`*
            
            **kwargs:
                Format arguments for `dataclasses_config.classes.path.RelPath.apply()`
        
        Returns:
        
        """
        
        root: Path = (Option(root) or Option(self.root)).get_or_else(Path(default_path))
        
        kvs = dict()
        for f in FieldExtension.from_class(self, RelPath):
            v = getattr(self, f.base.name)
            if (isinstance(v, RelPath)):
                kvs[f.base.name] = v.apply(root, **kwargs)
        
        kvs.setdefault('root', root)
        return self.replace(**kvs)

del A

__all__ = \
[
    'CONFIG_TREE_READERS',
    
    'config_class',
    'main_config',
    
    'Config',
    'ConfigInvalidError',
    'ConfigMissingKeyError',
    'ConfigWithRoot',
    'FieldExtension',
    'MainConfig',
]
__pdoc_extras__ = \
[
    'CONFIG_TREE_READERS',
]
