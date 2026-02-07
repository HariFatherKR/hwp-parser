# HWP Parser - Claude Project Guide

이 프로젝트는 한글(HWP/HWPX) 파일을 다양한 포맷으로 변환하는 Python 패키지입니다.

## 프로젝트 구조

```
hwpparser/
├── hwpparser/           # 메인 패키지
│   ├── __init__.py      # Public API
│   ├── cli.py           # Click CLI
│   ├── converter.py     # 변환 로직
│   ├── reader.py        # HWP 읽기
│   └── writer.py        # 출력 쓰기
├── tests/               # pytest 테스트
├── examples/            # 샘플 HWP 파일
└── skills/              # AI Agent 스킬 정의
```

## 핵심 명령어

```bash
# 가상환경 활성화
source venv/bin/activate

# 테스트 실행
pytest tests/ -v

# 린팅
ruff check hwpparser/

# 패키지 설치 (개발 모드)
pip install -e .
```

## CLI 사용법

```bash
# 단일 파일 변환
hwpparser convert input.hwp -f text -o output.txt
hwpparser convert input.hwp -f html -o output.html
hwpparser convert input.hwp -f odt -o output.odt
hwpparser convert input.hwp -f pdf -o output.pdf

# 일괄 변환
hwpparser batch ./documents/ -f text -o ./output/
```

## 코드 스타일

- Python 3.11+ features 사용 (StrEnum, TypeAlias 등)
- Type hints 필수
- Docstrings: Google style
- 테스트: pytest + fixtures

## 주요 클래스

### `HWPConverter`
```python
from hwpparser import HWPConverter, OutputFormat

converter = HWPConverter()
text = converter.convert("document.hwp", OutputFormat.TEXT)
```

### `HWPReader`
```python
from hwpparser.reader import HWPReader

with HWPReader("document.hwp") as reader:
    content = reader.read()
```

## 예외 처리

```python
from hwpparser.exceptions import HWPFileNotFoundError, HWPFormatError

try:
    result = converter.convert("missing.hwp")
except HWPFileNotFoundError:
    print("파일을 찾을 수 없습니다")
except HWPFormatError:
    print("지원하지 않는 파일 형식입니다")
```

## 테스트

```bash
# 전체 테스트
pytest tests/ -v

# 특정 테스트
pytest tests/test_converter.py -v

# 커버리지
pytest tests/ --cov=hwpparser
```

## 의존성 추가 시

`pyproject.toml`의 `dependencies` 섹션에 추가 후:
```bash
pip install -e .
```
