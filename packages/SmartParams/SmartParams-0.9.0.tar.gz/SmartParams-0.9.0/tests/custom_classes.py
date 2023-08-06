from typing import Any

from smartparams.smart import Smart


class Class:
    def __init__(self, arg1: str, arg2: int = 5) -> None:
        self.arg1 = arg1
        self.arg2 = arg2


class ClassChild(Class):
    pass


class ClassComposition:
    def __init__(  # type: ignore
        self,
        vanilla_cls: Class,
        smart_cls: Smart[Class],
        smart: Smart,
        unknown: Any,
        smart_cls_with_default: Smart[Class] = Smart(ClassChild, arg1="argument1"),
        smart_cls_with_only_default_generic=Smart(),
    ) -> None:
        self.vanilla_cls = vanilla_cls
        self.smart_cls = smart_cls
        self.smart = smart
        self.unknown = unknown
        self.smart_cls_with_default = smart_cls_with_default
        self.smart_cls_with_only_default_generic = smart_cls_with_only_default_generic


class ClassCompositionChild(ClassComposition):
    def __init__(  # type: ignore
        self,
        vanilla_cls: Class,
        smart_cls: Smart[Class],
        smart: Smart,
        unknown: Any,
        no_type,
        *args: Any,
        smart_cls_with_default: Smart[Class] = Smart(ClassChild, arg1="argument1"),
        smart_cls_with_only_default_generic=Smart(),
        with_only_default_primitive=11,
        **kwargs: Any,
    ) -> None:
        super(ClassCompositionChild, self).__init__(
            vanilla_cls=vanilla_cls,
            smart_cls=smart_cls,
            smart=smart,
            unknown=unknown,
            smart_cls_with_default=smart_cls_with_default,
            smart_cls_with_only_default_generic=smart_cls_with_only_default_generic,
        )
        self.no_type = no_type
        self.args = args
        self.with_only_default_primitive = with_only_default_primitive
        self.kwargs = kwargs


class RaiseClass:
    def __init__(self) -> None:
        raise RuntimeError


def some_function() -> None:
    pass
