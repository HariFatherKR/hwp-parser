"""
HWPX Writer - 다양한 포맷에서 HWPX 문서 생성

pypandoc-hwpx를 사용하여 HWPX(XML 기반) 포맷으로 변환합니다.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from ._logging import get_logger
from ._types import PathLike
from .constants import (
    EXTENSION_TO_FORMAT,
    PYPANDOC_INSTALL_HINT,
    Command,
)
from .utils import (
    check_command_exists,
    create_temp_file,
    ensure_path,
    run_command,
    validate_file_exists,
)

logger = get_logger("writer")

# 지원하는 입력 포맷
InputFormat = Literal["markdown", "html", "docx"]


class HWPXWriter:
    """다양한 소스에서 HWPX 문서를 생성하는 클래스.

    Example:
        >>> writer = HWPXWriter()
        >>> writer.from_markdown("# 제목", "output.hwpx")
        >>> writer.from_file("document.md", "output.hwpx")
    """

    __slots__ = ()

    def __init__(self) -> None:
        """HWPXWriter를 초기화하고 의존성을 확인합니다."""
        self._check_dependencies()
        logger.info("HWPXWriter 초기화됨")

    def _check_dependencies(self) -> None:
        """pypandoc-hwpx가 설치되어 있는지 확인합니다."""
        check_command_exists(Command.PYPANDOC_HWPX, PYPANDOC_INSTALL_HINT)

    def from_markdown(self, markdown: str, output_path: PathLike) -> Path:
        """마크다운 콘텐츠를 HWPX로 변환합니다.

        Args:
            markdown: 마크다운 텍스트
            output_path: 출력 HWPX 파일 경로

        Returns:
            생성된 HWPX 파일 경로
        """
        return write_hwpx(markdown, output_path, "markdown")

    def from_html(self, html: str, output_path: PathLike) -> Path:
        """HTML 콘텐츠를 HWPX로 변환합니다.

        Args:
            html: HTML 텍스트
            output_path: 출력 HWPX 파일 경로

        Returns:
            생성된 HWPX 파일 경로
        """
        return write_hwpx(html, output_path, "html")

    def from_file(
        self,
        input_path: PathLike,
        output_path: PathLike,
        input_format: InputFormat | None = None,
    ) -> Path:
        """파일을 HWPX로 변환합니다.

        Args:
            input_path: 입력 파일 경로
            output_path: 출력 HWPX 파일 경로
            input_format: 입력 포맷 (None이면 확장자에서 자동 감지)

        Returns:
            생성된 HWPX 파일 경로
        """
        input_path = validate_file_exists(input_path)
        output_path = ensure_path(output_path)

        # 포맷 자동 감지
        if input_format is None:
            ext = input_path.suffix.lower()
            detected = EXTENSION_TO_FORMAT.get(ext)
            if detected in ("markdown", "html", "docx"):
                input_format = detected  # type: ignore[assignment]

        logger.info("파일 → HWPX 변환: %s → %s", input_path, output_path)

        cmd = [Command.PYPANDOC_HWPX, str(input_path), "-o", str(output_path)]
        if input_format:
            cmd.extend(["-f", input_format])

        run_command(cmd, error_message=f"파일 → HWPX 변환 실패: {input_path}")
        logger.info("HWPX 생성 완료: %s", output_path)
        return output_path


def write_hwpx(
    content: str,
    output_path: PathLike,
    content_format: str = "markdown",
) -> Path:
    """콘텐츠를 HWPX 파일로 저장합니다.

    Args:
        content: 저장할 콘텐츠 (마크다운, HTML 등)
        output_path: 출력 HWPX 파일 경로
        content_format: 입력 콘텐츠 포맷 (markdown, html)

    Returns:
        생성된 HWPX 파일 경로
    """
    check_command_exists(Command.PYPANDOC_HWPX, PYPANDOC_INSTALL_HINT)
    output_path = ensure_path(output_path)

    # 확장자 결정
    suffix_map = {"markdown": ".md", "html": ".html"}
    suffix = suffix_map.get(content_format, ".txt")

    # 임시 파일에 콘텐츠 저장
    temp_file = create_temp_file(content, suffix=suffix)

    logger.info("콘텐츠 → HWPX 변환 시작")
    try:
        run_command(
            [Command.PYPANDOC_HWPX, str(temp_file), "-o", str(output_path)],
            error_message="콘텐츠 → HWPX 변환 실패",
        )
    finally:
        temp_file.unlink(missing_ok=True)

    logger.info("HWPX 생성 완료: %s", output_path)
    return output_path


def markdown_to_hwpx(markdown: str, output_path: PathLike) -> Path:
    """마크다운을 HWPX로 변환하는 편의 함수.

    Args:
        markdown: 마크다운 텍스트
        output_path: 출력 HWPX 파일 경로

    Returns:
        생성된 HWPX 파일 경로
    """
    return write_hwpx(markdown, output_path, "markdown")


def html_to_hwpx(html: str, output_path: PathLike) -> Path:
    """HTML을 HWPX로 변환하는 편의 함수.

    Args:
        html: HTML 텍스트
        output_path: 출력 HWPX 파일 경로

    Returns:
        생성된 HWPX 파일 경로
    """
    return write_hwpx(html, output_path, "html")
