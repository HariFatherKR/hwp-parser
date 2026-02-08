"""
HWP Reader - HWP 문서에서 콘텐츠 추출

pyhwp를 사용하여 HWP 5.0+ 포맷(바이너리 OLE2)을 처리합니다.
"""

from __future__ import annotations

import re
import tempfile
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Tuple

from bs4 import BeautifulSoup, NavigableString, XMLParsedAsHTMLWarning

# XML을 HTML 파서로 파싱할 때 경고 억제
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

from ._logging import get_logger
from ._types import PathLike
from .constants import (
    CHROME_INSTALL_HINT,
    CHROME_PATHS,
    DEFAULT_ENCODING,
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

    __slots__ = ("path", "_text", "_html", "_rich_text")

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
        self._rich_text: str | None = None
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

    @property
    def rich_text(self) -> str:
        """표를 포함한 리치 텍스트를 추출합니다 (lazy loading).
        
        HTML을 파싱하여 표를 마크다운 형식으로 포함합니다.
        """
        if self._rich_text is None:
            self._rich_text = hwp_to_rich_text(self.path)
        return self._rich_text

    def to_odt(self, output_path: PathLike) -> Path:
        """HWP를 ODT 포맷으로 변환합니다.

        Args:
            output_path: 출력 파일 경로

        Returns:
            생성된 ODT 파일 경로
        """
        return hwp_to_odt(self.path, output_path)

    def to_pdf(self, output_path: PathLike) -> Path:
        """HWP를 PDF로 변환합니다 (Chrome headless 사용).

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


def _extract_cell_text(cell) -> str:
    """테이블 셀에서 텍스트를 추출합니다."""
    texts = []
    for elem in cell.descendants:
        if isinstance(elem, NavigableString):
            text = str(elem).strip()
            # 캐리지 리턴 및 특수문자 제거
            text = text.replace('\r', '').replace('\n', ' ')
            if text:
                texts.append(text)
    return ' '.join(texts).strip()


def _parse_table_to_markdown(table) -> str:
    """HTML 테이블을 마크다운 형식으로 변환합니다."""
    rows = table.find_all('tr')
    if not rows:
        return ""
    
    # 각 행에서 셀 추출
    table_data: List[List[Tuple[str, int, int]]] = []  # (text, rowspan, colspan)
    
    for row in rows:
        cells = row.find_all(['td', 'th'])
        row_data = []
        for cell in cells:
            text = _extract_cell_text(cell)
            rowspan = int(cell.get('rowspan', 1))
            colspan = int(cell.get('colspan', 1))
            row_data.append((text, rowspan, colspan))
        table_data.append(row_data)
    
    if not table_data:
        return ""
    
    # 간단한 마크다운 테이블 생성 (colspan/rowspan 무시하고 평탄화)
    lines = []
    
    # 모든 행 처리
    for i, row_cells in enumerate(table_data):
        if not row_cells:
            continue
        
        # 셀 텍스트 추출 (colspan 처리)
        cell_texts = []
        for text, rowspan, colspan in row_cells:
            cell_texts.append(text if text else " ")
            # colspan > 1이면 빈 셀 추가
            for _ in range(colspan - 1):
                cell_texts.append(" ")
        
        line = "| " + " | ".join(cell_texts) + " |"
        lines.append(line)
        
        # 첫 번째 행 후에 구분선 추가
        if i == 0:
            separator = "|" + "|".join(["---" for _ in cell_texts]) + "|"
            lines.append(separator)
    
    return "\n".join(lines)


def _html_to_rich_text(html_content: str) -> str:
    """HTML을 표를 포함한 리치 텍스트로 변환합니다."""
    soup = BeautifulSoup(html_content, 'lxml')
    
    # 표를 마크다운으로 변환하고 플레이스홀더로 대체
    tables = soup.find_all('table')
    table_markdowns = []
    
    for i, table in enumerate(tables):
        md = _parse_table_to_markdown(table)
        if md:
            table_markdowns.append(md)
            # 테이블을 플레이스홀더로 대체
            placeholder = soup.new_tag('div')
            placeholder.string = f"__TABLE_{i}__"
            table.replace_with(placeholder)
    
    # 텍스트 추출
    text_parts = []
    for elem in soup.body.descendants if soup.body else soup.descendants:
        if isinstance(elem, NavigableString):
            text = str(elem).strip()
            text = text.replace('\r', '')
            if text:
                text_parts.append(text)
    
    # 전체 텍스트 조합
    full_text = '\n'.join(text_parts)
    
    # 플레이스홀더를 실제 테이블로 대체
    for i, md in enumerate(table_markdowns):
        placeholder = f"__TABLE_{i}__"
        if placeholder in full_text:
            full_text = full_text.replace(placeholder, f"\n\n{md}\n\n")
    
    # 연속된 빈 줄 정리
    full_text = re.sub(r'\n{3,}', '\n\n', full_text)
    
    return full_text.strip()


def hwp_to_text(path: PathLike) -> str:
    """HWP 파일에서 평문 텍스트를 추출합니다.

    hwp5txt CLI를 사용합니다.
    주의: 표 내용은 <표> 플레이스홀더로 표시됩니다.
    표 내용을 포함하려면 hwp_to_rich_text()를 사용하세요.

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


def hwp_to_rich_text(path: PathLike) -> str:
    """HWP 파일에서 표 내용을 포함한 텍스트를 추출합니다.

    HTML로 변환 후 파싱하여 표를 마크다운 형식으로 포함합니다.
    hwp_to_text()보다 느리지만 표 내용이 필요할 때 사용합니다.

    Args:
        path: HWP 파일 경로

    Returns:
        표를 포함한 추출된 텍스트

    Raises:
        DependencyError: pyhwp가 설치되지 않은 경우
        ConversionError: 변환 실패 시
    """
    path = validate_file_exists(path)
    logger.info("리치 텍스트 추출 시작: %s", path)
    
    # HTML로 변환
    html_content = hwp_to_html(path)
    
    # HTML을 리치 텍스트로 변환
    rich_text = _html_to_rich_text(html_content)
    
    logger.info("리치 텍스트 추출 완료: %d 문자", len(rich_text))
    return rich_text


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

    output_target = output_dir / "hwp_output"

    logger.info("HTML 변환 시작: %s", path)
    run_command(
        [Command.HWP5HTML, str(path), "--output", str(output_target)],
        error_message=f"HWP → HTML 변환 실패: {path}",
    )

    # hwp5html은 디렉토리를 생성하거나 단일 파일을 생성할 수 있음
    if output_target.is_dir():
        # 디렉토리인 경우 index.xhtml 또는 index.html 찾기
        html_file = output_target / "index.xhtml"
        if not html_file.exists():
            html_file = output_target / "index.html"
        if not html_file.exists():
            raise ConversionError(f"HTML 파일이 생성되지 않았습니다: {output_target}")
    else:
        html_file = output_target

    html_content = html_file.read_text(encoding=DEFAULT_ENCODING)
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


def _find_chrome() -> str | None:
    """시스템에 설치된 Chrome/Chromium 경로를 찾습니다."""
    for chrome_path in CHROME_PATHS:
        if Path(chrome_path).exists():
            return chrome_path
    return None


def hwp_to_pdf(path: PathLike, output_path: PathLike) -> Path:
    """HWP를 PDF로 변환합니다.

    HTML을 거쳐 Chrome headless로 PDF를 생성합니다.

    Args:
        path: HWP 파일 경로
        output_path: 출력 PDF 파일 경로

    Returns:
        생성된 PDF 파일 경로

    Raises:
        DependencyError: Chrome이 설치되지 않은 경우
        ConversionError: 변환 실패 시
    """
    path = validate_file_exists(path)
    output_path = ensure_path(output_path)

    chrome_path = _find_chrome()
    if chrome_path is None:
        from .exceptions import DependencyError
        raise DependencyError("chrome", CHROME_INSTALL_HINT)

    logger.info("PDF 변환 시작 (Chrome headless): %s → %s", path, output_path)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        html_output_dir = temp_dir_path / "html"
        html_output_dir.mkdir()

        # HWP → HTML
        check_command_exists(Command.HWP5HTML, PYHWP_INSTALL_HINT)
        run_command(
            [Command.HWP5HTML, str(path), "--output", str(html_output_dir)],
            error_message=f"HWP → HTML 변환 실패: {path}",
        )

        # HTML 파일 찾기
        html_file = html_output_dir / "index.xhtml"
        if not html_file.exists():
            html_file = html_output_dir / "index.html"
        if not html_file.exists():
            raise ConversionError(f"HTML 파일이 생성되지 않았습니다: {html_output_dir}")

        # HTML → PDF (Chrome headless)
        run_command(
            [
                chrome_path,
                "--headless",
                "--disable-gpu",
                "--no-sandbox",
                "--print-to-pdf=" + str(output_path),
                "--print-to-pdf-no-header",
                f"file://{html_file}",
            ],
            error_message=f"HTML → PDF 변환 실패: {html_file}",
        )

        if not output_path.exists():
            raise ConversionError(f"PDF 파일이 생성되지 않았습니다: {output_path}")

    logger.info("PDF 변환 완료: %s", output_path)
    return output_path
