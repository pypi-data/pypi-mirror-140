import inspect
import json
import warnings
from pydoc import locate
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple, Type, get_origin

from typeguard import check_type

_KEY_SEPARATOR = '.'
_CLASS_SEPARATOR = ':'
_PARAM_SEPARATOR = '='


def get_nested_dictionary_and_key(
    dictionary: Dict[str, Any],
    name: str,
    set_mode: bool = False,
    required: bool = False,
) -> Tuple[Dict[str, Any], str]:
    *nested_keys, last_key = name.split(_KEY_SEPARATOR)

    key_list = list()
    for key in nested_keys:
        key_list.append(key)
        if key not in dictionary:
            if set_mode:
                dictionary[key] = dict()
            else:
                raise KeyError(f"Param '{_KEY_SEPARATOR.join(key_list)}' is not in dictionary.")

        if not isinstance(dictionary[key], dict):
            if set_mode:
                dictionary[key] = dict()
            else:
                raise ValueError(f"Param '{_KEY_SEPARATOR.join(key_list)}' is not dictionary.")

        dictionary = dictionary[key]

    if required and last_key not in dictionary:
        raise KeyError(f"Param '{last_key}' is not in dictionary.")

    return dictionary, last_key


def flatten_keys(
    obj: Any,
    prefix: str = "",
) -> List[str]:
    if not isinstance(obj, dict):
        return [prefix]

    keys = []
    for k, v in obj.items():
        keys.extend(flatten_keys(v, join_keys(prefix, k)))

    return keys


def check_key_is_in(
    key: str,
    dictionary: Dict[str, Any],
) -> bool:
    key, _, sub_key = key.partition(_KEY_SEPARATOR)
    if key not in dictionary:
        return False

    if not sub_key:
        return True

    dictionary = dictionary[key]

    if not isinstance(dictionary, dict):
        return True

    return check_key_is_in(
        key=sub_key,
        dictionary=dictionary,
    )


def remove_duplicated_key_and_value(
    key: str,
    key_dict: Dict[str, str],
    value_dict: Dict[str, str],
    message: str,
    raise_error: bool,
) -> None:
    if key in key_dict:
        if raise_error:
            raise ValueError(message)
        warnings.warn(message)

        value_dict.pop(key_dict.pop(key))


def join_keys(*args: str) -> str:
    return _KEY_SEPARATOR.join(a for a in args if a)


def join_classes(*args: str) -> str:
    return _CLASS_SEPARATOR.join(a for a in args if a)


def parse_class(
    dictionary: Dict[str, Any],
    keyword: str,
) -> Tuple[Dict[str, Any], str, Optional[str]]:
    kwargs = dictionary.copy()
    class_name = kwargs.pop(keyword)
    class_name, _, option = class_name.partition(_CLASS_SEPARATOR)
    return kwargs, class_name, option


def parse_param(param: str) -> Tuple[str, Any]:
    key, separator, raw_value = param.partition(_PARAM_SEPARATOR)

    if not separator:
        raise ValueError(f"Param '{param}' has not assigned value.")

    try:
        value = json.loads(raw_value)
    except json.decoder.JSONDecodeError:
        value = raw_value

    return key, value


def str_to_bool(value: str) -> bool:
    value = value.lower()
    if value in ('1', 'y', 'yes', 't', 'true'):
        return True

    if value in ('0', 'n', 'no', 'f', 'false'):
        return False

    raise ValueError(f"String value '{value}' is not like to boolean.")


def import_class(name: str) -> type:
    cls = locate(name)
    if cls is None:
        raise ValueError(f"Class '{name}' does not exist.")
    if not isinstance(cls, type):
        raise ValueError(f"Object '{name}' is not a class.")
    return cls


def get_class_name(obj: Any) -> str:
    try:
        return obj.__qualname__
    except AttributeError:
        return obj.__class__.__qualname__


def get_type_hints(signature: inspect.Signature) -> Dict[str, Any]:
    type_hints: Dict[str, Any] = {}
    for name, param in signature.parameters.items():
        if param.annotation is not inspect.Parameter.empty:
            param_type = param.annotation
        elif param.default is not inspect.Parameter.empty and param.default is not None:
            param_type = get_origin(param.default) or type(param.default)
        else:
            param_type = Any

        if param.kind == inspect.Parameter.VAR_POSITIONAL:
            type_hints[name] = Tuple[param_type, ...]  # type: ignore
        elif param.kind == inspect.Parameter.VAR_KEYWORD:
            type_hints[name] = Dict[str, param_type]  # type: ignore
        else:
            type_hints[name] = param_type

    return type_hints


def check_overrides(
    location: str,
    params: Dict[str, Any],
    kwargs: Dict[str, Any],
    raise_error: bool,
) -> None:
    if overrides := set(params).intersection(kwargs):
        msg = f"Override {location}'s class arguments {overrides}."
        if raise_error:
            raise ValueError(msg)
        warnings.warn(msg)


def check_missings(
    location: str,
    kwargs: Dict[str, Any],
    missing_value: str,
    raise_error: bool,
) -> None:
    for name, value in kwargs.items():
        if isinstance(value, str) and value.endswith(missing_value):
            msg = f"Missing {location}'s class argument '{name}' value."
            if raise_error:
                raise ValueError(msg)
            warnings.warn(msg)


def check_typings(
    location: str,
    cls: Type[Any],
    args: Tuple[Any, ...],
    kwargs: Dict[str, Any],
    raise_error: bool,
) -> None:
    if cls is dict:
        return None

    signature = inspect.signature(cls)
    try:
        arguments = signature.bind(*args, **kwargs).arguments
    except TypeError as e:
        raise TypeError(f"The {location}'s class {''.join(e.args)}.")

    for name, expected_type in get_type_hints(signature).items():
        if name in arguments:
            try:
                check_type(
                    argname=f"{location}'s class argument '{name}'",
                    value=arguments[name],
                    expected_type=expected_type,
                )
            except TypeError as e:
                msg = f"The {''.join(e.args)}."
                if raise_error:
                    raise TypeError(msg)
                warnings.warn(msg)


def convert_to_primitive_types(
    obj: Any,
    missing_value: str,
) -> Any:
    if obj is None or isinstance(obj, (bool, int, float, str)):
        return obj

    if isinstance(obj, Mapping):
        return {
            convert_to_primitive_types(k, missing_value): convert_to_primitive_types(
                v, missing_value
            )
            for k, v in obj.items()
        }

    if isinstance(obj, Sequence):
        return [convert_to_primitive_types(item, missing_value) for item in obj]

    return missing_value
