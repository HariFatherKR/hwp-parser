"""
HWP Parser 유틸리티 함수

공통으로 사용되는 헬퍼 함수들을 모아둡니다.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

from ._logging import get_logger
from ._types import PathLike
from .constants import DEFAULT_ENCODING, EXTENSION_TO_FORMAT
from .exceptions import ConversionError, DependencyError, HWPFileNotFoundError

if TYPE_CHECKING:
    from collections.abc import Sequence

logger = get_logger("utils")


def ensure_path(path: PathLike) -> Path:
    """문자열 또는 Path를 Path 객체로 변환합니다.

    Args:
        path: 변환할 경로

    Returns:
        Path 객체
    """
    return Path(path) if isinstance(path, str) else Path(path)


def validate_file_exists(path: PathLike) -> Path:
    """파일 존재 여부를 확인하고 Path 객체를 반환합니다.

    Args:
        path: 확인할 파일 경로

    Returns:
        Path 객체

    Raises:
        HWPFileNotFoundError: 파일이 없을 경우
    """
    resolved = ensure_path(path)
    if not resolved.exists():
        logger.error("파일을 찾을 수 없습니다: %s", resolved)
        raise HWPFileNotFoundError(str(resolved))
    logger.debug("파일 확인됨: %s", resolved)
    return resolved


def check_command_exists(command: str, install_hint: str = "") -> None:
    """시스템에 명령어가 설치되어 있는지 확인합니다.

    Args:
        command: 확인할 명령어
        install_hint: 설치 방법 안내

    Raises:
        DependencyError: 명령어가 없을 경우
    """
    if shutil.which(command) is None:
        logger.error("명령어를 찾을 수 없습니다: %s", command)
        raise DependencyError(command, install_hint)
    logger.debug("명령어 확인됨: %s", command)


def run_command(
    args: Sequence[str],
    *,
    check: bool = True,
    capture_output: bool = True,
    text: bool = True,
    error_message: str = "",
) -> subprocess.CompletedProcess[str]:
    """subprocess를 실행하고 에러를 처리합니다.

    Args:
        args: 실행할 명령어와 인자들
        check: 실패 시 예외 발생 여부
        capture_output: 출력 캡처 여부
        text: 텍스트 모드 여부
        error_message: 에러 시 표시할 메시지

    Returns:
        subprocess.CompletedProcess 객체

    Raises:
        ConversionError: 명령어 실행 실패 시
        DependencyError: 명령어가 없을 경우
    """
    args_list = list(args)
    logger.debug("명령어 실행: %s", " ".join(args_list))

    try:
        result = subprocess.run(
            args_list,
            check=check,
            capture_output=capture_output,
            text=text,
        )
        logger.debug("명령어 성공: %s", args_list[0])
        return result
    except subprocess.CalledProcessError as e:
        message = error_message or f"명령어 실행 실패: {' '.join(args_list)}"
        if e.stderr:
            message += f"\n{e.stderr}"
        logger.error(message)
        raise ConversionError(message) from e
    except FileNotFoundError as e:
        logger.error("명령어를 찾을 수 없습니다: %s", args_list[0])
        raise DependencyError(args_list[0]) from e


def create_temp_file(
    content: str,
    suffix: str = ".txt",
    encoding: str = DEFAULT_ENCODING,
) -> Path:
    """임시 파일을 생성하고 경로를 반환합니다.

    Args:
        content: 파일에 쓸 내용
        suffix: 파일 확장자
        encoding: 인코딩

    Returns:
        생성된 임시 파일 경로

    Note:
        호출자가 파일 삭제를 책임집니다.
    """
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=suffix,
        delete=False,
        encoding=encoding,
    ) as f:
        f.write(content)
        path = Path(f.name)
        logger.debug("임시 파일 생성: %s", path)
        return path


def create_temp_dir() -> Path:
    """임시 디렉토리를 생성하고 경로를 반환합니다.

    Returns:
        생성된 임시 디렉토리 경로

    Note:
        호출자가 디렉토리 삭제를 책임집니다.
    """
    path = Path(tempfile.mkdtemp())
    logger.debug("임시 디렉토리 생성: %s", path)
    return path


def move_file(src: PathLike, dst: PathLike) -> Path:
    """파일을 이동합니다.

    Args:
        src: 원본 파일 경로
        dst: 대상 파일 경로

    Returns:
        이동된 파일 경로
    """
    src_path = ensure_path(src)
    dst_path = ensure_path(dst)
    shutil.move(str(src_path), str(dst_path))
    logger.debug("파일 이동: %s → %s", src_path, dst_path)
    return dst_path


def get_format_from_extension(path: PathLike) -> str:
    """파일 확장자에서 포맷을 추출합니다.

    Args:
        path: 파일 경로

    Returns:
        소문자 포맷 문자열 (예: 'hwp', 'pdf')
    """
    ext = ensure_path(path).suffix.lower()
    return EXTENSION_TO_FORMAT.get(ext, ext.lstrip("."))


# 하위 호환성을 위해 PathLike 재export
__all__ = [
    "PathLike",
    "ensure_path",
    "validate_file_exists",
    "check_command_exists",
    "run_command",
    "create_temp_file",
    "create_temp_dir",
    "move_file",
    "get_format_from_extension",
]
