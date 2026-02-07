# HWP Parser MCP Server 설정

Claude Desktop에서 HWP 파일을 직접 다룰 수 있도록 MCP (Model Context Protocol) 서버를 설정합니다.

## Claude Desktop 설정

`~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "hwpparser": {
      "command": "python",
      "args": ["-m", "hwpparser.mcp_server"],
      "cwd": "/path/to/hwpparser",
      "env": {
        "PYTHONPATH": "/path/to/hwpparser"
      }
    }
  }
}
```

## MCP 서버 구현 예시

`hwpparser/mcp_server.py`:

```python
"""HWP Parser MCP Server for Claude Desktop."""
import json
import sys
from typing import Any

from .converter import HWPConverter
from .constants import OutputFormat


def handle_request(request: dict[str, Any]) -> dict[str, Any]:
    """Handle MCP request."""
    method = request.get("method")
    params = request.get("params", {})
    
    if method == "tools/list":
        return {
            "tools": [
                {
                    "name": "hwp_to_text",
                    "description": "HWP 파일에서 텍스트 추출",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "HWP 파일 경로"
                            }
                        },
                        "required": ["file_path"]
                    }
                },
                {
                    "name": "hwp_to_html",
                    "description": "HWP 파일을 HTML로 변환",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string"},
                            "output_path": {"type": "string"}
                        },
                        "required": ["file_path"]
                    }
                }
            ]
        }
    
    elif method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})
        
        converter = HWPConverter()
        
        if tool_name == "hwp_to_text":
            result = converter.convert(
                args["file_path"], 
                OutputFormat.TEXT
            )
            return {"content": [{"type": "text", "text": result}]}
        
        elif tool_name == "hwp_to_html":
            output = args.get("output_path", "/tmp/output.html")
            converter.convert(
                args["file_path"],
                OutputFormat.HTML,
                output
            )
            return {"content": [{"type": "text", "text": f"HTML 저장: {output}"}]}
    
    return {"error": "Unknown method"}


def main():
    """MCP Server main loop."""
    for line in sys.stdin:
        request = json.loads(line)
        response = handle_request(request)
        response["id"] = request.get("id")
        print(json.dumps(response), flush=True)


if __name__ == "__main__":
    main()
```

## 사용 예시 (Claude Desktop)

```
사용자: 이 HWP 파일 내용 보여줘 ~/Documents/계약서.hwp

Claude: [hwp_to_text 도구 호출]
계약서 내용:
...
```

## 참고

- [MCP 공식 문서](https://modelcontextprotocol.io/)
- [Claude Desktop MCP 가이드](https://docs.anthropic.com/en/docs/claude-desktop/mcp)
