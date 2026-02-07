"""
HWP Parser 예외 클래스

모든 커스텀 예외를 한 곳에서 관리합니다.
빌트인 예외와 이름 충돌을 피하기 위해 HWP 접두사를 사용합니다.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


class HWPParserError(Exception):
    """HWP Parser 기본 예외 클래스."""

    pass


class HWPFileNotFoundError(HWPParserError, FileNotFoundError):
    """파일을 찾을 수 없을 때 발생.

    빌트인 FileNotFoundError도 상속하여 호환성 유지.
    """

    __slots__ = ("path",)

    def __init__(self, path: str) -> None:
        self.path = path
        super().__init__(f"파일을 찾을 수 없습니다: {path}")


class ConversionError(HWPParserError):
    """문서 변환 중 오류 발생."""

    __slots__ = ("source_format", "target_format")

    def __init__(
        self,
        message: str,
        source_format: str = "",
        target_format: str = "",
    ) -> None:
        self.source_format = source_format
        self.target_format = target_format
        super().__init__(message)


class DependencyError(HWPParserError):
    """필수 의존성이 없을 때 발생."""

    __slots__ = ("dependency", "install_hint")

    def __init__(self, dependency: str, install_hint: str = "") -> None:
        self.dependency = dependency
        self.install_hint = install_hint
        message = f"필수 의존성을 찾을 수 없습니다: {dependency}"
        if install_hint:
            message += f"\n설치 방법: {install_hint}"
        super().__init__(message)


class UnsupportedFormatError(HWPParserError):
    """지원하지 않는 포맷일 때 발생."""

    __slots__ = ("format_name", "supported")

    def __init__(
        self,
        format_name: str,
        supported: Sequence[str] | None = None,
    ) -> None:
        self.format_name = format_name
        self.supported: list[str] = list(supported) if supported else []
        message = f"지원하지 않는 포맷입니다: {format_name}"
        if self.supported:
            message += f"\n지원 포맷: {', '.join(self.supported)}"
        super().__init__(message)


# 하위 호환성을 위한 별칭 (deprecated)
FileNotFoundError = HWPFileNotFoundError  # noqa: A001
