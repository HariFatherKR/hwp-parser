"""
HWP Parser 워크플로우

일반적인 HWP 문서 처리 워크플로우를 제공합니다.
- RAG 파이프라인
- 배치 변환
- LangChain 연동
- 문서 요약/번역
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Iterator

from ._logging import get_logger
from ._types import PathLike
from .constants import DEFAULT_ENCODING
from .reader import hwp_to_text
from .utils import ensure_path

if TYPE_CHECKING:
    pass

logger = get_logger("workflows")


# =============================================================================
# 1. 텍스트 청킹 (RAG용)
# =============================================================================


@dataclass
class TextChunk:
    """텍스트 청크를 나타내는 데이터 클래스."""

    text: str
    index: int
    metadata: dict[str, Any] = field(default_factory=dict)

    def __len__(self) -> int:
        return len(self.text)


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    separator: str = "\n\n",
) -> list[TextChunk]:
    """텍스트를 청크로 분할합니다 (RAG용).

    Args:
        text: 분할할 텍스트
        chunk_size: 청크 크기 (문자 수)
        chunk_overlap: 청크 간 오버랩 (문자 수)
        separator: 우선 분할 기준 문자

    Returns:
        TextChunk 리스트

    Example:
        >>> chunks = chunk_text(hwp_to_text("doc.hwp"), chunk_size=500)
        >>> for chunk in chunks:
        ...     print(f"Chunk {chunk.index}: {len(chunk)} chars")
    """
    if not text:
        return []

    chunks: list[TextChunk] = []

    # 구분자로 먼저 분할
    paragraphs = text.split(separator)

    current_chunk = ""
    current_start = 0

    for para in paragraphs:
        # 현재 청크 + 새 문단이 크기 초과하면 저장
        if len(current_chunk) + len(para) > chunk_size and current_chunk:
            chunks.append(TextChunk(
                text=current_chunk.strip(),
                index=len(chunks),
                metadata={"start": current_start, "end": current_start + len(current_chunk)},
            ))
            # 오버랩 적용
            overlap_text = current_chunk[-chunk_overlap:] if chunk_overlap > 0 else ""
            current_chunk = overlap_text + separator + para
            current_start = current_start + len(current_chunk) - len(overlap_text)
        else:
            current_chunk += separator + para if current_chunk else para

    # 마지막 청크
    if current_chunk.strip():
        chunks.append(TextChunk(
            text=current_chunk.strip(),
            index=len(chunks),
            metadata={"start": current_start, "end": current_start + len(current_chunk)},
        ))

    logger.info("텍스트 청킹 완료: %d개 청크 생성", len(chunks))
    return chunks


def hwp_to_chunks(
    path: PathLike,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> list[TextChunk]:
    """HWP 파일에서 텍스트를 추출하고 청킹합니다.

    Args:
        path: HWP 파일 경로
        chunk_size: 청크 크기
        chunk_overlap: 청크 오버랩

    Returns:
        TextChunk 리스트 (메타데이터에 소스 경로 포함)

    Example:
        >>> chunks = hwp_to_chunks("document.hwp")
        >>> # 벡터 DB에 저장
        >>> for chunk in chunks:
        ...     embedding = embed(chunk.text)
        ...     db.insert(embedding, chunk.metadata)
    """
    path = ensure_path(path)
    text = hwp_to_text(path)

    chunks = chunk_text(text, chunk_size, chunk_overlap)

    # 소스 메타데이터 추가
    for chunk in chunks:
        chunk.metadata["source"] = str(path)
        chunk.metadata["source_type"] = "hwp"

    return chunks


# =============================================================================
# 2. 배치 변환
# =============================================================================


@dataclass
class BatchResult:
    """배치 처리 결과."""

    total: int = 0
    success: int = 0
    failed: int = 0
    errors: dict[str, str] = field(default_factory=dict)

    @property
    def success_rate(self) -> float:
        """성공률 (0.0 ~ 1.0)."""
        return self.success / self.total if self.total > 0 else 0.0


def batch_convert(
    input_dir: PathLike,
    output_dir: PathLike,
    output_format: str = "txt",
    *,
    pattern: str = "*.hwp",
    recursive: bool = False,
    on_progress: Callable[[Path, int, int], None] | None = None,
) -> BatchResult:
    """폴더 내 HWP 파일을 일괄 변환합니다.

    Args:
        input_dir: 입력 폴더
        output_dir: 출력 폴더
        output_format: 출력 포맷 (txt, html, odt, pdf)
        pattern: 파일 패턴 (기본값: *.hwp)
        recursive: 하위 폴더 포함 여부
        on_progress: 진행 콜백 (현재 파일, 현재 인덱스, 전체 개수)

    Returns:
        BatchResult (성공/실패 통계)

    Example:
        >>> result = batch_convert("./hwp_files", "./text_files", "txt")
        >>> print(f"변환 완료: {result.success}/{result.total}")
    """
    from .converter import convert

    input_dir = ensure_path(input_dir)
    output_dir = ensure_path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # HWP 파일 찾기
    hwp_files = list(input_dir.rglob(pattern)) if recursive else list(input_dir.glob(pattern))

    result = BatchResult(total=len(hwp_files))
    logger.info("배치 변환 시작: %d개 파일", result.total)

    for i, hwp_file in enumerate(hwp_files):
        try:
            # 상대 경로 유지
            relative = hwp_file.relative_to(input_dir)
            output_file = output_dir / relative.with_suffix(f".{output_format}")
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # 변환
            convert(hwp_file, output_file)
            result.success += 1

            if on_progress:
                on_progress(hwp_file, i + 1, result.total)

        except Exception as e:
            result.failed += 1
            result.errors[str(hwp_file)] = str(e)
            logger.warning("변환 실패: %s - %s", hwp_file, e)

    logger.info("배치 변환 완료: %d 성공, %d 실패", result.success, result.failed)
    return result


def batch_extract_text(
    input_dir: PathLike,
    output_file: PathLike | None = None,
    *,
    pattern: str = "*.hwp",
    recursive: bool = False,
    separator: str = "\n\n---\n\n",
) -> str:
    """폴더 내 모든 HWP 파일에서 텍스트를 추출하여 하나로 합칩니다.

    Args:
        input_dir: 입력 폴더
        output_file: 출력 파일 (None이면 문자열로만 반환)
        pattern: 파일 패턴
        recursive: 하위 폴더 포함
        separator: 파일 간 구분자

    Returns:
        합쳐진 텍스트

    Example:
        >>> # LLM에 전체 내용 입력
        >>> all_text = batch_extract_text("./documents")
        >>> summary = llm.summarize(all_text[:100000])
    """
    input_dir = ensure_path(input_dir)

    hwp_files = sorted(input_dir.rglob(pattern)) if recursive else sorted(input_dir.glob(pattern))

    texts: list[str] = []

    for hwp_file in hwp_files:
        try:
            text = hwp_to_text(hwp_file)
            header = f"# {hwp_file.name}\n\n"
            texts.append(header + text)
        except Exception as e:
            logger.warning("텍스트 추출 실패: %s - %s", hwp_file, e)

    combined = separator.join(texts)

    if output_file:
        output_path = ensure_path(output_file)
        output_path.write_text(combined, encoding=DEFAULT_ENCODING)
        logger.info("통합 텍스트 저장: %s (%d자)", output_path, len(combined))

    return combined


# =============================================================================
# 3. LangChain 연동
# =============================================================================


@dataclass
class Document:
    """LangChain 호환 Document 클래스.

    LangChain의 Document와 동일한 인터페이스를 제공합니다.
    """

    page_content: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        return f"Document(content_length={len(self.page_content)}, metadata={self.metadata})"


class HWPLoader:
    """HWP 파일용 LangChain 스타일 Document Loader.

    LangChain과 함께 사용하거나 독립적으로 사용할 수 있습니다.

    Example:
        >>> # 단일 파일
        >>> loader = HWPLoader("document.hwp")
        >>> docs = loader.load()

        >>> # LangChain과 함께
        >>> from langchain.text_splitter import RecursiveCharacterTextSplitter
        >>> splitter = RecursiveCharacterTextSplitter(chunk_size=1000)
        >>> chunks = splitter.split_documents(docs)
    """

    def __init__(
        self,
        file_path: PathLike | list[PathLike],
        *,
        encoding: str = DEFAULT_ENCODING,
    ) -> None:
        """HWPLoader를 초기화합니다.

        Args:
            file_path: HWP 파일 경로 또는 경로 리스트
            encoding: 텍스트 인코딩
        """
        if isinstance(file_path, list):
            self.file_paths = [ensure_path(p) for p in file_path]
        else:
            self.file_paths = [ensure_path(file_path)]
        self.encoding = encoding

    def load(self) -> list[Document]:
        """모든 HWP 파일을 Document로 로드합니다.

        Returns:
            Document 리스트
        """
        documents: list[Document] = []

        for file_path in self.file_paths:
            try:
                text = hwp_to_text(file_path)
                doc = Document(
                    page_content=text,
                    metadata={
                        "source": str(file_path),
                        "file_name": file_path.name,
                        "file_type": "hwp",
                    },
                )
                documents.append(doc)
            except Exception as e:
                logger.warning("문서 로드 실패: %s - %s", file_path, e)

        logger.info("HWP 로드 완료: %d개 문서", len(documents))
        return documents

    def lazy_load(self) -> Iterator[Document]:
        """Document를 하나씩 로드합니다 (메모리 효율적).

        Yields:
            Document 객체
        """
        for file_path in self.file_paths:
            try:
                text = hwp_to_text(file_path)
                yield Document(
                    page_content=text,
                    metadata={
                        "source": str(file_path),
                        "file_name": file_path.name,
                        "file_type": "hwp",
                    },
                )
            except Exception as e:
                logger.warning("문서 로드 실패: %s - %s", file_path, e)


class DirectoryHWPLoader:
    """디렉토리 내 모든 HWP 파일을 로드하는 Loader.

    Example:
        >>> loader = DirectoryHWPLoader("./documents", recursive=True)
        >>> docs = loader.load()
        >>> print(f"로드됨: {len(docs)}개 문서")
    """

    def __init__(
        self,
        directory: PathLike,
        *,
        pattern: str = "*.hwp",
        recursive: bool = False,
    ) -> None:
        """DirectoryHWPLoader를 초기화합니다.

        Args:
            directory: 디렉토리 경로
            pattern: 파일 패턴
            recursive: 하위 폴더 포함 여부
        """
        self.directory = ensure_path(directory)
        self.pattern = pattern
        self.recursive = recursive

    def load(self) -> list[Document]:
        """모든 HWP 파일을 Document로 로드합니다."""
        if self.recursive:
            hwp_files = list(self.directory.rglob(self.pattern))
        else:
            hwp_files = list(self.directory.glob(self.pattern))

        loader = HWPLoader(hwp_files)
        return loader.load()


# =============================================================================
# 4. 문서 메타데이터 추출
# =============================================================================


def extract_metadata(path: PathLike) -> dict[str, Any]:
    """HWP 파일에서 메타데이터를 추출합니다.

    Args:
        path: HWP 파일 경로

    Returns:
        메타데이터 딕셔너리

    Example:
        >>> meta = extract_metadata("document.hwp")
        >>> print(meta["file_size"], meta["char_count"])
    """
    path = ensure_path(path)
    text = hwp_to_text(path)

    # 기본 메타데이터
    metadata: dict[str, Any] = {
        "source": str(path),
        "file_name": path.name,
        "file_size": path.stat().st_size,
        "char_count": len(text),
        "word_count": len(text.split()),
        "line_count": text.count("\n") + 1,
    }

    # 수정 시간
    stat = path.stat()
    metadata["modified_time"] = stat.st_mtime

    return metadata


# =============================================================================
# 5. JSON/JSONL 내보내기 (검색 인덱싱용)
# =============================================================================


def export_to_jsonl(
    input_dir: PathLike,
    output_file: PathLike,
    *,
    pattern: str = "*.hwp",
    recursive: bool = False,
    include_text: bool = True,
    chunk_size: int | None = None,
) -> int:
    """HWP 파일들을 JSONL 형식으로 내보냅니다 (검색 인덱싱용).

    Args:
        input_dir: 입력 디렉토리
        output_file: 출력 JSONL 파일
        pattern: 파일 패턴
        recursive: 하위 폴더 포함
        include_text: 전체 텍스트 포함 여부
        chunk_size: 청킹 시 청크 크기 (None이면 청킹 안 함)

    Returns:
        내보낸 레코드 수

    Example:
        >>> # Elasticsearch에 인덱싱할 JSONL 생성
        >>> count = export_to_jsonl("./docs", "./index.jsonl", chunk_size=1000)
        >>> print(f"{count}개 레코드 생성")
    """
    input_dir = ensure_path(input_dir)
    output_file = ensure_path(output_file)

    hwp_files = list(input_dir.rglob(pattern)) if recursive else list(input_dir.glob(pattern))

    record_count = 0

    with open(output_file, "w", encoding=DEFAULT_ENCODING) as f:
        for hwp_file in hwp_files:
            try:
                text = hwp_to_text(hwp_file)
                metadata = extract_metadata(hwp_file)

                if chunk_size:
                    # 청킹하여 각각 레코드로
                    chunks = chunk_text(text, chunk_size=chunk_size)
                    for chunk in chunks:
                        record = {
                            **metadata,
                            "chunk_index": chunk.index,
                            "text": chunk.text,
                        }
                        f.write(json.dumps(record, ensure_ascii=False) + "\n")
                        record_count += 1
                else:
                    # 전체 문서를 하나의 레코드로
                    record = {**metadata}
                    if include_text:
                        record["text"] = text
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")
                    record_count += 1

            except Exception as e:
                logger.warning("JSONL 내보내기 실패: %s - %s", hwp_file, e)

    logger.info("JSONL 내보내기 완료: %s (%d개 레코드)", output_file, record_count)
    return record_count
