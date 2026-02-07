"""
HWP Parser 타입 정의

TypeAlias와 Protocol을 사용한 타입 정의.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import TYPE_CHECKING, Protocol, TypeAlias, Union, runtime_checkable

if TYPE_CHECKING:
    from os import PathLike as OSPathLike

# 경로 타입
PathLike: TypeAlias = Union[str, Path, "OSPathLike[str]"]

# 변환 결과 타입
ConversionResult: TypeAlias = Union[str, Path]


@runtime_checkable
class Converter(Protocol):
    """문서 변환기 프로토콜.

    새로운 변환기를 추가할 때 이 프로토콜을 구현합니다.
    """

    def convert(self, input_path: PathLike, output_path: PathLike) -> Path:
        """문서를 변환합니다.

        Args:
            input_path: 입력 파일 경로
            output_path: 출력 파일 경로

        Returns:
            생성된 파일 경로
        """
        ...


@runtime_checkable
class TextExtractor(Protocol):
    """텍스트 추출기 프로토콜."""

    def extract(self, input_path: PathLike) -> str:
        """문서에서 텍스트를 추출합니다.

        Args:
            input_path: 입력 파일 경로

        Returns:
            추출된 텍스트
        """
        ...


@runtime_checkable
class CommandRunner(Protocol):
    """외부 명령어 실행기 프로토콜.

    테스트 시 모킹을 위해 사용합니다.
    """

    def run(
        self,
        args: list[str],
        *,
        check: bool = True,
        capture_output: bool = True,
        text: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        """명령어를 실행합니다."""
        ...
