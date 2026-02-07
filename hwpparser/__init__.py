"""
HWP Parser - LLM 활용을 위한 한글 문서 파서 및 변환기

지원 기능:
- HWP (한글 5.0+) → Text, HTML, ODT, PDF
- HWPX (한글 XML) → 직접 XML 접근
- Markdown/HTML/DOCX → HWPX

Examples:
    >>> import hwpparser

    >>> # HWP 읽기
    >>> with hwpparser.read_hwp("document.hwp") as doc:
    ...     print(doc.text)

    >>> # 빠른 텍스트 추출
    >>> text = hwpparser.hwp_to_text("document.hwp")

    >>> # 포맷 변환
    >>> hwpparser.convert("document.hwp", "output.pdf")
    >>> hwpparser.convert("document.md", "output.hwpx")

    >>> # HWPX 생성
    >>> hwpparser.markdown_to_hwpx("# 제목\\n내용", "output.hwpx")
"""

from __future__ import annotations

__version__ = "0.1.0"
__author__ = "HariFatherKR"
__license__ = "MIT"

# 예외
# 로깅 설정
from ._logging import setup_logging

# Converter
from .converter import (
    convert,
    get_supported_conversions,
    get_supported_input_formats,
    get_supported_output_formats,
)
from .exceptions import (
    ConversionError,
    DependencyError,
    HWPFileNotFoundError,
    HWPParserError,
    UnsupportedFormatError,
)

# Reader
from .reader import (
    HWPDocument,
    HWPReader,
    hwp_to_html,
    hwp_to_odt,
    hwp_to_pdf,
    hwp_to_text,
    read_hwp,
)

# Workflows
from .workflows import (
    # 청킹 (RAG용)
    BatchResult,
    DirectoryHWPLoader,
    Document,
    HWPLoader,
    TextChunk,
    batch_convert,
    batch_extract_text,
    chunk_text,
    export_to_jsonl,
    extract_metadata,
    hwp_to_chunks,
)

# Writer
from .writer import (
    HWPXWriter,
    html_to_hwpx,
    markdown_to_hwpx,
    write_hwpx,
)

# 하위 호환성
FileNotFoundError = HWPFileNotFoundError  # noqa: A001

__all__ = [
    # 버전
    "__version__",
    "__author__",
    "__license__",
    # 예외
    "HWPParserError",
    "HWPFileNotFoundError",
    "ConversionError",
    "DependencyError",
    "UnsupportedFormatError",
    # Reader
    "HWPDocument",
    "HWPReader",
    "read_hwp",
    "hwp_to_text",
    "hwp_to_html",
    "hwp_to_odt",
    "hwp_to_pdf",
    # Writer
    "HWPXWriter",
    "write_hwpx",
    "markdown_to_hwpx",
    "html_to_hwpx",
    # Converter
    "convert",
    "get_supported_conversions",
    "get_supported_input_formats",
    "get_supported_output_formats",
    # Workflows - 청킹 (RAG)
    "TextChunk",
    "chunk_text",
    "hwp_to_chunks",
    # Workflows - 배치 처리
    "BatchResult",
    "batch_convert",
    "batch_extract_text",
    # Workflows - LangChain 연동
    "Document",
    "HWPLoader",
    "DirectoryHWPLoader",
    # Workflows - 메타데이터/인덱싱
    "extract_metadata",
    "export_to_jsonl",
    # 로깅
    "setup_logging",
]
