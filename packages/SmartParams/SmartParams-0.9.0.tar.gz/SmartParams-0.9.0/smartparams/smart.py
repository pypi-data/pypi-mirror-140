import inspect
import os
import re
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Iterable,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    get_args,
    get_origin,
)

from smartparams.cli import Print, parse_arguments
from smartparams.io import load_data, print_data, save_data
from smartparams.utils import (
    check_key_is_in,
    check_missings,
    check_overrides,
    check_typings,
    convert_to_primitive_types,
    flatten_keys,
    get_class_name,
    get_nested_dictionary_and_key,
    import_class,
    join_classes,
    join_keys,
    parse_class,
    parse_param,
    remove_duplicated_key_and_value,
    str_to_bool,
)

_T = TypeVar('_T')


class Smart(Generic[_T]):
    """Creates a partial wrapper for a class that can be configurable from a file or a cli.

    Smart class has functionality of both partial and dict classes. It allows creating
    objects with lazy instantiating. This makes possible injecting values from config
    file or command line.

    Examples:
        # script.py
        from dataclasses import dataclass
        from pathlib import Path

        from smartparams import Smart


        @dataclass
        class Params:
            value: str


        def main(smart: Smart[Params]) -> None:
            params = smart()
            # do some stuff ...


        if __name__ == '__main__':
            Smart.strict = True
            Smart(Params).run(
                function=main,
                path=Path('params.yaml'),
            )

        #  Run in command line:
        #    $ python script.py value="Some value"
        #    $ python script.py --dump
        #    $ python script.py
        #    $ python script.py --print keys
        #    $ python script.py --help


    Attributes:
        keyword: Name of the key containing the value with the path of the class to be imported.
            Can be set by env variable SMARTPARAMS_KEYWORD, default 'class'.
        missing_value: Value assigned to unknown types when creating a representation.
            Can be set by env variable SMARTPARAMS_MISSING_VALUE, default '???'.
        check_missings: Whether to check missing values before instantiating object.
            Can be set by env variable SMARTPARAMS_CHECK_MISSINGS, default 'true'.
        check_typings: Whether to check arguments type before instantiating object.
            Can be set by env variable SMARTPARAMS_CHECK_TYPINGS, default 'true'.
        check_overrides: Whether to check override arguments before instantiating object.
            Can be set by env variable SMARTPARAMS_CHECK_OVERRIDES, default 'true'.
        allow_only_registered_classes: Whether to allow import only registered classes.
            Can be set by env variable SMARTPARAMS_ALLOW_ONLY_REGISTERED_CLASSES, default 'false'.
        strict: Whether to raise exceptions instead of warnings.
            Can be set by env variable SMARTPARAMS_STRICT, default 'false'.

    """

    keyword: str = os.getenv('SMARTPARAMS_KEYWORD', default='class')
    missing_value: str = os.getenv('SMARTPARAMS_MISSING_VALUE', default='???')

    check_missings: bool = str_to_bool(os.getenv('SMARTPARAMS_CHECK_MISSINGS', default='true'))
    check_typings: bool = str_to_bool(os.getenv('SMARTPARAMS_CHECK_TYPINGS', default='true'))
    check_overrides: bool = str_to_bool(os.getenv('SMARTPARAMS_CHECK_OVERRIDES', default='true'))

    allow_only_registered_classes: bool = str_to_bool(
        os.getenv('SMARTPARAMS_ALLOW_ONLY_REGISTERED_CLASSES', default='false'),
    )

    strict: bool = str_to_bool(os.getenv('SMARTPARAMS_STRICT', default='false'))

    _aliases: Dict[str, str] = dict()
    _origins: Dict[str, str] = dict()

    def __init__(
        self,
        _type: Type[Union[_T, Dict]] = dict,
        /,
        **kwargs: Any,
    ) -> None:
        """Creates instance of Smart class.

        Args:
            _type: Class to be wrapped.
            **kwargs: Partial keyword arguments to be passed to the class constructor.

        """
        self._type: Type[Union[_T, Dict]] = _type
        self._dict: Dict[str, Any] = dict()

        self._location: str = ''

        for k, v in kwargs.items():
            self.set(k, v)

    @property
    def type(self) -> Type[Union[_T, Dict]]:
        return self._type

    @property
    def dict(self) -> Dict[str, Any]:
        return self._dict.copy()

    def __call__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> _T:
        """Creates instance of given type.

        Args:
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            An class instance.

        """
        params = self._init_dict(
            dictionary=self._dict,
            location=self._location,
        )

        if self.check_overrides:
            check_overrides(
                location=join_classes(self._location, get_class_name(self._type)),
                params=params,
                kwargs=kwargs,
                raise_error=self.strict,
            )

        params.update(kwargs)

        return self._init_class(
            location=self._location,
            cls=self._type,
            args=args,
            kwargs=params,
        )

    def __str__(self) -> str:
        cls_str = "" if self._type is dict else f"[{get_class_name(self._type)}]"
        params_str = ", ".join((f"{k}={v}" for k, v in self._dict.items()))
        return f"{self.__class__.__name__}{cls_str}({params_str})"

    def __repr__(self) -> str:
        return str(self)

    def keys(
        self,
        flatten: bool = False,
        pattern: Optional[str] = None,
    ) -> Iterable[str]:
        """Generates keys existing in the dictionary.

        Args:
            flatten: Whether to return the flattened keys in the nested dictionaries.
            pattern: Regex pattern for filtering keys.

        Yields:
            Keys from dictionary.

        """
        keys = flatten_keys(self._dict) if flatten else self._dict
        if pattern is None:
            yield from keys
        else:
            yield from (key for key in keys if re.fullmatch(pattern, key))

    def values(
        self,
        flatten: bool = False,
        pattern: Optional[str] = None,
    ) -> Iterable[Any]:
        """Generates values existing in the dictionary.

        Args:
            flatten: Whether to return the values in the nested dictionaries.
            pattern: Regex pattern for filtering values by key.

        Yields:
            Values from dictionary.

        """
        return (self.get(k) for k in self.keys(flatten, pattern))

    def items(
        self,
        flatten: bool = False,
        pattern: Optional[str] = None,
    ) -> Iterable[Tuple[str, Any]]:
        """Generates items existing in the dictionary.

        Args:
            flatten: Whether to return the items in the nested dictionaries.
            pattern: Regex pattern for filtering items by key.

        Yields:
            Items from dictionary.

        """
        return ((k, self.get(k)) for k in self.keys(flatten, pattern))

    def isin(
        self,
        name: str,
    ) -> bool:
        """Checks if name is in dictionary.

        Args:
            name: The key to be checked.

        Returns:
            True if name is in dictionary, otherwise False.

        """
        return check_key_is_in(name, self._dict)

    def get(
        self,
        name: str,
        default: Optional[Any] = ...,
    ) -> Any:
        """Returns value of given name from dictionary.

        Args:
            name: The key of value.
            default: Value returned if key doesn't exist.

        Returns:
            Value matched with given name.

        Raises:
            ValueError if name doesn't exist and default value not specified.

        """
        dictionary, key = get_nested_dictionary_and_key(
            dictionary=self._dict,
            name=name,
            required=default is ...,
        )
        return dictionary.get(key, default)

    def set(
        self,
        name: str,
        value: Any,
    ) -> Any:
        """Sets new value of given name in dictionary.

        Args:
            name: The key of value.
            value: Value to be set.

        Returns:
            The given value.

        """
        dictionary, key = get_nested_dictionary_and_key(
            dictionary=self._dict,
            name=name,
            set_mode=True,
        )
        dictionary[key] = value
        return value

    def pop(
        self,
        name: str,
        default: Optional[Any] = ...,
    ) -> Any:
        """Removes and returns value of given name from dictionary.

        Args:
            name: The key of value.
            default: Value returned if key doesn't exist.

        Returns:
            Removed value.

        Raises:
            ValueError if name doesn't exist and default value not specified.

        """
        dictionary, key = get_nested_dictionary_and_key(
            dictionary=self._dict,
            name=name,
            required=default is ...,
        )
        return dictionary.pop(key, default)

    def map(
        self,
        name: str,
        function: Callable,
    ) -> Any:
        """Applies value of given name to given function.

        Args:
            name: Name of value to be mapped.
            function: A function to which map passes a value.

        Returns:
            Mapped value.

        Raises:
            ValueError if name doesn't exist.

        """
        dictionary, key = get_nested_dictionary_and_key(
            dictionary=self._dict,
            name=name,
            required=True,
        )

        dictionary[key] = value = function(dictionary[key])
        return value

    def update_from(
        self,
        source: Union['Smart', Mapping[str, Any], Sequence[str], Path],
        name: Optional[str] = None,
        override: bool = True,
        required: bool = True,
    ) -> 'Smart':
        """Inserts items from given source.

        Args:
            source: Smart object, dictionary, list or path of items to insert.
            name: Key of source dictionary to insert.
            override: Whether to override existing items.
            required: Whether the name is required to exist.

        Returns:
            Smart instance.

        Raises:
            TypeError if given source is not supported.

        """
        smart: Smart
        if isinstance(source, Smart):
            smart = source
        elif isinstance(source, Mapping):
            smart = Smart(**source)
        elif isinstance(source, Sequence):
            smart = Smart(**dict(map(parse_param, source)))
        elif isinstance(source, Path):
            smart = Smart(**load_data(source))
        else:
            raise TypeError(f"Source type '{type(source)}' is not supported.")

        if name is None:
            for key in smart.keys(flatten=True):
                if override or not self.isin(key):
                    self.set(key, smart.get(key))
        else:
            try:
                self.update_from(
                    source=smart.get(name, default=... if required else dict()),
                    override=override,
                )
            except Exception as e:
                raise RuntimeError(f"Cannot update with source name '{name}'. " + ' '.join(e.args))

        return self

    @classmethod
    def load_from(
        cls,
        source: Union['Smart', Mapping[str, Any], Sequence[str], Path],
        name: Optional[str] = None,
    ) -> Any:
        """Loads object from the given source.

        Args:
            source: Smart object, dictionary, list or path of object to load.
            name: Key of source dictionary.

        Returns:
            Instance of loaded source.

        Raises:
            TypeError if given source is not supported.

        """
        return cls().update_from(source=source, name=name).init()

    def init(
        self,
        name: Optional[str] = None,
        persist: bool = True,
    ) -> Any:
        """Instantiates dictionary with given name.

        Args:
            name: Key of dictionary to be instantiated.
            persist: Whether to keep instantiated object in dictionary.

        Returns:
            Object of instantiated class.

        """
        obj = self._init_object(
            obj=self.dict if name is None else self.get(name),
            location=self._location,
        )

        if persist and name is not None:
            return self.set(name, obj)

        return obj

    def representation(
        self,
        skip_defaults: bool = False,
        merge_params: bool = False,
    ) -> Dict[str, Any]:
        """Creates representation of Smart object.

        Args:
            skip_defaults: Whether to skip arguments with default values.
            merge_params: Whether to join items from dictionary.

        Returns:
            Dictionary with Smart representation.

        """
        smart: Smart = Smart()

        if merge_params:
            smart.update_from(self)

        smart.update_from(
            source=self._object_representation(
                obj=self._type,
                skip_default=skip_defaults,
            ),
            override=False,
        )

        return convert_to_primitive_types(
            obj=smart.dict,
            missing_value=self.missing_value,
        )

    def register(
        self,
        classes: Union[
            Sequence[Union[str, Type[Any]]],
            Mapping[str, str],
            Mapping[Type[Any], str],
            Mapping[Union[str, Type[Any]], str],
        ],
        prefix: str = '',
    ) -> 'Smart':
        """Registers classes to be imported.

        Args:
            classes: Class list or dict with aliases to be registered.
            prefix: Prefix string added to alias.

        Returns:
            Smart object.

        """
        if self._location:
            raise AttributeError(
                f"Classes can only be registered in root Smart object, not in {self._location}."
            )

        if isinstance(classes, Sequence):
            self._register_classes(
                classes=classes,
                prefix=prefix,
            )
        elif isinstance(classes, Mapping):
            self._register_aliases(
                aliases=classes,
                prefix=prefix,
            )
        else:
            raise TypeError(f"Register classes type '{type(classes)}' is not supported.")

        return self

    def run(
        self,
        function: Callable[['Smart'], Any],
        path: Path = Path('params.yaml'),
    ) -> 'Smart':
        """Runs main function.

        Args:
            function: Main function to be run.
            path: Path of params file.

        Returns:
            Smart object.

        """
        args = parse_arguments(default_path=path)

        if args.strict:
            Smart.strict = True

        if args.path.is_file():
            self.update_from(args.path)

        self.update_from(args.params)

        if args.dump:
            save_data(
                data=self.representation(
                    skip_defaults=args.skip_defaults,
                    merge_params=args.merge_params,
                ),
                path=args.path,
            )
        elif args.print:
            if args.print == Print.PARAMS:
                print_data(
                    data=self.representation(
                        skip_defaults=args.skip_defaults,
                        merge_params=args.merge_params,
                    ),
                    fmt=args.format,
                )
            elif args.print == Print.KEYS:
                print_data(
                    data=tuple(self.keys(flatten=True)),
                    fmt=args.format,
                )
            else:
                raise NotImplementedError(f"Print '{args.print}' has not been implemented yet.")
        else:
            function(self)

        return self

    def _init_object(self, obj: Any, location: str) -> Any:
        if isinstance(obj, dict):
            if self.keyword in obj:
                return self._init_class_from_dict(
                    dictionary=obj,
                    location=location,
                )

            return self._init_dict(
                dictionary=obj,
                location=location,
            )

        if isinstance(obj, list):
            return self._init_list(
                lst=obj,
                location=location,
            )

        return obj

    def _init_dict(self, dictionary: Dict[str, Any], location: str) -> Dict[str, Any]:
        return {
            key: self._init_object(
                obj=value,
                location=join_keys(location, key),
            )
            for key, value in dictionary.items()
        }

    def _init_list(self, lst: List[Any], location: str) -> List[Any]:
        return [
            self._init_object(
                obj=element,
                location=join_keys(location, str(index)),
            )
            for index, element in enumerate(lst)
        ]

    def _init_class_from_dict(
        self,
        dictionary: Dict[str, Any],
        location: str,
    ) -> Any:
        kwargs, class_name, option = parse_class(
            dictionary=dictionary,
            keyword=self.keyword,
        )

        if class_name == self.__class__.__name__:
            return self._init_class(
                location=location,
                cls=Smart,
                kwargs=kwargs,
            )

        if class_name in self._origins:
            class_name = self._origins[class_name]
        elif self.allow_only_registered_classes:
            raise ImportError(f"Class '{class_name}' is not registered.")

        cls = cast(Type[_T], import_class(class_name))

        if option:
            if option == self.__class__.__name__:
                return self._init_class(
                    location=location,
                    cls=Smart,
                    args=(cls,),
                    kwargs=kwargs,
                )

            raise ValueError(f"Option '{option}' is not supported.")

        return self._init_class(
            location=location,
            cls=cls,
            kwargs=kwargs,
        )

    def _init_class(
        self,
        location: str,
        cls: Type[Any],
        args: Optional[Tuple[Any, ...]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
    ) -> Any:
        class_location = join_classes(location, get_class_name(cls))
        args = args or tuple()
        kwargs = kwargs or dict()

        if self.check_missings:
            check_missings(
                location=class_location,
                kwargs=kwargs,
                missing_value=self.missing_value,
                raise_error=self.strict,
            )

        if self.check_typings:
            check_typings(
                cls=cls,
                args=args,
                kwargs=kwargs,
                location=class_location,
                raise_error=self.strict,
            )

        try:
            obj = cls(*args, **kwargs)
        except Exception as e:
            raise RuntimeError(f"Error during instantiate {class_location} class.") from e
        else:
            if isinstance(obj, Smart):
                obj._location = location

            return obj

    def _object_representation(
        self,
        obj: Any,
        skip_default: bool,
    ) -> Dict[str, Any]:
        representation: Dict[str, Any] = dict()
        signature = inspect.signature(obj)

        for name, param in signature.parameters.items():
            if name != 'self' and param.kind in (
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.KEYWORD_ONLY,
            ):
                annotation = param.annotation
                default = param.default

                if annotation is Smart or isinstance(default, Smart) and default.type is dict:
                    representation[name] = {
                        self.keyword: self.__class__.__name__,
                    }
                elif get_origin(annotation) is Smart or isinstance(default, Smart):
                    if isinstance(default, Smart):
                        param_type = default.type
                    else:
                        param_type, *_ = get_args(annotation)

                    keyword = inspect.formatannotation(param_type)
                    keyword = self._aliases.get(keyword, keyword)
                    keyword = join_classes(keyword, get_class_name(self))

                    representation[name] = {
                        self.keyword: keyword,
                        **self._object_representation(
                            obj=param_type,
                            skip_default=skip_default,
                        ),
                    }
                elif default is not inspect.Parameter.empty and skip_default:
                    continue
                elif default is None or isinstance(default, (bool, float, int, str)):
                    representation[name] = default
                elif annotation is not inspect.Parameter.empty and isinstance(annotation, type):
                    if annotation in (bool, float, int, str):
                        representation[name] = annotation.__name__ + self.missing_value
                    else:
                        keyword = inspect.formatannotation(annotation)
                        keyword = self._aliases.get(keyword, keyword)
                        representation[name] = {
                            self.keyword: keyword,
                            **self._object_representation(
                                obj=annotation,
                                skip_default=skip_default,
                            ),
                        }
                else:
                    representation[name] = self.missing_value

        return representation

    def _register_classes(
        self,
        classes: Sequence[Union[str, Type[Any]]],
        prefix: str = '',
    ) -> None:
        self._register_aliases(
            aliases={cls: cls if isinstance(cls, str) else get_class_name(cls) for cls in classes},
            prefix=prefix,
        )

    def _register_aliases(
        self,
        aliases: Union[
            Mapping[str, str],
            Mapping[Type[Any], str],
            Mapping[Union[str, Type[Any]], str],
        ],
        prefix: str = '',
    ) -> None:
        for origin, alias in aliases.items():
            origin = origin if isinstance(origin, str) else inspect.formatannotation(origin)
            alias = join_keys(prefix, alias)

            remove_duplicated_key_and_value(
                key=origin,
                key_dict=self._aliases,
                value_dict=self._origins,
                message=f"Origin '{origin}' has been overridden.",
                raise_error=self.strict,
            )

            remove_duplicated_key_and_value(
                key=alias,
                key_dict=self._origins,
                value_dict=self._aliases,
                message=f"Alias '{alias}' has been overridden.",
                raise_error=self.strict,
            )

            self._aliases[origin] = alias
            self._origins[alias] = origin
