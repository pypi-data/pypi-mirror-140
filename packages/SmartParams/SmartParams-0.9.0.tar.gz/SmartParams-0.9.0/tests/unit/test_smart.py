from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union
from unittest.mock import Mock, patch

from smartparams.smart import Smart
from tests.custom_classes import Class, ClassChild
from tests.unit import UnitCase


class TestSmartInitCase(UnitCase):
    def setUp(self) -> None:
        self.smart = Smart(Class, arg1='arg1', arg2=10)

    def test_dict(self) -> None:
        params = self.smart.dict

        self.assertEqual(dict(arg1='arg1', arg2=10), params)
        self.assertIsNot(self.smart._dict, params)

    def test_call(self) -> None:
        obj = self.smart()

        self.assertIsInstance(obj, Class)
        self.assertEqual('arg1', obj.arg1)
        self.assertEqual(10, obj.arg2)

    def test_call__with_dict(self) -> None:
        smart = Smart(Class)

        obj = smart('a1', arg2=15)

        self.assertIsInstance(obj, Class)
        self.assertEqual('a1', obj.arg1)
        self.assertEqual(15, obj.arg2)

    def test_call__with_duplicated_dict(self) -> None:
        smart = Smart(Class, arg1='arg1')

        self.assertRaises(TypeError, smart, 'a1')

    def test_call__without_class(self) -> None:
        smart: Smart = Smart()

        obj = smart()

        self.assertIsInstance(obj, dict)


class TestSmartAccessCase(UnitCase):
    def setUp(self) -> None:
        self.smart: Smart = Smart(arg1='arg1', arg2=['arg2'], arg3={'arg31': 'a31', 'arg32': 'a32'})

    def test_keys(self) -> None:
        keys = self.smart.keys()

        self.assertTupleEqual(('arg1', 'arg2', 'arg3'), tuple(keys))

    def test_keys__flatten(self) -> None:
        value = self.smart.keys(flatten=True)

        self.assertTupleEqual(('arg1', 'arg2', 'arg3.arg31', 'arg3.arg32'), tuple(value))

    def test_keys__flatten_pattern(self) -> None:
        value = self.smart.keys(flatten=True, pattern='arg[1,3].*')

        self.assertTupleEqual(('arg1', 'arg3.arg31', 'arg3.arg32'), tuple(value))

    def test_values(self) -> None:
        expected = ('arg1', ['arg2'], {'arg31': 'a31', 'arg32': 'a32'})

        actual = self.smart.values()

        self.assertTupleEqual(expected, tuple(actual))

    def test_items(self) -> None:
        expected = (
            ('arg1', 'arg1'),
            ('arg2', ['arg2']),
            ('arg3', {'arg31': 'a31', 'arg32': 'a32'}),
        )

        actual = self.smart.items()

        self.assertTupleEqual(expected, tuple(actual))

    def test_get(self) -> None:
        value = self.smart.get('arg3.arg31')

        self.assertEqual('a31', value)

    def test_set(self) -> None:
        new_value = 'argument31'

        value = self.smart.set('arg3.arg31', new_value)

        self.assertEqual('argument31', value)
        self.assertEqual('argument31', self.smart.dict['arg3']['arg31'])
        self.assertEqual('a32', self.smart.dict['arg3']['arg32'])

    def test_pop(self) -> None:
        value = self.smart.pop('arg3.arg31')

        self.assertEqual('a31', value)
        self.assertFalse('arg3' in self.smart.dict['arg3'])

    def test_map(self) -> None:
        function = Mock(return_value='argument31')

        value = self.smart.map('arg3.arg31', function)

        self.assertEqual('argument31', value)
        self.assertEqual('argument31', self.smart.dict['arg3']['arg31'])
        self.assertEqual('a32', self.smart.dict['arg3']['arg32'])

    @patch('smartparams.smart.load_data')
    def test_update(self, load_data: Mock) -> None:
        dictionary = {'arg1': {'nested1': 'argument1'}, 'arg3': {'arg31': 'argument31'}}
        load_data.return_value = dictionary
        test_cases: List[Tuple[Union['Smart', Dict[str, Any], List[str], Path], str]] = [
            (Smart(**dictionary), "smart"),
            (dictionary, "dict"),
            (['arg3.arg31=argument31', 'arg1={"nested1": "argument1"}'], "list"),
            (Path('path/to/file.yaml'), "path"),
        ]

        for source, msg in test_cases:
            smart: Smart = deepcopy(self.smart)

            with self.subTest(msg=msg):
                smart.update_from(source)

                self.assertTrue('arg1' in smart.dict)
                self.assertTrue('arg2' in smart.dict)
                self.assertTrue('arg3' in smart.dict)
                self.assertEqual({'nested1': 'argument1'}, smart.dict['arg1'])
                self.assertListEqual(['arg2'], smart.dict['arg2'])
                self.assertEqual('argument31', smart.dict['arg3']['arg31'])
                self.assertEqual('a32', smart.dict['arg3']['arg32'])

    @patch('smartparams.smart.load_data')
    def test_update__not_override(self, load_data: Mock) -> None:
        dictionary = {'arg1': {'nested1': 'aa1'}, 'arg3': {'arg31': 'aa31'}, 'arg4': {'a4': 'aa4'}}
        load_data.return_value = dictionary
        test_cases: List[Tuple[Union['Smart', Dict[str, Any], List[str], Path], str]] = [
            (Smart(**dictionary), "smart"),
            (dictionary, "dict"),
            (['arg3.arg31=argument31', 'arg1={"nested1": "aa1"}', 'arg4={"a4": "aa4"}'], "list"),
            (Path('path/to/file.yaml'), "path"),
        ]

        for source, msg in test_cases:
            smart: Smart = deepcopy(self.smart)

            with self.subTest(msg=msg):
                smart.update_from(source, override=False)

                self.assertTrue('arg1' in smart.dict)
                self.assertTrue('arg2' in smart.dict)
                self.assertTrue('arg3' in smart.dict)
                self.assertEqual('arg1', smart.dict['arg1'])
                self.assertListEqual(['arg2'], smart.dict['arg2'])
                self.assertEqual('a31', smart.dict['arg3']['arg31'])
                self.assertEqual('a32', smart.dict['arg3']['arg32'])
                self.assertEqual({'a4': 'aa4'}, smart.dict['arg4'])

    def test_update__not_required(self) -> None:
        dictionary = {'arg1': {'nested1': 'aa1'}}
        expected = deepcopy(self.smart.dict)

        self.smart.update_from(dictionary, name='arg2', required=False)

        self.assertEqual(expected, self.smart.dict)

    def test_update__with_name(self) -> None:
        dictionary = {'arg': {'nested': ['arg3.arg31=argument31', 'arg1={"nested1": "argument1"}']}}

        self.smart.update_from(dictionary, name='arg.nested')

        self.assertTrue('arg1' in self.smart.dict)
        self.assertTrue('arg2' in self.smart.dict)
        self.assertTrue('arg3' in self.smart.dict)
        self.assertEqual({'nested1': 'argument1'}, self.smart.dict['arg1'])
        self.assertListEqual(['arg2'], self.smart.dict['arg2'])
        self.assertEqual('argument31', self.smart.dict['arg3']['arg31'])
        self.assertEqual('a32', self.smart.dict['arg3']['arg32'])

    def test_update__with_name_error(self) -> None:
        dictionary = {'arg': {'nested': ['arg3.arg31 argument31']}}

        self.assertRaises(RuntimeError, self.smart.update_from, dictionary, name='arg.nested')

    def test_update__unknown(self) -> None:
        source = set()  # type: ignore

        self.assertRaises(TypeError, self.smart.update_from, source)


class TestSmartInstantiateCase(UnitCase):
    def setUp(self) -> None:
        self.class_name = f"{Class.__module__}.{Class.__qualname__}"
        self.params = dict(
            smart_dict={'class': 'Smart'},
            smart={'class': self.class_name + ':Smart', 'arg1': 'arg1', 'arg2': 10},
            object={'class': self.class_name, 'arg1': 'arg1', 'arg2': 10},
            value=21,
        )
        self.smart: Smart = Smart(**self.params)

    def test_init__persist(self) -> None:
        obj = self.smart.init('object')

        self.assertIs(self.smart.get('object'), obj)
        self.assertIsInstance(self.smart.get('object'), Class)
        self.assertTrue('object' in self.smart.dict)

    def test_init__not_persist(self) -> None:
        obj = self.smart.init('object', persist=False)

        self.assertIsNot(self.smart.get('object'), obj)
        self.assertIsInstance(self.smart.get('object'), dict)
        self.assertTrue('object' in self.smart.dict)

    def test_init__any(self) -> None:
        data = "string"

        result = self.smart._init_object(data, '')

        self.assertEqual(data, result)

    def test_init__smart_dict(self) -> None:
        obj = self.params['smart_dict']

        result = self.smart._init_object(obj, '')

        self.assertIsInstance(result, Smart)
        self.assertIs(result.type, dict)

    def test_init__smart(self) -> None:
        obj = self.params['smart']

        result = self.smart._init_object(obj, '')

        self.assertIsInstance(result, Smart)
        self.assertIs(result.type, Class)

    def test_init__unknown(self) -> None:
        obj = self.params['smart']
        obj['class'] += "suffix"  # type: ignore

        self.assertRaises(ValueError, self.smart._init_object, obj, '')

    def test_init__object(self) -> None:
        obj = self.params['object']

        result = self.smart._init_object(obj, '')

        self.assertIsInstance(result, Class)

    def test_init__dict(self) -> None:
        obj = {'key': 'value'}

        result = self.smart._init_object(obj, '')

        self.assertIsNot(obj, result)

    def test_init__list(self) -> None:
        obj = ['item']

        result = self.smart._init_object(obj, '')

        self.assertIsNot(obj, result)

    def test_init__with_aliases(self) -> None:
        self.smart.allow_only_registered_classes = True
        self.smart._aliases = {self.class_name: 'Class'}
        self.smart._origins = {v: k for k, v in self.smart._aliases.items()}
        obj = self.params['object']
        obj['class'] = 'Class'  # type: ignore

        result = self.smart._init_object(obj, '')

        self.assertIsInstance(result, Class)

    def test_init__with_aliases_not_used(self) -> None:
        self.smart._aliases = {self.class_name: 'Class'}
        self.smart._origins = {v: k for k, v in self.smart._aliases.items()}
        obj = self.params['object']

        result = self.smart._init_object(obj, '')

        self.assertIsInstance(result, Class)

    def test_init__with_aliases_error(self) -> None:
        self.smart.allow_only_registered_classes = True
        self.smart._aliases = {self.class_name: 'Class'}
        self.smart._origins = {v: k for k, v in self.smart._aliases.items()}
        obj = self.params['object']

        self.assertRaises(ImportError, self.smart._init_object, obj, '')


class TestRegisterCase(UnitCase):
    def setUp(self) -> None:
        self.smart: Smart = Smart()
        self.smart.strict = True

    def tearDown(self) -> None:
        Smart._aliases = dict()
        Smart._origins = dict()

    def test_register__classes(self) -> None:
        classes = ('origin.1', 'origin.2')

        self.smart.register(classes)

        self.assertFalse(self.smart.allow_only_registered_classes)
        self.assertEqual({'origin.1': 'origin.1', 'origin.2': 'origin.2'}, self.smart._aliases)
        self.assertEqual({'origin.1': 'origin.1', 'origin.2': 'origin.2'}, self.smart._origins)

    def test_register__with_prefix_with_class(self) -> None:
        aliases = [Class, ClassChild]
        expected_aliases = {
            'tests.custom_classes.Class': 'some.classes.Class',
            'tests.custom_classes.ClassChild': 'some.classes.ClassChild',
        }
        expected_origins = {
            'some.classes.Class': 'tests.custom_classes.Class',
            'some.classes.ClassChild': 'tests.custom_classes.ClassChild',
        }

        self.smart.register(aliases, prefix='some.classes')

        self.assertFalse(self.smart.allow_only_registered_classes)
        self.assertEqual(expected_aliases, self.smart._aliases)
        self.assertEqual(expected_origins, self.smart._origins)

    def test_register__aliases(self) -> None:
        aliases = {'origin.1': 'alias.1', 'origin.2': 'alias.2'}

        self.smart.register(aliases)

        self.assertFalse(self.smart.allow_only_registered_classes)
        self.assertEqual({'origin.1': 'alias.1', 'origin.2': 'alias.2'}, self.smart._aliases)
        self.assertEqual({'alias.1': 'origin.1', 'alias.2': 'origin.2'}, self.smart._origins)

    def test_register__alias_duplicates(self) -> None:
        self.smart._aliases = {'origin': 'alias'}
        self.smart._origins = {'alias': 'origin'}
        aliases = {'origin.1': 'alias'}

        self.assertRaises(ValueError, self.smart.register, aliases)

    def test_register__origin_duplicates(self) -> None:
        self.smart._aliases = {'origin': 'alias'}
        self.smart._origins = {'alias': 'origin'}
        aliases = {'origin': 'alias.1'}

        self.assertRaises(ValueError, self.smart.register, aliases)

    @patch('smartparams.utils.warnings')
    def test_register__duplicates(self, warnings: Mock) -> None:
        self.smart.strict = False
        Smart._aliases = {'origin.1': 'alias.1', 'origin.2': 'alias.2'}
        Smart._origins = {'alias.1': 'origin.1', 'alias.2': 'origin.2'}
        aliases = {'origin.1': 'alias.2'}

        self.smart.register(aliases)

        self.assertEqual({'origin.1': 'alias.2'}, Smart._aliases)
        self.assertEqual({'alias.2': 'origin.1'}, Smart._origins)
        warnings.warn.assert_called()

    def test_register__raise(self) -> None:
        self.assertRaises(TypeError, self.smart.register, Mock())

    def test_register__nested(self) -> None:
        self.smart._location = 'nested'

        self.assertRaises(AttributeError, self.smart.register, Mock())
