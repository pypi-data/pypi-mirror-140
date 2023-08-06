import pickle as pkl
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from smartparams import Smart
from tests.custom_classes import (
    Class,
    ClassChild,
    ClassComposition,
    RaiseClass,
    some_function,
)
from tests.unit import UnitCase


class TestSerialization(UnitCase):
    def setUp(self) -> None:
        class_name = f"{Class.__module__}.{Class.__qualname__}"
        class_child_name = f"{ClassChild.__module__}.{ClassChild.__qualname__}"
        self.smart = Smart(
            ClassComposition,
            **{
                'vanilla_cls': {'arg1': 'argument1', 'arg2': 15, 'class': class_name},
                'smart': {'class': 'Smart'},
                'smart_cls': {'arg1': 'str???', 'arg2': 75, 'class': f'{class_name}:Smart'},
                'unknown': some_function,
                'smart_cls_with_default': {
                    'arg1': 'argument1',
                    'arg2': 5,
                    'class': f'{class_child_name}:Smart',
                },
            },
        )

    def test_pickle(self) -> None:
        pickled = pkl.dumps(self.smart)
        smart = pkl.loads(pickled)

        self.assertIsInstance(smart, Smart)
        self.assertEqual(str(self.smart), str(smart))
        self.assertIs(smart.type, ClassComposition)
        self.assertEqual(self.smart.dict, smart.dict)


class TestSmartRunCase(UnitCase):
    def setUp(self) -> None:
        self.smart = Smart(Class, arg2=10)

    def tearDown(self) -> None:
        Smart.strict = False

    @patch('smartparams.cli.sys', Mock(argv='script.py --dump --merge-params'.split()))
    def test_run__dump(self) -> None:
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.yaml') as file:
            self.smart.run(function=Mock(), path=Path(file.name))

            self.assertEqual("arg2: 10\narg1: str???\n", file.read())

    @patch('smartparams.cli.sys', Mock(argv='script.py --print params'.split()))
    @patch('smartparams.io.print')
    def test_run__print_params(self, print_mock: Mock) -> None:
        self.smart.run(function=Mock())

        print_mock.assert_called_with("arg1: str???\narg2: 5\n")

    @patch('smartparams.cli.sys', Mock(argv='script.py --print keys'.split()))
    @patch('smartparams.io.print')
    def test_run__print_keys(self, print_mock: Mock) -> None:
        self.smart.run(function=Mock())

        print_mock.assert_called_with("- arg2\n")

    @patch('smartparams.cli.sys', Mock(argv='script.py --strict arg1=10'.split()))
    def test_run__strict(self) -> None:
        self.assertRaises(TypeError, self.smart.run, function=lambda x: x())

    @patch('smartparams.smart.load_data', Mock(return_value={'arg1': 'string'}))
    def test_run__function(self) -> None:
        function = Mock()
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.yaml') as file:
            file.write("arg1: string\n")
            file.seek(0)

            self.smart.run(function=function, path=Path(file.name))

            function.assert_called_once_with(self.smart)


class TestSmartRepresentationCase(UnitCase):
    def setUp(self) -> None:
        self.smart: Smart = Smart()

    def test_object_representation__with_defaults(self) -> None:
        class_name = f"{Class.__module__}.{Class.__qualname__}"
        class_child_name = f"{ClassChild.__module__}.{ClassChild.__qualname__}"
        expected = {
            'vanilla_cls': {'class': class_name, 'arg1': 'str???', 'arg2': 5},
            'smart_cls': {'class': f'{class_name}:Smart', 'arg1': 'str???', 'arg2': 5},
            'smart': {'class': 'Smart'},
            'unknown': '???',
            'smart_cls_with_default': {
                'class': f'{class_child_name}:Smart',
                'arg1': 'str???',
                'arg2': 5,
            },
            'smart_cls_with_only_default_generic': {
                'class': 'Smart',
            },
        }

        actual = self.smart._object_representation(ClassComposition, skip_default=False)

        self.assertEqual(expected, actual)

    def test_object_representation__without_defaults(self) -> None:
        class_name = f"{Class.__module__}.{Class.__qualname__}"
        class_child_name = f"{ClassChild.__module__}.{ClassChild.__qualname__}"
        expected = {
            'vanilla_cls': {'class': class_name, 'arg1': 'str???'},
            'smart_cls': {'class': f'{class_name}:Smart', 'arg1': 'str???'},
            'smart': {'class': 'Smart'},
            'unknown': '???',
            'smart_cls_with_default': {
                'class': f'{class_child_name}:Smart',
                'arg1': 'str???',
            },
            'smart_cls_with_only_default_generic': {
                'class': 'Smart',
            },
        }

        actual = self.smart._object_representation(ClassComposition, skip_default=True)

        self.assertEqual(expected, actual)

    def test_object_representation__with_aliases(self) -> None:
        class_name = f"{Class.__module__}.{Class.__qualname__}"
        class_child_name = f"{ClassChild.__module__}.{ClassChild.__qualname__}"
        self.smart.allow_only_registered_classes = True
        self.smart._aliases = {class_name: 'Parent', class_child_name: 'Child'}
        self.smart._origins = {v: k for k, v in self.smart._aliases.items()}
        expected = {
            'vanilla_cls': {'class': 'Parent', 'arg1': 'str???', 'arg2': 5},
            'smart_cls': {'class': 'Parent:Smart', 'arg1': 'str???', 'arg2': 5},
            'smart': {'class': 'Smart'},
            'unknown': '???',
            'smart_cls_with_default': {
                'class': 'Child:Smart',
                'arg1': 'str???',
                'arg2': 5,
            },
            'smart_cls_with_only_default_generic': {
                'class': 'Smart',
            },
        }

        actual = self.smart._object_representation(ClassComposition, skip_default=False)

        self.assertEqual(expected, actual)


class TestCheckCase(UnitCase):
    def setUp(self) -> None:
        self.smart = Smart(Class, arg1='str???', arg2=15)
        self.smart.strict = True

    def test_init_class__check_false(self) -> None:
        self.smart.check_missings = False
        self.smart.check_overrides = False
        self.smart.check_typings = False

        obj = self.smart(arg2='88')

        self.assertIsInstance(obj, Class)
        self.assertEqual('88', obj.arg2)

    def test_init_class__check_missings_true(self) -> None:
        self.smart.check_missings = True
        self.smart.check_overrides = False
        self.smart.check_typings = False

        self.assertRaises(ValueError, self.smart, arg2='88')

    @patch('smartparams.utils.warnings')
    def test_init_class__check_missings_warning(self, warnings: Mock) -> None:
        self.smart.strict = False

        self.smart.check_missings = True
        self.smart.check_overrides = False
        self.smart.check_typings = False

        obj = self.smart(arg2='88')

        self.assertEqual('88', obj.arg2)
        warnings.warn.assert_called()

    def test_init_class__check_overrides_true(self) -> None:
        self.smart.check_missings = False
        self.smart.check_overrides = True
        self.smart.check_typings = False

        self.assertRaises(ValueError, self.smart, arg2='88')

    @patch('smartparams.utils.warnings')
    def test_init_class__check_overrides_warning(self, warnings: Mock) -> None:
        self.smart.strict = False

        self.smart.check_missings = False
        self.smart.check_overrides = True
        self.smart.check_typings = False

        obj = self.smart(arg2='88')

        self.assertEqual('88', obj.arg2)
        warnings.warn.assert_called()

    def test_init_class__check_typings_true(self) -> None:
        self.smart.check_missings = False
        self.smart.check_overrides = False
        self.smart.check_typings = True

        self.assertRaises(TypeError, self.smart, arg2='88')

    @patch('smartparams.utils.warnings')
    def test_init_class__check_typings_warning(self, warnings: Mock) -> None:
        self.smart.strict = False

        self.smart.check_missings = False
        self.smart.check_overrides = False
        self.smart.check_typings = True

        obj = self.smart(arg2='88')

        self.assertEqual('88', obj.arg2)
        warnings.warn.assert_called()

    def test_init_class__location(self) -> None:
        smart = Smart(Smart, nested=[{'class': 'Smart'}])
        smart._location = 'location'

        obj = smart()

        self.assertIsInstance(obj, Smart)
        self.assertEqual('location.nested.0', obj.get('nested')[0]._location)

    def test_init_class__raise(self) -> None:
        smart = Smart(RaiseClass)

        self.assertRaises(Exception, smart)
