# HWP Parser - Python API Reference

## 핵심 함수

### 읽기 (Reader)

#### `read_hwp(file_path: PathLike) -> HWPDocument`
HWP 파일을 열고 문서 객체를 반환합니다.

```python
import hwpparser

doc = hwpparser.read_hwp("document.hwp")
print(doc.text)  # 평문 텍스트
print(doc.html)  # HTML
doc.to_odt("output.odt")
doc.to_pdf("output.pdf")
```

#### `hwp_to_text(file_path: PathLike) -> str`
빠른 텍스트 추출 (한 번만 사용할 때)

```python
text = hwpparser.hwp_to_text("document.hwp")
```

#### `hwp_to_html(file_path: PathLike) -> str`
HTML 변환

```python
html = hwpparser.hwp_to_html("document.hwp")
```

#### `hwp_to_odt(file_path: PathLike, output: PathLike) -> None`
ODT 파일로 저장

```python
hwpparser.hwp_to_odt("document.hwp", "output.odt")
```

#### `hwp_to_pdf(file_path: PathLike, output: PathLike) -> None`
PDF 파일로 저장 (Chrome headless 사용)

HWP → HTML → PDF 파이프라인으로 변환합니다.

```python
hwpparser.hwp_to_pdf("document.hwp", "output.pdf")
```

**필요 조건**:
- Chrome 또는 Chromium 브라우저

### 쓰기 (Writer)

#### `markdown_to_hwpx(markdown: str, output: PathLike) -> None`
Markdown을 HWPX로 변환

```python
hwpparser.markdown_to_hwpx("# 제목\n내용", "output.hwpx")
```

#### `html_to_hwpx(html: str, output: PathLike) -> None`
HTML을 HWPX로 변환

```python
hwpparser.html_to_hwpx("<h1>제목</h1>", "output.hwpx")
```

### 변환 (Converter)

#### `convert(input_path: PathLike, output_path: PathLike) -> None`
통합 변환 인터페이스 (확장자 자동 인식)

```python
hwpparser.convert("document.hwp", "output.txt")
hwpparser.convert("document.hwp", "output.pdf")
hwpparser.convert("README.md", "README.hwpx")
```

#### `get_supported_conversions() -> dict`
지원 변환 목록

```python
conversions = hwpparser.get_supported_conversions()
# {'hwp': ['text', 'html', 'odt', 'pdf'], ...}
```

## 워크플로우 (Workflows)

### 청킹 (RAG용)

#### `hwp_to_chunks(file_path: PathLike, chunk_size: int = 1000) -> List[TextChunk]`
문서를 청크로 분할

```python
chunks = hwpparser.hwp_to_chunks("document.hwp", chunk_size=1000)
for chunk in chunks:
    print(f"Text: {chunk.text}")
    print(f"Metadata: {chunk.metadata}")
```

**TextChunk 구조**:
```python
@dataclass
class TextChunk:
    text: str
    metadata: dict  # {'file', 'page', 'offset', 'length'}
```

#### `chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[TextChunk]`
텍스트를 청크로 분할

```python
chunks = hwpparser.chunk_text(text, chunk_size=1000, overlap=200)
```

### LangChain 연동

#### `HWPLoader(file_path: PathLike)`
단일 파일 로더

```python
from hwpparser import HWPLoader

loader = HWPLoader("document.hwp")
docs = loader.load()  # List[Document]
```

#### `DirectoryHWPLoader(path: PathLike, recursive: bool = False)`
디렉토리 로더

```python
from hwpparser import DirectoryHWPLoader

loader = DirectoryHWPLoader("./documents", recursive=True)
docs = loader.load()
```

**Document 구조**:
```python
@dataclass
class Document:
    page_content: str
    metadata: dict  # {'source', 'file_name', 'char_count', ...}
```

### 배치 처리

#### `batch_convert(input_dir: PathLike, output_dir: PathLike, format: str) -> BatchResult`
폴더 내 모든 HWP 파일 일괄 변환

```python
result = hwpparser.batch_convert("./hwp_files", "./text_files", "txt")
print(f"성공: {result.success}/{result.total}")
print(f"실패: {result.failed}")
for error in result.errors:
    print(f"  {error['file']}: {error['error']}")
```

#### `batch_extract_text(directory: PathLike, recursive: bool = False) -> str`
모든 HWP 파일의 텍스트 합치기

```python
all_text = hwpparser.batch_extract_text("./documents", recursive=True)
```

### 검색 인덱싱

#### `export_to_jsonl(input_dir: PathLike, output_file: PathLike, chunk_size: int = None) -> None`
JSONL 인덱스 생성 (Elasticsearch/Algolia용)

```python
hwpparser.export_to_jsonl(
    "./documents",
    "./search_index.jsonl",
    chunk_size=1000  # 청킹 포함
)
```

**JSONL 포맷**:
```json
{"id": "doc1_chunk1", "text": "...", "metadata": {...}}
{"id": "doc1_chunk2", "text": "...", "metadata": {...}}
```

### 메타데이터

#### `extract_metadata(file_path: PathLike) -> dict`
문서 메타데이터 추출

```python
meta = hwpparser.extract_metadata("document.hwp")
print(meta)
# {
#   'file_name': 'document.hwp',
#   'file_size': 12345,
#   'char_count': 1000,
#   'word_count': 200,
#   'page_count': 5,
#   ...
# }
```

## 예외 클래스

```python
from hwpparser.exceptions import (
    HWPParserError,          # 기본 예외
    HWPFileNotFoundError,    # 파일 없음
    ConversionError,         # 변환 실패
    DependencyError,         # 의존성 누락
    UnsupportedFormatError,  # 지원하지 않는 포맷
)
```

## HWPDocument 클래스

```python
class HWPDocument:
    @property
    def text(self) -> str:
        """평문 텍스트"""

    @property
    def html(self) -> str:
        """HTML 변환"""

    def to_odt(self, output: PathLike) -> None:
        """ODT 파일로 저장"""

    def to_pdf(self, output: PathLike) -> None:
        """PDF 파일로 저장"""

    def __enter__(self) -> 'HWPDocument':
        """Context manager 지원"""

    def __exit__(self, *args) -> None:
        """리소스 정리"""
```

## 사용 예시

### 컨텍스트 매니저 패턴
```python
with hwpparser.read_hwp("document.hwp") as doc:
    print(doc.text)
    doc.to_pdf("output.pdf")
# 자동으로 리소스 정리
```

### 에러 핸들링
```python
try:
    text = hwpparser.hwp_to_text("document.hwp")
except hwpparser.HWPFileNotFoundError:
    print("파일을 찾을 수 없습니다")
except hwpparser.DependencyError as e:
    print(f"의존성 누락: {e}")
    # pip install pyhwp
except hwpparser.ConversionError as e:
    print(f"변환 실패: {e}")
```

### 타입 힌팅
```python
from pathlib import Path
from typing import List
from hwpparser import TextChunk

def process_document(file_path: str | Path) -> List[TextChunk]:
    return hwpparser.hwp_to_chunks(file_path, chunk_size=1000)
```
