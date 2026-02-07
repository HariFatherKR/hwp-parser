# ChatGPT Custom GPT 설정 가이드

## 1. Custom GPT 생성

1. [ChatGPT](https://chat.openai.com)에서 **Explore GPTs** → **Create**
2. **Configure** 탭에서 설정

## 2. 기본 설정

| 항목 | 값 |
|------|-----|
| Name | HWP 문서 도우미 |
| Description | 한글(HWP) 파일을 읽고 변환하는 AI 어시스턴트 |
| Instructions | `instructions.md` 내용 복사 |

## 3. Actions 설정 (선택사항)

API 서버가 있는 경우:

1. **Actions** → **Create new action**
2. **Import from URL** 또는 `openapi.yaml` 붙여넣기
3. Authentication 설정 (필요시)

## 4. Knowledge 업로드

다음 파일들을 업로드:
- `README.md` (프로젝트 설명)
- 샘플 HWP 파일들

## 5. Capabilities

- [x] Web Browsing
- [x] Code Interpreter (파일 처리용)
- [ ] DALL·E (불필요)

## 6. 테스트

```
사용자: HWP 파일 하나 첨부할게. 내용 읽어줘.
GPT: [Code Interpreter로 파일 분석]
```

## API 서버 없이 사용

Code Interpreter만으로도 기본적인 HWP 분석이 가능합니다:
- pyhwp 패키지 설치 (Code Interpreter 환경에서)
- 업로드된 HWP 파일 직접 처리

## 참고

- [Custom GPT 공식 문서](https://help.openai.com/en/articles/8554397-creating-a-gpt)
- [Actions 가이드](https://platform.openai.com/docs/actions)
