# HWP Parser Skill

HWP/HWPX 파일을 텍스트, HTML, ODT, PDF로 변환하는 스킬입니다.

## Prerequisites

```bash
# Python 3.11+ with venv
cd /path/to/hwpparser
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

## Commands

### 텍스트 추출
```bash
hwpparser convert input.hwp -f text -o output.txt
```

### HTML 변환
```bash
hwpparser convert input.hwp -f html -o output.html
```

### ODT 변환
```bash
hwpparser convert input.hwp -f odt -o output.odt
```

### PDF 변환 (Chrome headless)
```bash
hwpparser convert input.hwp -f pdf -o output.pdf
```

### 일괄 변환
```bash
hwpparser batch ./documents/ -f text -o ./output/
```

## Output Formats

| Format | Extension | Description |
|--------|-----------|-------------|
| `text` | `.txt` | 순수 텍스트 추출 |
| `html` | `.html` | HTML 문서 변환 |
| `odt` | `.odt` | OpenDocument 포맷 |
| `pdf` | `.pdf` | PDF (Chrome headless) |

## Examples

### HWP 파일에서 텍스트 추출하기
```bash
# 사용자 요청: "이 HWP 파일 내용 읽어줘"
hwpparser convert document.hwp -f text -o /tmp/output.txt
cat /tmp/output.txt
```

### 여러 HWP 파일을 HTML로 변환
```bash
# 사용자 요청: "documents 폴더의 모든 HWP를 HTML로 변환해줘"
hwpparser batch ./documents/ -f html -o ./html_output/
```

## Troubleshooting

### pyhwp 의존성 오류
```bash
pip install pyhwp six
```

### PDF 변환 실패
Chrome 또는 Chromium 설치 필요:
```bash
# macOS
brew install --cask google-chrome

# Ubuntu
sudo apt install chromium-browser
```

## References

- [pyhwp GitHub](https://github.com/mete0r/pyhwp)
- [HWP 파일 포맷](https://www.hancom.com/etc/hwpDownload.do)
