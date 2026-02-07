# HWP Parser 📄

LLM 활용을 위한 한글(HWP/HWPX) 문서 파서 및 변환기

## 기능

- **HWP 읽기** → Text, HTML, ODT, PDF
- **HWPX 생성** ← Markdown, HTML, DOCX  
- **CLI 도구** - 빠른 변환
- **Python API** - 프로그래밍 활용

## 설치

```bash
pip install hwpparser

# HWPX 생성 기능 포함
pip install hwpparser[hwpx]
```

소스에서 설치:

```bash
git clone https://github.com/harifatherkr/hwpparser
cd hwpparser
pip install -e ".[all]"
```

### 시스템 의존성

```bash
# macOS
brew install pandoc
brew install --cask libreoffice  # PDF 변환용

# Ubuntu/Debian
sudo apt install pandoc libreoffice
```

## 빠른 시작

### CLI

```bash
# HWP에서 텍스트 추출
hwpparser text document.hwp

# 포맷 변환
hwpparser convert document.hwp output.txt
hwpparser convert document.hwp output.pdf
hwpparser convert document.md output.hwpx

# 지원 포맷 확인
hwpparser formats
```

### Python API

```python
import hwpparser

# HWP 읽기
doc = hwpparser.read_hwp("document.hwp")
print(doc.text)  # 평문 텍스트
print(doc.html)  # HTML

# ODT/PDF로 저장
doc.to_odt("output.odt")
doc.to_pdf("output.pdf")

# 빠른 텍스트 추출
text = hwpparser.hwp_to_text("document.hwp")

# 마크다운 → HWPX
hwpparser.markdown_to_hwpx("# 제목\n내용", "output.hwpx")

# 통합 변환 인터페이스
hwpparser.convert("input.hwp", "output.pdf")
hwpparser.convert("input.md", "output.hwpx")
```

## 지원 변환

| 입력 | 출력 |
|------|------|
| HWP | Text, HTML, ODT, PDF |
| Markdown | HWPX |
| HTML | HWPX |
| DOCX | HWPX |

## 포맷 설명

- **HWP** (한글 5.0+): 바이너리 OLE2 포맷, 읽기 전용
- **HWPX**: XML 기반 포맷 (DOCX와 유사), 읽기/쓰기 지원

## 워크플로우

### 1. RAG 파이프라인 (청킹)

```python
import hwpparser

# HWP → 청크 (벡터 DB용)
chunks = hwpparser.hwp_to_chunks("document.hwp", chunk_size=1000)

for chunk in chunks:
    embedding = your_embed_function(chunk.text)
    vector_db.insert(embedding, chunk.metadata)
```

### 2. LangChain 연동

```python
from hwpparser import HWPLoader, DirectoryHWPLoader

# 단일 파일
loader = HWPLoader("document.hwp")
docs = loader.load()

# 폴더 전체
loader = DirectoryHWPLoader("./documents", recursive=True)
docs = loader.load()

# LangChain과 함께
from langchain.text_splitter import RecursiveCharacterTextSplitter
splitter = RecursiveCharacterTextSplitter(chunk_size=1000)
chunks = splitter.split_documents(docs)
```

### 3. 배치 변환

```python
# 폴더 내 모든 HWP → TXT
result = hwpparser.batch_convert("./hwp_files", "./text_files", "txt")
print(f"변환: {result.success}/{result.total}")

# 모든 HWP 텍스트 합치기
all_text = hwpparser.batch_extract_text("./documents")
```

### 4. 검색 인덱싱 (JSONL)

```python
# Elasticsearch/Algolia용 JSONL 생성
hwpparser.export_to_jsonl(
    "./documents", 
    "./index.jsonl",
    chunk_size=1000  # 청킹 포함
)
```

### 5. 메타데이터 추출

```python
meta = hwpparser.extract_metadata("document.hwp")
print(meta["char_count"], meta["word_count"])
```

## 개발

```bash
# 개발 환경 설정
pip install -e ".[dev]"

# 테스트
pytest

# 린트
ruff check hwpparser

# 타입 체크
mypy hwpparser
```

## 의존성 및 저작권

이 프로젝트는 다음 오픈소스 라이브러리를 사용합니다:

- **pyhwp** (Copyright © 2010-2023 mete0r)
  - 라이선스: GNU Affero General Public License v3 (AGPL v3)
  - 저장소: https://github.com/mete0r/pyhwp
  - 용도: HWP 파일 파싱 및 변환

**중요**: 이 프로젝트는 AGPL v3 라이브러리(pyhwp)에 의존합니다. AGPL v3는 카피레프트 라이선스로, 이 프로젝트를 서비스로 제공하거나 배포할 경우 소스 코드 공개 의무가 발생할 수 있습니다.

## 라이선스

MIT (단, AGPL 의존성에 주의)
