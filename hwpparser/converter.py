"""
Converter - HWP/HWPX 문서 통합 변환 인터페이스

지원 변환:
- HWP → Text, HTML, ODT, PDF
- Markdown/HTML/DOCX → HWPX
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from ._logging import get_logger
from ._types import PathLike
from .constants import DEFAULT_ENCODING
from .exceptions import UnsupportedFormatError
from .reader import hwp_to_html, hwp_to_odt, hwp_to_pdf, hwp_to_text
from .utils import ensure_path, get_format_from_extension, validate_file_exists
from .writer import write_hwpx

logger = get_logger("converter")

# 변환 함수 타입
ConverterFunc = Callable[[PathLike, PathLike | None], str | Path]


def _hwp_to_html_file(input_path: PathLike, output_path: PathLike | None) -> Path:
    """HWP → HTML 파일로 저장."""
    html_content = hwp_to_html(input_path)
    if output_path is None:
        raise ValueError("HTML 파일 출력에는 output_path가 필요합니다.")
    output = ensure_path(output_path)
    output.write_text(html_content, encoding=DEFAULT_ENCODING)
    return output


def _file_to_hwpx(input_path: PathLike, output_path: PathLike | None, format_type: str) -> Path:
    """파일 → HWPX 변환."""
    if output_path is None:
        raise ValueError("HWPX 출력에는 output_path가 필요합니다.")
    content = Path(input_path).read_text(encoding=DEFAULT_ENCODING)
    return write_hwpx(content, output_path, format_type)


# 지원하는 변환 조합: (입력 포맷, 출력 포맷) → 변환 함수
SUPPORTED_CONVERSIONS: dict[tuple[str, str], ConverterFunc] = {
    # HWP → 다른 포맷
    ("hwp", "text"): lambda p, _: hwp_to_text(p),
    ("hwp", "txt"): lambda p, _: hwp_to_text(p),
    ("hwp", "html"): _hwp_to_html_file,
    ("hwp", "odt"): lambda p, o: hwp_to_odt(p, o) if o else Path(),
    ("hwp", "pdf"): lambda p, o: hwp_to_pdf(p, o) if o else Path(),
    # 다른 포맷 → HWPX
    ("markdown", "hwpx"): lambda p, o: _file_to_hwpx(p, o, "markdown"),
    ("md", "hwpx"): lambda p, o: _file_to_hwpx(p, o, "markdown"),
    ("html", "hwpx"): lambda p, o: _file_to_hwpx(p, o, "html"),
}


def convert(
    input_path: PathLike,
    output_path: PathLike | None = None,
    *,
    input_format: str | None = None,
    output_format: str | None = None,
) -> str | Path:
    """문서를 다른 포맷으로 변환합니다.

    Args:
        input_path: 입력 파일 경로
        output_path: 출력 파일 경로 (텍스트 출력 시 선택)
        input_format: 입력 포맷 (None이면 확장자에서 자동 감지)
        output_format: 출력 포맷 (None이면 출력 확장자에서 자동 감지)

    Returns:
        텍스트 출력 시 str, 파일 출력 시 Path

    Raises:
        HWPFileNotFoundError: 입력 파일이 없을 경우
        UnsupportedFormatError: 지원하지 않는 변환일 경우
        ConversionError: 변환 실패 시

    Examples:
        >>> # HWP → 텍스트
        >>> text = convert("document.hwp", output_format="text")

        >>> # HWP → PDF
        >>> convert("document.hwp", "output.pdf")

        >>> # 마크다운 → HWPX
        >>> convert("document.md", "output.hwpx")
    """
    input_path = validate_file_exists(input_path)

    # 포맷 자동 감지
    if input_format is None:
        input_format = get_format_from_extension(input_path)

    if output_format is None and output_path is not None:
        output_format = get_format_from_extension(output_path)

    if output_format is None:
        raise ValueError("output_format을 지정하거나 출력 파일 경로를 제공해야 합니다.")

    # 정규화
    input_format = input_format.lower()
    output_format = output_format.lower()

    logger.info("변환 시작: %s (%s) → %s", input_path, input_format, output_format)

    # 변환 함수 찾기
    conversion_key = (input_format, output_format)
    converter_func = SUPPORTED_CONVERSIONS.get(conversion_key)

    if converter_func is None:
        supported = [f"{i}→{o}" for i, o in SUPPORTED_CONVERSIONS]
        raise UnsupportedFormatError(
            f"{input_format}→{output_format}",
            supported,
        )

    # 텍스트 출력 (파일 불필요)
    if output_format in ("text", "txt"):
        result = converter_func(input_path, None)
        logger.info("텍스트 추출 완료: %d 문자", len(str(result)))
        return result

    if output_path is None:
        raise ValueError(f"{output_format} 출력에는 output_path가 필요합니다.")

    result = converter_func(input_path, output_path)
    logger.info("변환 완료: %s", result)
    return result


def get_supported_conversions() -> list[tuple[str, str]]:
    """지원하는 (입력 포맷, 출력 포맷) 쌍 목록을 반환합니다."""
    return list(SUPPORTED_CONVERSIONS.keys())


def get_supported_input_formats() -> list[str]:
    """지원하는 입력 포맷 목록을 반환합니다."""
    return sorted({fmt for fmt, _ in SUPPORTED_CONVERSIONS})


def get_supported_output_formats() -> list[str]:
    """지원하는 출력 포맷 목록을 반환합니다."""
    return sorted({fmt for _, fmt in SUPPORTED_CONVERSIONS})
