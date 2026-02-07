# Gemini에서 HWP Parser 사용하기

## 방법 1: Google AI Studio

### 설정

1. [Google AI Studio](https://aistudio.google.com) 접속
2. **New Chat** → **System Instructions**에 `system-prompt.md` 내용 입력
3. **Tools** → **Code Execution** 활성화

### 사용

```
사용자: [HWP 파일 업로드] 이 문서 내용 읽어줘
Gemini: [Code Execution으로 pyhwp 사용]
```

## 방법 2: Gemini API (Function Calling)

### Python 예제

```python
import google.generativeai as genai
import json

# API 키 설정
genai.configure(api_key="YOUR_API_KEY")

# Function 정의 로드
with open("functions.json") as f:
    tools = json.load(f)

# 모델 설정
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    tools=tools["function_declarations"],
    system_instruction=open("system-prompt.md").read()
)

# 대화
chat = model.start_chat()
response = chat.send_message("이 HWP 파일 분석해줘: /path/to/doc.hwp")

# Function call 처리
for part in response.candidates[0].content.parts:
    if hasattr(part, 'function_call'):
        fn = part.function_call
        if fn.name == "extract_text":
            # hwpparser 호출
            result = extract_hwp_text(fn.args["file_path"])
            # 결과 전달
            response = chat.send_message(
                genai.types.Content(
                    parts=[genai.types.Part(
                        function_response=genai.types.FunctionResponse(
                            name=fn.name,
                            response={"text": result}
                        )
                    )]
                )
            )
```

## 방법 3: Vertex AI Agent Builder

### 설정 단계

1. Google Cloud Console → Vertex AI → Agent Builder
2. **Create Agent** → 이름: "HWP Document Assistant"
3. **Goals**에 목표 입력
4. **Tools** → Custom Tool 추가

### OpenAPI 스펙 업로드

ChatGPT의 `openapi.yaml`을 그대로 사용 가능:
1. Tools → Create Tool → OpenAPI
2. `openapi.yaml` 업로드
3. Authentication 설정

## 참고 링크

- [Gemini API Function Calling](https://ai.google.dev/docs/function_calling)
- [Vertex AI Agent Builder](https://cloud.google.com/vertex-ai/docs/agents)
- [Google AI Studio](https://aistudio.google.com)
