"""Workflows 모듈 테스트."""

from __future__ import annotations

from pathlib import Path

import pytest

from hwpparser.workflows import (
    BatchResult,
    DirectoryHWPLoader,
    Document,
    HWPLoader,
    TextChunk,
    batch_extract_text,
    chunk_text,
    extract_metadata,
    hwp_to_chunks,
)


class TestChunkText:
    """chunk_text 함수 테스트."""

    def test_basic_chunking(self) -> None:
        """기본 청킹."""
        text = "A" * 500 + "\n\n" + "B" * 500 + "\n\n" + "C" * 500
        chunks = chunk_text(text, chunk_size=600, chunk_overlap=100)

        assert len(chunks) >= 2
        assert all(isinstance(c, TextChunk) for c in chunks)

    def test_empty_text(self) -> None:
        """빈 텍스트."""
        chunks = chunk_text("")
        assert chunks == []

    def test_chunk_metadata(self) -> None:
        """청크 메타데이터."""
        text = "Hello World"
        chunks = chunk_text(text, chunk_size=100)

        assert len(chunks) == 1
        assert "start" in chunks[0].metadata
        assert "end" in chunks[0].metadata


class TestHwpToChunks:
    """hwp_to_chunks 함수 테스트."""

    def test_hwp_chunking(self, sample_hwp: Path) -> None:
        """HWP 파일 청킹."""
        chunks = hwp_to_chunks(sample_hwp, chunk_size=200)

        assert len(chunks) > 0
        assert all(c.metadata.get("source") for c in chunks)
        assert all(c.metadata.get("source_type") == "hwp" for c in chunks)


class TestHWPLoader:
    """HWPLoader 클래스 테스트."""

    def test_single_file(self, sample_hwp: Path) -> None:
        """단일 파일 로드."""
        loader = HWPLoader(sample_hwp)
        docs = loader.load()

        assert len(docs) == 1
        assert isinstance(docs[0], Document)
        assert len(docs[0].page_content) > 0
        assert docs[0].metadata["file_type"] == "hwp"

    def test_lazy_load(self, sample_hwp: Path) -> None:
        """lazy_load 테스트."""
        loader = HWPLoader(sample_hwp)

        docs = list(loader.lazy_load())
        assert len(docs) == 1


class TestDirectoryHWPLoader:
    """DirectoryHWPLoader 클래스 테스트."""

    def test_directory_load(self, fixtures_dir: Path) -> None:
        """디렉토리 로드."""
        loader = DirectoryHWPLoader(fixtures_dir)
        docs = loader.load()

        assert len(docs) >= 1


class TestExtractMetadata:
    """extract_metadata 함수 테스트."""

    def test_metadata_extraction(self, sample_hwp: Path) -> None:
        """메타데이터 추출."""
        meta = extract_metadata(sample_hwp)

        assert "source" in meta
        assert "file_name" in meta
        assert "file_size" in meta
        assert "char_count" in meta
        assert "word_count" in meta
        assert meta["char_count"] > 0


class TestBatchResult:
    """BatchResult 클래스 테스트."""

    def test_success_rate(self) -> None:
        """성공률 계산."""
        result = BatchResult(total=10, success=8, failed=2)
        assert result.success_rate == 0.8

    def test_empty_result(self) -> None:
        """빈 결과."""
        result = BatchResult()
        assert result.success_rate == 0.0
