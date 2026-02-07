"""
HWP Parser 로깅 설정

구조화된 로깅을 제공합니다.
"""

from __future__ import annotations

import logging
import sys
from typing import Final

# 기본 로거 이름
LOGGER_NAME: Final[str] = "hwpparser"


def get_logger(name: str | None = None) -> logging.Logger:
    """모듈별 로거를 반환합니다.

    Args:
        name: 로거 이름 (None이면 기본 로거)

    Returns:
        logging.Logger 인스턴스
    """
    if name is None:
        return logging.getLogger(LOGGER_NAME)
    return logging.getLogger(f"{LOGGER_NAME}.{name}")


def setup_logging(
    level: int = logging.INFO,
    *,
    format_string: str | None = None,
    stream: bool = True,
) -> None:
    """로깅을 설정합니다.

    Args:
        level: 로그 레벨
        format_string: 로그 포맷 (None이면 기본값)
        stream: stderr로 출력할지 여부
    """
    logger = get_logger()
    logger.setLevel(level)

    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    formatter = logging.Formatter(format_string)

    if stream and not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(formatter)
        logger.addHandler(handler)


# 편의를 위한 기본 로거
logger = get_logger()
