"""
HWP Parser CLI

사용법:
    hwpparser convert input.hwp output.txt
    hwpparser convert input.hwp output.pdf
    hwpparser convert input.md output.hwpx
    hwpparser text input.hwp
    hwpparser formats
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from . import __version__
from ._logging import get_logger, setup_logging
from .constants import DEFAULT_ENCODING
from .converter import convert, get_supported_conversions
from .exceptions import ConversionError, DependencyError, HWPFileNotFoundError, HWPParserError
from .reader import hwp_to_text

if TYPE_CHECKING:
    from collections.abc import Sequence

logger = get_logger("cli")


def create_parser() -> argparse.ArgumentParser:
    """CLI 파서를 생성합니다."""
    parser = argparse.ArgumentParser(
        prog="hwpparser",
        description="HWP Parser - 한글 문서 파서 및 변환기",
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"hwpparser {__version__}",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="상세 로깅 출력",
    )

    subparsers = parser.add_subparsers(dest="command", help="명령어")

    # convert 명령어
    convert_parser = subparsers.add_parser(
        "convert",
        help="문서 포맷 변환",
    )
    convert_parser.add_argument("input", help="입력 파일 경로")
    convert_parser.add_argument("output", help="출력 파일 경로")
    convert_parser.add_argument(
        "-f", "--from",
        dest="input_format",
        help="입력 포맷 (자동 감지됨)",
    )
    convert_parser.add_argument(
        "-t", "--to",
        dest="output_format",
        help="출력 포맷 (자동 감지됨)",
    )

    # text 명령어 (HWP → 텍스트 단축)
    text_parser = subparsers.add_parser(
        "text",
        help="HWP에서 텍스트 추출",
    )
    text_parser.add_argument("input", help="HWP 파일 경로")
    text_parser.add_argument(
        "-o", "--output",
        help="출력 파일 (미지정 시 stdout)",
    )

    # formats 명령어
    subparsers.add_parser(
        "formats",
        help="지원 포맷 변환 목록",
    )

    return parser


def cmd_convert(args: argparse.Namespace) -> int:
    """convert 명령어 실행."""
    result = convert(
        args.input,
        args.output,
        input_format=args.input_format,
        output_format=args.output_format,
    )

    if isinstance(result, str):
        print(result)
    else:
        print(f"생성됨: {result}", file=sys.stderr)

    return 0


def cmd_text(args: argparse.Namespace) -> int:
    """text 명령어 실행."""
    text = hwp_to_text(args.input)

    if args.output:
        Path(args.output).write_text(text, encoding=DEFAULT_ENCODING)
        print(f"생성됨: {args.output}", file=sys.stderr)
    else:
        print(text)

    return 0


def cmd_formats(args: argparse.Namespace) -> int:
    """formats 명령어 실행."""
    del args  # unused
    print("지원 변환:")
    for inp, out in sorted(get_supported_conversions()):
        print(f"  {inp} → {out}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """CLI 진입점.

    Args:
        argv: 명령줄 인자 (None이면 sys.argv 사용)

    Returns:
        종료 코드 (0: 성공, 1: 오류)
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    # 로깅 설정
    if getattr(args, "verbose", False):
        import logging
        setup_logging(level=logging.DEBUG)

    if args.command is None:
        parser.print_help()
        return 1

    # 명령어 → 핸들러 매핑
    handlers = {
        "convert": cmd_convert,
        "text": cmd_text,
        "formats": cmd_formats,
    }

    try:
        handler = handlers.get(args.command)
        if handler is None:
            logger.error("알 수 없는 명령어: %s", args.command)
            return 1
        return handler(args)

    except HWPFileNotFoundError as e:
        print(f"오류: {e}", file=sys.stderr)
        return 1
    except DependencyError as e:
        print(f"의존성 오류: {e}", file=sys.stderr)
        return 1
    except ConversionError as e:
        print(f"변환 오류: {e}", file=sys.stderr)
        return 1
    except HWPParserError as e:
        print(f"오류: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n중단됨", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
