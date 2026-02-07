"""Converter 모듈 테스트."""

from __future__ import annotations

from pathlib import Path

import pytest

from hwpparser import convert, get_supported_conversions
from hwpparser.exceptions import HWPFileNotFoundError, UnsupportedFormatError


class TestConvert:
    """convert 함수 테스트."""

    def test_hwp_to_text(self, sample_hwp: Path) -> None:
        """HWP → 텍스트 변환."""
        text = convert(sample_hwp, output_format="text")

        assert isinstance(text, str)
        assert len(text) > 0

    def test_unsupported_conversion(self, tmp_output: Path) -> None:
        """지원하지 않는 변환."""
        input_file = tmp_output / "test.xyz"
        input_file.write_text("test")

        with pytest.raises(UnsupportedFormatError):
            convert(input_file, tmp_output / "output.abc")

    def test_file_not_found(self) -> None:
        """없는 파일."""
        with pytest.raises(HWPFileNotFoundError):
            convert("없는파일.hwp", "output.txt")

    def test_auto_detect_format(self, sample_hwp: Path, tmp_output: Path) -> None:
        """포맷 자동 감지."""
        output_file = tmp_output / "output.txt"
        result = convert(sample_hwp, output_file)

        # 텍스트 포맷이면 문자열 반환
        assert isinstance(result, str)


class TestGetSupportedConversions:
    """get_supported_conversions 함수 테스트."""

    def test_returns_list(self) -> None:
        """리스트 반환."""
        conversions = get_supported_conversions()

        assert isinstance(conversions, list)
        assert len(conversions) > 0

    def test_hwp_to_text_supported(self) -> None:
        """HWP → text 지원."""
        conversions = get_supported_conversions()

        assert ("hwp", "text") in conversions or ("hwp", "txt") in conversions

    def test_md_to_hwpx_supported(self) -> None:
        """MD → HWPX 지원."""
        conversions = get_supported_conversions()

        assert ("md", "hwpx") in conversions or ("markdown", "hwpx") in conversions
