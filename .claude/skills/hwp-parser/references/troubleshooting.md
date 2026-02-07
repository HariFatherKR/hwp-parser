# HWP Parser - Troubleshooting Guide

## 설치 문제

### pyhwp 설치 실패

**증상**:
```
ERROR: Could not find a version that satisfies the requirement pyhwp
```

**해결**:
```bash
# Python 버전 확인 (3.8 이상 필요)
python --version

# pip 업그레이드
pip install --upgrade pip

# 재설치
pip install pyhwp
```

### 의존성 충돌

**증상**:
```
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed.
```

**해결**:
```bash
# 가상환경 새로 생성
python -m venv venv_new
source venv_new/bin/activate
pip install hwpparser[all]
```

## 변환 문제

### PDF 변환 실패 - LibreOffice 없음

**증상**:
```
DependencyError: LibreOffice not found
```

**해결**:
```bash
# macOS
brew install --cask libreoffice

# Ubuntu/Debian
sudo apt-get install libreoffice

# 설치 확인
which soffice
```

### PDF 변환 - 권한 오류

**증상**:
```
PermissionError: [Errno 13] Permission denied
```

**해결**:
```bash
# 임시 디렉토리 권한 확인
ls -la /tmp

# 환경변수 설정
export TMPDIR=/path/to/writable/tmp
hwpparser convert document.hwp output.pdf
```

### HWP 파일 읽기 실패

**증상**:
```
ConversionError: Failed to read HWP file
```

**원인 & 해결**:

1. **파일 손상 확인**
   ```bash
   # 파일 타입 확인
   file document.hwp
   # 출력: document.hwp: Composite Document File V2 Document
   ```

2. **HWP 버전 확인**
   - HWP 5.0 이상만 지원
   - HWPX (XML 포맷)는 별도 처리 필요

3. **암호화된 파일**
   ```python
   # 현재 암호화 파일은 지원하지 않음
   # 한글에서 암호 해제 후 사용
   ```

### 인코딩 오류

**증상**:
```
UnicodeDecodeError: 'utf-8' codec can't decode byte
```

**해결**:
```python
# 인코딩 지정
text = hwpparser.hwp_to_text("document.hwp")

# CLI
hwpparser text document.hwp --encoding cp949
```

## 성능 문제

### 대용량 파일 처리 느림

**증상**: 100MB 이상 파일 처리 시간 과다

**해결**:
```python
# 청킹으로 스트리밍 처리
chunks = hwpparser.hwp_to_chunks("large.hwp", chunk_size=500)

# 또는 텍스트만 추출 (빠름)
text = hwpparser.hwp_to_text("large.hwp")
```

### 메모리 부족

**증상**:
```
MemoryError: Unable to allocate array
```

**해결**:
```bash
# 메모리 제한 늘리기 (Linux)
ulimit -v unlimited

# 청킹 크기 줄이기
hwpparser batch ./files/ -f text --chunk-size 500
```

### 배치 변환 속도 개선

```python
# 병렬 처리
result = hwpparser.batch_convert(
    "./files",
    "./output",
    "txt",
    workers=8  # CPU 코어 수에 맞게 조정
)
```

## 플랫폼별 문제

### macOS - LibreOffice 경로 인식 실패

**증상**:
```
FileNotFoundError: LibreOffice not found
```

**해결**:
```bash
# LibreOffice 경로 확인
which soffice
ls -la /Applications/LibreOffice.app/Contents/MacOS/soffice

# 심볼릭 링크 생성
sudo ln -s /Applications/LibreOffice.app/Contents/MacOS/soffice /usr/local/bin/soffice
```

### Ubuntu - Pandoc 버전 문제

**증상**:
```
DependencyError: Pandoc version 2.0+ required
```

**해결**:
```bash
# 최신 버전 설치
wget https://github.com/jgm/pandoc/releases/download/3.1.11/pandoc-3.1.11-1-amd64.deb
sudo dpkg -i pandoc-3.1.11-1-amd64.deb

# 확인
pandoc --version
```

### Windows - 경로 문제

**증상**:
```
FileNotFoundError: [WinError 3] The system cannot find the path specified
```

**해결**:
```python
# 경로 슬래시 확인
import os
path = os.path.normpath("C:/Users/Documents/file.hwp")
text = hwpparser.hwp_to_text(path)

# 또는 원시 문자열
text = hwpparser.hwp_to_text(r"C:\Users\Documents\file.hwp")
```

## API 사용 문제

### Import Error

**증상**:
```python
ImportError: cannot import name 'hwp_to_text' from 'hwpparser'
```

**해결**:
```python
# 올바른 임포트
import hwpparser
text = hwpparser.hwp_to_text("file.hwp")

# 또는
from hwpparser import hwp_to_text
text = hwp_to_text("file.hwp")
```

### 컨텍스트 매니저 오류

**증상**:
```python
AttributeError: __enter__
```

**해결**:
```python
# 올바른 사용
with hwpparser.read_hwp("file.hwp") as doc:
    print(doc.text)

# 또는 수동 관리
doc = hwpparser.read_hwp("file.hwp")
try:
    print(doc.text)
finally:
    # 리소스 정리는 자동
    pass
```

## 타입 힌팅 문제

### mypy 오류

**증상**:
```
error: Skipping analyzing "hwpparser": module is installed, but missing library stubs
```

**해결**:
```bash
# py.typed 파일 확인
pip show -f hwpparser | grep py.typed

# 타입 체크 무시
# mypy.ini
[mypy-hwpparser]
ignore_missing_imports = True
```

## 디버깅

### 로깅 활성화

```python
import logging
import hwpparser

# 로깅 설정
hwpparser.setup_logging(level=logging.DEBUG)

# 변환 시도
try:
    text = hwpparser.hwp_to_text("document.hwp")
except Exception as e:
    logging.exception("변환 실패")
```

### CLI 디버그 모드

```bash
# 상세 로그
hwpparser convert document.hwp output.pdf --verbose

# 디버그 모드
hwpparser convert document.hwp output.pdf --debug
```

### 임시 파일 확인

```python
import tempfile
import hwpparser

# 임시 디렉토리 확인
temp_dir = tempfile.gettempdir()
print(f"임시 디렉토리: {temp_dir}")

# 변환 후 임시 파일 유지 (디버그용)
import os
os.environ['HWPPARSER_KEEP_TEMP'] = '1'
hwpparser.hwp_to_pdf("document.hwp", "output.pdf")
```

## 특정 에러 메시지

### "Command 'hwp5txt' not found"

**원인**: pyhwp 미설치

**해결**:
```bash
pip install pyhwp
```

### "No module named 'pypandoc'"

**원인**: HWPX 생성 의존성 누락

**해결**:
```bash
pip install hwpparser[hwpx]
# 또는
pip install pypandoc pypandoc-hwpx
```

### "pandoc: command not found"

**원인**: Pandoc 시스템 패키지 미설치

**해결**:
```bash
# macOS
brew install pandoc

# Ubuntu
sudo apt-get install pandoc

# Windows (관리자 권한)
choco install pandoc
```

### "Error calling soffice"

**원인**: LibreOffice 실행 권한 또는 경로 문제

**해결**:
```bash
# 실행 권한 확인
chmod +x /usr/bin/soffice

# 수동 실행 테스트
soffice --headless --convert-to pdf test.odt

# macOS 보안 설정
# 시스템 환경설정 > 보안 및 개인 정보 보호 > 일반
# "확인 없이 열기" 클릭
```

## 자주 묻는 질문 (FAQ)

### Q: HWPX 파일도 읽을 수 있나요?
A: 현재 읽기는 HWP (바이너리) 전용입니다. HWPX는 생성(쓰기)만 지원합니다.

### Q: 암호화된 HWP 파일은?
A: 지원하지 않습니다. 한글에서 암호 해제 후 사용하세요.

### Q: HWP 3.0 이하 버전은?
A: HWP 5.0 이상만 지원합니다.

### Q: 이미지나 표는 변환되나요?
A: 텍스트만 추출됩니다. HTML/ODT/PDF 변환 시 레이아웃은 일부 유지됩니다.

### Q: 상용 사용 가능한가요?
A: hwpparser는 MIT 라이선스입니다. 단, pyhwp는 AGPL v3이므로 주의하세요.

## 버그 리포트

문제가 해결되지 않으면:

1. **이슈 확인**: https://github.com/harifatherkr/hwpparser/issues
2. **버그 리포트 작성**:
   - Python 버전
   - OS 정보
   - hwpparser 버전: `pip show hwpparser`
   - 에러 메시지 전문
   - 재현 가능한 최소 코드
3. **샘플 파일**: 가능하면 문제 발생 HWP 파일 첨부

## 추가 도움

- 공식 문서: https://hwpparser.readthedocs.io
- GitHub: https://github.com/harifatherkr/hwpparser
- pyhwp 프로젝트: https://github.com/mete0r/pyhwp
