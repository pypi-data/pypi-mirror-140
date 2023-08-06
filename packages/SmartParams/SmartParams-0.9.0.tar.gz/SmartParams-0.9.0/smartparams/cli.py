import argparse
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional, Tuple, cast

_FORMATS = ('yaml', 'json', 'dict')
_DEFAULT_FORMAT = 'yaml'


class Print(str, Enum):
    PARAMS = 'params'
    KEYS = 'keys'

    @classmethod
    def values(cls) -> Tuple[str, ...]:
        return tuple(cast(Enum, item).value for item in cls)


@dataclass
class Arguments:
    path: Path
    dump: bool
    skip_defaults: bool
    merge_params: bool
    print: Optional[str]
    format: str
    params: List[str]
    strict: bool


def parse_arguments(default_path: Optional[Path] = None) -> Arguments:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--path',
        default=default_path,
        type=Path,
        required=not bool(default_path),
        help="Path to params file.",
    )
    parser.add_argument('--dump', action='store_true', help="Create params file template.")
    parser.add_argument('--print', choices=Print.values(), help="Print params or keys.")
    parser.add_argument('--format', choices=_FORMATS, help="Print format.")
    parser.add_argument('--skip-defaults', '-s', action='store_true', help="Skip default params.")
    parser.add_argument('--merge-params', '-m', action='store_true', help="Merge existing params.")
    parser.add_argument('--strict', action='store_true', help="Raise errors instead of warnings.")
    args, params = parser.parse_known_args(sys.argv[1:])

    if args.dump and args.print:
        parser.error("Cannot use --dump and --print simultaneously.")

    if not args.dump and args.print != Print.PARAMS:
        if args.skip_defaults:
            parser.error(f"Cannot use --skip-defaults without --dump or --print {Print.PARAMS}.")
        if args.merge_params:
            parser.error(f"Cannot use --merge-params without --dump or --print {Print.PARAMS}.")

    if args.dump and args.format:
        parser.error("Cannot use --format with --dump.")

    return Arguments(
        path=args.path,
        print=args.print,
        dump=args.dump,
        skip_defaults=args.skip_defaults,
        merge_params=args.merge_params,
        format=args.format or _DEFAULT_FORMAT,
        params=params,
        strict=args.strict,
    )
