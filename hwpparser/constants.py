"""
HWP Parser 상수 정의

모든 상수를 한 곳에서 관리합니다.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Final


class InputFormat(StrEnum):
    """지원하는 입력 포맷."""

    HWP = "hwp"
    MARKDOWN = "markdown"
    MD = "md"
    HTML = "html"
    DOCX = "docx"


class OutputFormat(StrEnum):
    """지원하는 출력 포맷."""

    TEXT = "text"
    TXT = "txt"
    HTML = "html"
    ODT = "odt"
    PDF = "pdf"
    HWPX = "hwpx"


# 의존성 설치 안내
PYHWP_INSTALL_HINT: Final[str] = "pip install pyhwp"
PYPANDOC_INSTALL_HINT: Final[str] = "pip install pypandoc-hwpx"
PANDOC_INSTALL_HINT: Final[str] = "brew install pandoc"
CHROME_INSTALL_HINT: Final[str] = "brew install --cask google-chrome"
# DEPRECATED: LibreOffice는 더 이상 사용하지 않음 (Chrome headless로 대체)
# LIBREOFFICE_INSTALL_HINT: Final[str] = "brew install --cask libreoffice"

# Chrome 경로 (macOS)
CHROME_PATHS: Final[list[str]] = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/opt/homebrew/bin/chromium",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium-browser",
]

# 기본 인코딩
DEFAULT_ENCODING: Final[str] = "utf-8"

# 확장자 → 포맷 매핑
EXTENSION_TO_FORMAT: Final[dict[str, str]] = {
    ".hwp": "hwp",
    ".hwpx": "hwpx",
    ".md": "markdown",
    ".markdown": "markdown",
    ".html": "html",
    ".htm": "html",
    ".docx": "docx",
    ".txt": "text",
    ".odt": "odt",
    ".pdf": "pdf",
}

# CLI 명령어
class Command(StrEnum):
    """외부 CLI 명령어."""

    HWP5TXT = "hwp5txt"
    HWP5HTML = "hwp5html"
    HWP5ODT = "hwp5odt"
    PYPANDOC_HWPX = "pypandoc-hwpx"
    # DEPRECATED: soffice는 더 이상 사용하지 않음 (Chrome headless로 대체)
    # SOFFICE = "soffice"
