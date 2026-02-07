"""HWP Reader 테스트."""

from __future__ import annotations

from pathlib import Path

import pytest

from hwpparser import HWPReader, hwp_to_text, read_hwp
from hwpparser.exceptions import HWPFileNotFoundError


class TestHWPReader:
    """HWPReader 클래스 테스트."""

    def test_init_with_valid_file(self, sample_hwp: Path) -> None:
        """유효한 파일로 초기화."""
        reader = HWPReader(sample_hwp)
        assert reader.path == sample_hwp

    def test_init_with_string_path(self, sample_hwp: Path) -> None:
        """문자열 경로로 초기화."""
        reader = HWPReader(str(sample_hwp))
        assert reader.path == sample_hwp

    def test_init_file_not_found(self) -> None:
        """없는 파일로 초기화 시 오류."""
        with pytest.raises(HWPFileNotFoundError):
            HWPReader("존재하지_않는_파일.hwp")

    def test_text_property(self, sample_hwp: Path) -> None:
        """text 프로퍼티 테스트."""
        reader = HWPReader(sample_hwp)
        text = reader.text

        assert isinstance(text, str)
        assert len(text) > 0

    def test_text_is_cached(self, sample_hwp: Path) -> None:
        """text가 캐싱되는지 확인."""
        reader = HWPReader(sample_hwp)
        text1 = reader.text
        text2 = reader.text

        assert text1 is text2

    def test_context_manager(self, sample_hwp: Path) -> None:
        """컨텍스트 매니저 테스트."""
        with HWPReader(sample_hwp) as reader:
            assert reader.path == sample_hwp
            text = reader.text
            assert len(text) > 0

    def test_repr(self, sample_hwp: Path) -> None:
        """__repr__ 테스트."""
        reader = HWPReader(sample_hwp)
        repr_str = repr(reader)
        assert "HWPReader" in repr_str
        assert str(sample_hwp) in repr_str


class TestHwpToText:
    """hwp_to_text 함수 테스트."""

    def test_extract_text(self, sample_hwp: Path) -> None:
        """텍스트 추출."""
        text = hwp_to_text(sample_hwp)

        assert isinstance(text, str)
        assert len(text) > 0
        # 한글 샘플 파일 내용 확인
        assert "한글" in text or "문서" in text or "본문" in text

    def test_file_not_found(self) -> None:
        """없는 파일."""
        with pytest.raises(HWPFileNotFoundError):
            hwp_to_text("없는파일.hwp")


class TestReadHwp:
    """read_hwp 함수 테스트."""

    def test_returns_reader(self, sample_hwp: Path) -> None:
        """HWPReader 반환."""
        reader = read_hwp(sample_hwp)

        assert isinstance(reader, HWPReader)
        assert reader.path == sample_hwp
