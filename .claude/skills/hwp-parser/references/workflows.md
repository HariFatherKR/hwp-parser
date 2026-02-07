# HWP Parser - Workflows & Use Cases

## 1. RAG (Retrieval-Augmented Generation) 파이프라인

### 기본 청킹

```python
import hwpparser

# HWP → 청크
chunks = hwpparser.hwp_to_chunks("document.hwp", chunk_size=1000)

for chunk in chunks:
    print(f"Text: {chunk.text}")
    print(f"Metadata: {chunk.metadata}")
    # {'file': 'document.hwp', 'page': 1, 'offset': 0, 'length': 1000}
```

### 벡터 DB 연동 (Pinecone)

```python
import hwpparser
import openai
from pinecone import Pinecone

# 초기화
pc = Pinecone(api_key="your-api-key")
index = pc.Index("hwp-documents")

# 청킹 및 벡터화
chunks = hwpparser.hwp_to_chunks("document.hwp", chunk_size=1000)

for i, chunk in enumerate(chunks):
    # OpenAI 임베딩
    embedding = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=chunk.text
    )['data'][0]['embedding']

    # Pinecone에 저장
    index.upsert([(
        f"doc_{i}",
        embedding,
        {
            "text": chunk.text,
            "file": chunk.metadata['file'],
            "page": chunk.metadata['page']
        }
    )])
```

### 벡터 DB 연동 (Chroma)

```python
import hwpparser
import chromadb
from chromadb.utils import embedding_functions

# Chroma 초기화
client = chromadb.Client()
collection = client.create_collection(
    name="hwp_docs",
    embedding_function=embedding_functions.OpenAIEmbeddingFunction()
)

# 청킹
chunks = hwpparser.hwp_to_chunks("document.hwp", chunk_size=500)

# 추가
collection.add(
    documents=[c.text for c in chunks],
    metadatas=[c.metadata for c in chunks],
    ids=[f"chunk_{i}" for i in range(len(chunks))]
)

# 검색
results = collection.query(
    query_texts=["환불 정책은?"],
    n_results=3
)
```

## 2. LangChain 연동

### 단일 문서 로더

```python
from hwpparser import HWPLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 문서 로드
loader = HWPLoader("document.hwp")
docs = loader.load()

# 청킹
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
chunks = splitter.split_documents(docs)
```

### 디렉토리 로더

```python
from hwpparser import DirectoryHWPLoader

# 폴더 전체 로드
loader = DirectoryHWPLoader("./documents", recursive=True)
docs = loader.load()

print(f"로드된 문서: {len(docs)}개")
```

### LangChain RAG 체인

```python
from hwpparser import DirectoryHWPLoader
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI

# 문서 로드
loader = DirectoryHWPLoader("./hwp_docs", recursive=True)
docs = loader.load()

# 벡터 스토어 생성
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(docs, embeddings)

# QA 체인
qa_chain = RetrievalQA.from_chain_type(
    llm=OpenAI(),
    retriever=vectorstore.as_retriever(search_kwargs={"k": 3})
)

# 질문
answer = qa_chain.run("이 문서의 주요 내용은?")
print(answer)
```

## 3. 검색 엔진 인덱싱

### Elasticsearch

```python
import hwpparser
from elasticsearch import Elasticsearch

# ES 연결
es = Elasticsearch(['http://localhost:9200'])

# 청킹 및 인덱싱
chunks = hwpparser.hwp_to_chunks("document.hwp", chunk_size=1000)

for i, chunk in enumerate(chunks):
    es.index(
        index='hwp_documents',
        id=f"doc_{i}",
        document={
            'text': chunk.text,
            'file': chunk.metadata['file'],
            'page': chunk.metadata['page'],
            'created': '2025-01-01'
        }
    )
```

### JSONL 익스포트 (범용)

```python
import hwpparser

# 폴더 전체를 JSONL로
hwpparser.export_to_jsonl(
    "./documents",
    "./search_index.jsonl",
    chunk_size=1000
)
```

**출력 형식**:
```json
{"id": "doc1_0", "text": "...", "metadata": {"file": "doc1.hwp", "page": 1}}
{"id": "doc1_1", "text": "...", "metadata": {"file": "doc1.hwp", "page": 2}}
```

### Algolia 업로드

```python
import json
from algoliasearch.search_client import SearchClient

# JSONL 읽기
with open("search_index.jsonl") as f:
    records = [json.loads(line) for line in f]

# Algolia 업로드
client = SearchClient.create('APP_ID', 'API_KEY')
index = client.init_index('hwp_docs')
index.save_objects(records)
```

## 4. 배치 문서 처리

### 폴더 전체 변환

```python
import hwpparser

# 모든 HWP → TXT
result = hwpparser.batch_convert(
    "./hwp_files",
    "./text_files",
    "txt"
)

print(f"성공: {result.success}/{result.total}")
print(f"실패: {result.failed}")
```

### 병렬 처리

```python
from concurrent.futures import ThreadPoolExecutor
import hwpparser

files = ["doc1.hwp", "doc2.hwp", "doc3.hwp"]

def convert_file(file):
    try:
        text = hwpparser.hwp_to_text(file)
        with open(f"{file}.txt", "w") as f:
            f.write(text)
        return True
    except Exception as e:
        print(f"Error: {file} - {e}")
        return False

with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(convert_file, files))

print(f"성공: {sum(results)}/{len(files)}")
```

### 조건부 처리

```python
import hwpparser
from pathlib import Path

# 최근 1주일 이내 수정된 파일만
import datetime

threshold = datetime.datetime.now() - datetime.timedelta(days=7)

for hwp_file in Path("./documents").glob("**/*.hwp"):
    if hwp_file.stat().st_mtime > threshold.timestamp():
        text = hwpparser.hwp_to_text(hwp_file)
        output = hwp_file.with_suffix(".txt")
        output.write_text(text)
```

## 5. 콘텐츠 분석

### 키워드 추출

```python
import hwpparser
from collections import Counter
import re

# 텍스트 추출
text = hwpparser.hwp_to_text("document.hwp")

# 단어 빈도 분석
words = re.findall(r'\w+', text.lower())
top_words = Counter(words).most_common(10)

print("상위 키워드:")
for word, count in top_words:
    print(f"  {word}: {count}회")
```

### 문서 요약

```python
import hwpparser
import openai

# 텍스트 추출
text = hwpparser.hwp_to_text("document.hwp")

# OpenAI 요약
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "문서를 3문장으로 요약해주세요."},
        {"role": "user", "content": text}
    ]
)

summary = response.choices[0].message.content
print(summary)
```

### 감정 분석

```python
import hwpparser
from transformers import pipeline

# 텍스트 추출
text = hwpparser.hwp_to_text("review.hwp")

# 감정 분석
classifier = pipeline("sentiment-analysis", model="snunlp/KR-FinBert-SC")
result = classifier(text[:512])  # 최대 길이 제한

print(f"감정: {result[0]['label']}, 신뢰도: {result[0]['score']:.2f}")
```

## 6. 문서 생성

### Markdown → HWPX 보고서

```python
import hwpparser

markdown = """
# 월간 보고서

## 요약
- 목표 달성: 95%
- 주요 성과: ...

## 상세 내역
...
"""

hwpparser.markdown_to_hwpx(markdown, "report.hwpx")
```

### 데이터 → 한글 문서

```python
import pandas as pd
import hwpparser

# 데이터 로드
df = pd.read_csv("sales.csv")

# Markdown 테이블 생성
markdown = "# 매출 보고서\n\n"
markdown += df.to_markdown()

# HWPX 변환
hwpparser.markdown_to_hwpx(markdown, "sales_report.hwpx")
```

### 템플릿 기반 생성

```python
import hwpparser
from jinja2 import Template

# 템플릿
template = Template("""
# {{ title }}

작성자: {{ author }}
날짜: {{ date }}

## 내용

{{ content }}
""")

# 렌더링
markdown = template.render(
    title="프로젝트 보고서",
    author="홍길동",
    date="2025-01-30",
    content="프로젝트가 성공적으로 완료되었습니다."
)

# HWPX 생성
hwpparser.markdown_to_hwpx(markdown, "project_report.hwpx")
```

## 7. API 서버 통합

### FastAPI 엔드포인트

```python
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import hwpparser
import tempfile

app = FastAPI()

@app.post("/convert/text")
async def convert_to_text(file: UploadFile = File(...)):
    # 임시 파일 저장
    with tempfile.NamedTemporaryFile(delete=False, suffix=".hwp") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    # 변환
    text = hwpparser.hwp_to_text(tmp_path)

    return {"text": text}

@app.post("/convert/pdf")
async def convert_to_pdf(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".hwp") as tmp_in:
        tmp_in.write(await file.read())

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_out:
        hwpparser.hwp_to_pdf(tmp_in.name, tmp_out.name)

    return FileResponse(tmp_out.name, media_type="application/pdf")
```

### Flask 엔드포인트

```python
from flask import Flask, request, send_file
import hwpparser
import tempfile

app = Flask(__name__)

@app.route('/api/convert', methods=['POST'])
def convert():
    file = request.files['file']
    output_format = request.form.get('format', 'text')

    with tempfile.NamedTemporaryFile(suffix=".hwp") as tmp_in:
        file.save(tmp_in.name)

        if output_format == 'text':
            text = hwpparser.hwp_to_text(tmp_in.name)
            return {'text': text}

        elif output_format == 'pdf':
            tmp_out = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
            hwpparser.hwp_to_pdf(tmp_in.name, tmp_out.name)
            return send_file(tmp_out.name, mimetype='application/pdf')
```

## 8. CI/CD 통합

### GitHub Actions

```yaml
name: Convert HWP Docs

on:
  push:
    paths:
      - 'docs/**/*.hwp'

jobs:
  convert:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install hwpparser[all]
          sudo apt-get install -y pandoc libreoffice

      - name: Convert HWP to Text
        run: |
          hwpparser batch docs/ -f text -o docs_text/ -r

      - name: Commit changes
        run: |
          git config user.name github-actions
          git config user.email github-actions@github.com
          git add docs_text/
          git commit -m "Auto-convert HWP docs"
          git push
```
