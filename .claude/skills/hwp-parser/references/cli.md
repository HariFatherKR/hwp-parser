# HWP Parser - CLI Guide

## 설치

```bash
pip install hwpparser

# HWPX 생성 기능 포함
pip install hwpparser[hwpx]

# 개발 모드 (소스에서)
pip install -e ".[all]"
```

## 기본 명령어

### `hwpparser text`
텍스트 추출 (stdout)

```bash
hwpparser text document.hwp
```

**옵션**:
- `--encoding`, `-e`: 출력 인코딩 (기본: utf-8)

```bash
hwpparser text document.hwp -e cp949
```

### `hwpparser convert`
파일 변환

```bash
# 기본 사용 (확장자 자동 인식)
hwpparser convert input.hwp output.txt
hwpparser convert input.hwp output.html
hwpparser convert input.hwp output.odt
hwpparser convert input.hwp output.pdf

# 포맷 명시
hwpparser convert input.hwp -f text -o output.txt
hwpparser convert input.hwp -f html -o output.html

# Markdown → HWPX
hwpparser convert README.md README.hwpx
```

**옵션**:
- `--format`, `-f`: 출력 포맷 (text, html, odt, pdf)
- `--output`, `-o`: 출력 파일 경로

### `hwpparser batch`
일괄 변환

```bash
# 기본 사용
hwpparser batch ./hwp_files/ -f text -o ./text_files/

# 재귀 검색
hwpparser batch ./documents/ -f pdf -o ./pdfs/ --recursive

# 에러 무시하고 계속
hwpparser batch ./files/ -f html -o ./output/ --continue-on-error
```

**옵션**:
- `--format`, `-f`: 출력 포맷 (필수)
- `--output`, `-o`: 출력 디렉토리 (필수)
- `--recursive`, `-r`: 하위 폴더 포함
- `--continue-on-error`: 에러 시 계속 진행
- `--workers`: 병렬 처리 워커 수 (기본: CPU 코어 수)

```bash
hwpparser batch ./files/ -f text -o ./output/ --workers 4
```

### `hwpparser formats`
지원 포맷 목록

```bash
hwpparser formats
```

**출력 예시**:
```
지원 변환:
  HWP → text, html, odt, pdf
  Markdown → hwpx
  HTML → hwpx
  DOCX → hwpx
```

### `hwpparser metadata`
메타데이터 추출

```bash
hwpparser metadata document.hwp

# JSON 출력
hwpparser metadata document.hwp --json
```

**출력 예시**:
```json
{
  "file_name": "document.hwp",
  "file_size": 12345,
  "char_count": 1000,
  "word_count": 200,
  "page_count": 5
}
```

## 고급 사용법

### 파이프라인

```bash
# HWP → 텍스트 → 검색
hwpparser text document.hwp | grep "검색어"

# 여러 파일 처리
find . -name "*.hwp" -exec hwpparser text {} \;

# 결과 합치기
for file in *.hwp; do
  hwpparser text "$file" >> all_text.txt
done
```

### 스크립트 통합

```bash
#!/bin/bash
# convert_all.sh

INPUT_DIR="./hwp_files"
OUTPUT_DIR="./converted"

# 텍스트 변환
hwpparser batch "$INPUT_DIR" -f text -o "$OUTPUT_DIR/text" -r

# HTML 변환
hwpparser batch "$INPUT_DIR" -f html -o "$OUTPUT_DIR/html" -r

# PDF 변환 (에러 무시)
hwpparser batch "$INPUT_DIR" -f pdf -o "$OUTPUT_DIR/pdf" -r --continue-on-error

echo "변환 완료!"
```

### 조건부 변환

```bash
# 큰 파일만 변환 (1MB 이상)
find . -name "*.hwp" -size +1M -exec hwpparser convert {} {}.txt \;

# 최근 수정된 파일만
find . -name "*.hwp" -mtime -7 | while read file; do
  hwpparser convert "$file" "${file%.hwp}.pdf"
done
```

## 환경변수

```bash
# 기본 출력 인코딩
export HWPPARSER_ENCODING=utf-8

# 임시 파일 디렉토리
export HWPPARSER_TEMP_DIR=/tmp/hwpparser

# 로그 레벨
export HWPPARSER_LOG_LEVEL=DEBUG
```

## 셸 통합

### Bash/Zsh 별칭

```bash
# ~/.bashrc 또는 ~/.zshrc
alias hwp2txt='hwpparser convert -f text'
alias hwp2pdf='hwpparser convert -f pdf'
alias hwptext='hwpparser text'
```

사용:
```bash
hwp2txt document.hwp output.txt
hwptext document.hwp | less
```

### Fish 함수

```fish
# ~/.config/fish/functions/hwp2txt.fish
function hwp2txt
    hwpparser convert -f text $argv
end
```

## 출력 제어

### 진행 상황 표시

```bash
# 배치 변환 시 진행률 표시
hwpparser batch ./files/ -f text -o ./output/ --progress

# 간략한 출력
hwpparser convert document.hwp output.txt --quiet
```

### 로그 레벨

```bash
# 상세 로그
hwpparser convert document.hwp output.pdf --verbose

# 디버그 모드
hwpparser convert document.hwp output.pdf --debug
```

## 에러 처리

### Exit Codes

- `0`: 성공
- `1`: 일반 에러
- `2`: 파일 없음
- `3`: 변환 실패
- `4`: 의존성 누락

### 에러 예시

```bash
# 파일 없음
$ hwpparser text missing.hwp
Error: File not found: missing.hwp
Exit code: 2

# 의존성 누락 (PDF 변환)
$ hwpparser convert document.hwp output.pdf
Error: Chrome not found. Install with: brew install --cask google-chrome
Exit code: 4
```

## 성능 팁

### 병렬 처리

```bash
# 워커 수 조정
hwpparser batch ./files/ -f text -o ./output/ --workers 8
```

### 대용량 파일

```bash
# 메모리 제한 설정
ulimit -v 2000000  # 2GB
hwpparser convert large_document.hwp output.txt
```

### 배치 최적화

```bash
# 먼저 실패할 파일 확인
hwpparser batch ./files/ -f pdf -o ./output/ --dry-run

# 에러 로그 저장
hwpparser batch ./files/ -f pdf -o ./output/ --continue-on-error 2> errors.log
```

## Docker 사용

```dockerfile
FROM python:3.11-slim

# 시스템 의존성
RUN apt-get update && apt-get install -y \
    pandoc \
    chromium-browser \
    && rm -rf /var/lib/apt/lists/*

# hwpparser 설치
RUN pip install hwpparser[all]

WORKDIR /data
ENTRYPOINT ["hwpparser"]
```

사용:
```bash
docker build -t hwpparser .
docker run -v $(pwd):/data hwpparser convert document.hwp output.pdf
```
