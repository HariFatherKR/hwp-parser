"""Pytest 설정 및 공통 fixture."""

from __future__ import annotations

from pathlib import Path

import pytest


FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures_dir() -> Path:
    """테스트 fixtures 디렉토리 경로."""
    return FIXTURES_DIR


@pytest.fixture
def sample_hwp(fixtures_dir: Path) -> Path:
    """샘플 HWP 파일 경로."""
    path = fixtures_dir / "sample.hwp"
    if not path.exists():
        pytest.skip("샘플 HWP 파일 없음")
    return path


@pytest.fixture
def tmp_output(tmp_path: Path) -> Path:
    """임시 출력 디렉토리."""
    return tmp_path
