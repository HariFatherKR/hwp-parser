"""
HWP Reader - HWP 문서에서 콘텐츠 추출

pyhwp를 사용하여 HWP 5.0+ 포맷(바이너리 OLE2)을 처리합니다.
"""

from __future__ import annotations

import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ._logging import get_logger
from ._types import PathLike
from .constants import (
    DEFAULT_ENCODING,
    LIBREOFFICE_INSTALL_HINT,
    PYHWP_INSTALL_HINT,
    Command,
)
from .exceptions import ConversionError
from .utils import (
    check_command_exists,
    create_temp_dir,
    ensure_path,
    move_file,
    run_command,
    validate_file_exists,
)

logger = get_logger("reader")


@dataclass(slots=True)
class HWPDocument:
    """파싱된 HWP 문서를 나타내는 데이터 클래스.

    Attributes:
        path: 원본 파일 경로
        text: 추출된 평문 텍스트
        html: 변환된 HTML
        metadata: 문서 메타데이터
    """

    path: Path
    text: str = ""
    html: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return self.text

    def __repr__(self) -> str:
        return f"HWPDocument(path={self.path!r}, text_length={len(self.text)})"


class HWPReader:
    """HWP 문서를 읽고 파싱하는 클래스.

    컨텍스트 매니저로 사용할 수 있습니다.

    Example:
        >>> with HWPReader("document.hwp") as reader:
        ...     print(reader.text)
        ...     reader.to_pdf("output.pdf")

        >>> # 또는 직접 사용
        >>> reader = HWPReader("document.hwp")
        >>> print(reader.text)
    """

    __slots__ = ("path", "_text", "_html")

    def __init__(self, path: PathLike) -> None:
        """HWPReader를 초기화합니다.

        Args:
            path: HWP 파일 경로

        Raises:
            HWPFileNotFoundError: 파일이 없을 경우
        """
        self.path = validate_file_exists(path)
        self._text: str | None = None
        self._html: str | None = None
        logger.info("HWPReader 초기화: %s", self.path)

    def __enter__(self) -> HWPReader:
        """컨텍스트 매니저 진입."""
        return self

    def __exit__(self, exc_type: type | None, exc_val: BaseException | None, exc_tb: Any) -> None:
        """컨텍스트 매니저 종료."""
        # 현재는 정리할 리소스 없음
        pass

    def __repr__(self) -> str:
        return f"HWPReader(path={self.path!r})"

    @property
    def text(self) -> str:
        """HWP에서 평문 텍스트를 추출합니다 (lazy loading)."""
        if self._text is None:
            self._text = hwp_to_text(self.path)
        return self._text

    @property
    def html(self) -> str:
        """HWP를 HTML로 변환합니다 (lazy loading)."""
        if self._html is None:
            self._html = hwp_to_html(self.path)
        return self._html

    def to_odt(self, output_path: PathLike) -> Path:
        """HWP를 ODT 포맷으로 변환합니다.

        Args:
            output_path: 출력 파일 경로

        Returns:
            생성된 ODT 파일 경로
        """
        return hwp_to_odt(self.path, output_path)

    def to_pdf(self, output_path: PathLike) -> Path:
        """HWP를 PDF로 변환합니다 (LibreOffice 필요).

        Args:
            output_path: 출력 파일 경로

        Returns:
            생성된 PDF 파일 경로
        """
        return hwp_to_pdf(self.path, output_path)

    def to_document(self) -> HWPDocument:
        """HWPDocument 데이터 클래스로 반환합니다."""
        return HWPDocument(
            path=self.path,
            text=self.text,
            html=self.html,
        )


def read_hwp(path: PathLike) -> HWPReader:
    """HWP 파일을 읽고 리더 객체를 반환합니다.

    Args:
        path: HWP 파일 경로

    Returns:
        HWPReader 인스턴스
    """
    return HWPReader(path)


def hwp_to_text(path: PathLike) -> str:
    """HWP 파일에서 평문 텍스트를 추출합니다.

    hwp5txt CLI를 사용합니다.

    Args:
        path: HWP 파일 경로

    Returns:
        추출된 텍스트

    Raises:
        DependencyError: pyhwp가 설치되지 않은 경우
        ConversionError: 변환 실패 시
    """
    path = validate_file_exists(path)
    check_command_exists(Command.HWP5TXT, PYHWP_INSTALL_HINT)

    logger.info("텍스트 추출 시작: %s", path)
    result = run_command(
        [Command.HWP5TXT, str(path)],
        error_message=f"HWP 텍스트 추출 실패: {path}",
    )
    logger.info("텍스트 추출 완료: %d 문자", len(result.stdout))
    return result.stdout


def hwp_to_html(path: PathLike, output_dir: Path | None = None) -> str:
    """HWP를 HTML로 변환합니다.

    hwp5html CLI를 사용합니다.

    Args:
        path: HWP 파일 경로
        output_dir: 출력 디렉토리 (기본값: 임시 디렉토리)

    Returns:
        생성된 HTML 내용
    """
    path = validate_file_exists(path)
    check_command_exists(Command.HWP5HTML, PYHWP_INSTALL_HINT)

    if output_dir is None:
        output_dir = create_temp_dir()

    output_file = output_dir / "index.html"

    logger.info("HTML 변환 시작: %s", path)
    run_command(
        [Command.HWP5HTML, str(path), "--output", str(output_file)],
        error_message=f"HWP → HTML 변환 실패: {path}",
    )

    html_content = output_file.read_text(encoding=DEFAULT_ENCODING)
    logger.info("HTML 변환 완료: %d 문자", len(html_content))
    return html_content


def hwp_to_odt(path: PathLike, output_path: PathLike) -> Path:
    """HWP를 ODT로 변환합니다.

    hwp5odt CLI를 사용합니다.

    Args:
        path: HWP 파일 경로
        output_path: 출력 ODT 파일 경로

    Returns:
        생성된 ODT 파일 경로
    """
    path = validate_file_exists(path)
    output_path = ensure_path(output_path)
    check_command_exists(Command.HWP5ODT, PYHWP_INSTALL_HINT)

    logger.info("ODT 변환 시작: %s → %s", path, output_path)
    run_command(
        [Command.HWP5ODT, str(path), "--output", str(output_path)],
        error_message=f"HWP → ODT 변환 실패: {path}",
    )
    logger.info("ODT 변환 완료: %s", output_path)
    return output_path


def hwp_to_pdf(path: PathLike, output_path: PathLike) -> Path:
    """HWP를 PDF로 변환합니다.

    ODT를 거쳐 LibreOffice로 PDF를 생성합니다.

    Args:
        path: HWP 파일 경로
        output_path: 출력 PDF 파일 경로

    Returns:
        생성된 PDF 파일 경로

    Raises:
        DependencyError: LibreOffice가 설치되지 않은 경우
    """
    path = validate_file_exists(path)
    output_path = ensure_path(output_path)
    check_command_exists(Command.SOFFICE, LIBREOFFICE_INSTALL_HINT)

    logger.info("PDF 변환 시작: %s → %s", path, output_path)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        temp_odt = temp_dir_path / "temp.odt"

        # HWP → ODT
        hwp_to_odt(path, temp_odt)

        # ODT → PDF (LibreOffice)
        run_command(
            [Command.SOFFICE, "--headless", "--convert-to", "pdf", "--outdir", temp_dir, str(temp_odt)],
            error_message=f"ODT → PDF 변환 실패: {temp_odt}",
        )

        temp_pdf = temp_dir_path / "temp.pdf"
        if not temp_pdf.exists():
            raise ConversionError(f"PDF 파일이 생성되지 않았습니다: {temp_pdf}")

        move_file(temp_pdf, output_path)

    logger.info("PDF 변환 완료: %s", output_path)
    return output_path
