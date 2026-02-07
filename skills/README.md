# HWP Parser - AI Agent Skills

각 AI 플랫폼에서 HWP Parser를 사용하기 위한 스킬/플러그인 정의입니다.

## 지원 플랫폼

| 플랫폼 | 폴더 | 설명 |
|--------|------|------|
| **OpenClaw** | `openclaw/` | OpenClaw Agent Skill (SKILL.md + scripts) |
| **Claude** | `claude/` | Claude Code/Desktop (CLAUDE.md + MCP Server) |
| **ChatGPT** | `chatgpt/` | Custom GPT (Instructions + OpenAPI Actions) |
| **Gemini** | `gemini/` | Google AI Studio / Vertex AI (System Prompt + Functions) |

## 폴더 구조

```
skills/
├── README.md           # 이 파일
├── openclaw/
│   ├── SKILL.md        # OpenClaw 스킬 정의
│   ├── scripts/
│   │   └── convert.sh  # 변환 스크립트
│   └── references/
│       └── setup.md    # 설치 가이드
├── claude/
│   ├── CLAUDE.md       # Claude 프로젝트 가이드
│   └── mcp-server.md   # MCP 서버 설정
├── chatgpt/
│   ├── README.md       # 설정 가이드
│   ├── instructions.md # Custom GPT 시스템 프롬프트
│   └── openapi.yaml    # Actions API 스펙
└── gemini/
    ├── README.md       # 사용 가이드
    ├── system-prompt.md
    └── functions.json  # Function Calling 정의
```

## 사용 방법

### OpenClaw
```bash
# SKILL.md를 ~/.openclaw/workspace/skills/hwp-parser/에 복사
cp -r skills/openclaw ~/.openclaw/workspace/skills/hwp-parser
```

### Claude Code / Claude Desktop
```bash
# 프로젝트 루트에 CLAUDE.md 복사
cp skills/claude/CLAUDE.md ./CLAUDE.md

# MCP 서버 설정 (Claude Desktop)
# skills/claude/mcp-server.md 참조
```

### ChatGPT Custom GPT
1. [ChatGPT](https://chat.openai.com) → Explore GPTs → Create
2. `instructions.md` 내용을 Instructions에 붙여넣기
3. Actions에 `openapi.yaml` 추가 (API 서버가 있는 경우)

### Google Gemini
1. [Google AI Studio](https://aistudio.google.com)
2. System Instructions에 `system-prompt.md` 내용 입력
3. API 사용 시 `functions.json`으로 Function Calling 설정

## 공통 기능

모든 플랫폼에서 다음 기능을 지원합니다:

- ✅ HWP → 텍스트 추출
- ✅ HWP → HTML 변환
- ✅ HWP → ODT 변환
- ✅ HWP → PDF 변환 (Chrome headless)
- ✅ 일괄 변환

## 기여하기

새로운 AI 플랫폼 지원 추가:
1. `skills/<platform>/` 폴더 생성
2. 해당 플랫폼의 스킬/플러그인 형식에 맞게 파일 작성
3. 이 README에 추가
4. PR 제출

## 라이선스

MIT License
