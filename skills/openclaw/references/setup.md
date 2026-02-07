# HWP Parser 설치 가이드

## 요구사항

- Python 3.11+
- pip
- (PDF 변환 시) Chrome 또는 Chromium

## 설치

```bash
# 저장소 클론
git clone https://github.com/snovium/hwpparser.git
cd hwpparser

# 가상환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -e .
```

## 의존성

- **pyhwp**: HWP 파일 읽기
- **six**: Python 2/3 호환성
- **click**: CLI 인터페이스

## PDF 변환을 위한 Chrome 설치

### macOS
Chrome이 이미 설치되어 있으면 별도 설치 불필요
```bash
brew install --cask google-chrome
# 또는 Chromium
brew install --cask chromium
```

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install chromium-browser
# 또는
sudo apt install google-chrome-stable
```

### Windows
[Chrome 공식 사이트](https://www.google.com/chrome/)에서 다운로드

## 설치 확인

```bash
hwpparser --version
hwpparser convert --help
```
