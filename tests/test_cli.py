"""CLI 테스트."""

from __future__ import annotations

from pathlib import Path

import pytest

from hwpparser.cli import main


class TestCLI:
    """CLI 테스트."""

    def test_version(self, capsys: pytest.CaptureFixture[str]) -> None:
        """버전 출력."""
        with pytest.raises(SystemExit) as exc_info:
            main(["--version"])

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "hwpparser" in captured.out

    def test_no_command(self) -> None:
        """명령어 없이 실행."""
        result = main([])
        assert result == 1

    def test_formats(self, capsys: pytest.CaptureFixture[str]) -> None:
        """formats 명령어."""
        result = main(["formats"])

        assert result == 0
        captured = capsys.readouterr()
        assert "hwp" in captured.out

    def test_text_file_not_found(self) -> None:
        """text 명령어 - 파일 없음."""
        result = main(["text", "없는파일.hwp"])
        assert result == 1

    def test_text_command(self, sample_hwp: Path, capsys: pytest.CaptureFixture[str]) -> None:
        """text 명령어."""
        result = main(["text", str(sample_hwp)])

        assert result == 0
        captured = capsys.readouterr()
        assert len(captured.out) > 0
