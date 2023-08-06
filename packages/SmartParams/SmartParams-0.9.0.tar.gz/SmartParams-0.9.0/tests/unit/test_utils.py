import inspect
from typing import Any, Dict, Tuple
from unittest.mock import Mock

from smartparams import Smart
from smartparams.utils import (
    convert_to_primitive_types,
    get_class_name,
    get_nested_dictionary_and_key,
    get_type_hints,
    parse_param,
    str_to_bool,
)
from tests.custom_classes import Class, ClassCompositionChild
from tests.unit import UnitCase


class TestGetNestedDictionaryAndKey(UnitCase):
    def setUp(self) -> None:
        self.dict = dict(arg1='arg1', arg2=['arg2'], arg3={'arg31': 'a31', 'arg32': 'a32'})

    def test_get_nested_dictionary_and_key(self) -> None:
        name = 'arg3.arg31'

        dictionary, key = get_nested_dictionary_and_key(dictionary=self.dict, name=name)

        self.assertEqual('arg31', key)
        self.assertTupleEqual((('arg31', 'a31'), ('arg32', 'a32')), tuple(dictionary.items()))

    def test_get_nested_dictionary_and_key__not_in_dictionary(self) -> None:
        name = 'missing.any'

        self.assertRaises(KeyError, get_nested_dictionary_and_key, dictionary=self.dict, name=name)

    def test_get_nested_dictionary_and_key__required_true(self) -> None:
        name = 'arg3.missing'

        self.assertRaises(
            KeyError,
            get_nested_dictionary_and_key,
            dictionary=self.dict,
            name=name,
            required=True,
        )

    def test_get_nested_dictionary_and_key__is_not_dictionary(self) -> None:
        name = 'arg3.arg31.a31'

        self.assertRaises(
            ValueError, get_nested_dictionary_and_key, dictionary=self.dict, name=name
        )

    def test_get_nested_dictionary_and_key__set_mode(self) -> None:
        name = 'arg3.missing.key'

        dictionary, key = get_nested_dictionary_and_key(
            dictionary=self.dict,
            name=name,
            set_mode=True,
        )

        self.assertIsInstance(dictionary, dict)
        self.assertFalse(bool(dictionary))
        self.assertEqual('key', key)

    def test_get_nested_dictionary_and_key__set_mode_not_is_not_dictionary(self) -> None:
        name = 'arg3.arg31.a31'

        dictionary, key = get_nested_dictionary_and_key(
            dictionary=self.dict,
            name=name,
            set_mode=True,
        )

        self.assertIsInstance(dictionary, dict)
        self.assertFalse(bool(dictionary))
        self.assertEqual('a31', key)


class TestParseParam(UnitCase):
    def test_parse_param(self) -> None:
        data = 'key.neste_key=[true, null, "some string", {"1": 9.0}]'

        key, value = parse_param(data)

        self.assertEqual('key.neste_key', key)
        self.assertListEqual([True, None, "some string", {"1": 9.0}], value)

    def test_parse_param_not_valid(self) -> None:
        data = 'key.neste_key=[true, null, "some string, {"1": 9.0}]'

        key, value = parse_param(data)

        self.assertEqual('key.neste_key', key)
        self.assertEqual('[true, null, "some string, {"1": 9.0}]', value)

    def test_parse_param__raise_no_assignment(self) -> None:
        data = 'key.neste_key [true, null, "some string", {"1": 9.0}]'

        self.assertRaises(ValueError, parse_param, data)


class TestGetClassName(UnitCase):
    def test_get_class_name(self) -> None:
        test_cases = (
            (Mock, 'Mock'),
            (Mock(), 'Mock'),
            (123, 'int'),
            (type, 'type'),
            (None, 'NoneType'),
            (lambda: ..., 'TestGetClassName.test_get_class_name.<locals>.<lambda>'),
            ((i for i in range(1)), 'TestGetClassName.test_get_class_name.<locals>.<genexpr>'),
        )

        for cls, expected in test_cases:
            with self.subTest(expected=expected):
                actual = get_class_name(cls)  # type: ignore

                self.assertEqual(expected, actual)


class TestStrToBool(UnitCase):
    def test_str_to_bool__true(self) -> None:
        test_cases = (
            'Y',
            'True',
        )

        for value in test_cases:
            with self.subTest(value=value):
                actual = str_to_bool(value)

                self.assertTrue(actual)

    def test_str_to_bool__false(self) -> None:
        test_cases = (
            'N',
            'False',
        )

        for value in test_cases:
            with self.subTest(value=value):
                actual = str_to_bool(value)

                self.assertFalse(actual)

    def test_str_to_bool__raise(self) -> None:
        test_cases = (
            '2',
            'D',
        )

        for value in test_cases:
            with self.subTest(value=value):
                self.assertRaises(ValueError, str_to_bool, value)


class TestGetTypeHints(UnitCase):
    def test_get_type_hints(self) -> None:
        test_cases = (
            (
                ClassCompositionChild,
                {
                    'vanilla_cls': Class,
                    'smart_cls': Smart[Class],
                    'smart': Smart,
                    'unknown': Any,
                    'no_type': Any,
                    'args': Tuple[Any, ...],
                    'smart_cls_with_default': Smart[Class],
                    'smart_cls_with_only_default_generic': Smart,
                    'with_only_default_primitive': int,
                    'kwargs': Dict[str, Any],
                },
            ),
        )

        for cls, expected in test_cases:
            signature = inspect.signature(cls)

            with self.subTest(cls=cls.__name__):
                actual = get_type_hints(signature)

                self.assertEqual(expected, actual)


class TestConvertToPrimitiveTypes(UnitCase):
    def test_convert_to_primitive_types(self) -> None:
        data = (True, None, {'known': 9.0, 'unknown': set()})
        expected = [True, None, {'known': 9.0, 'unknown': '???'}]

        actual = convert_to_primitive_types(data, missing_value='???')

        self.assertEqual(expected, actual)
