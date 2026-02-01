# Quick Reference Guide

This is a command-first guide for getting Second Opinion running quickly.  
For background, concepts, and failure patterns, see **README.md**.

---

## Installation (≈ 5 Minutes)

### 1. Environment Setup
```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
2. Configuration
cp .env.example .env
# Edit .env if needed
3. Start Ollama
ollama serve        # In a separate terminal
ollama pull llama3
4. Start the App
python app.py
# or
uvicorn app:app --reload

```
Open http://localhost:8000

## Usage

1. Open the web UI
2. Paste a document or upload a file.

(Optional) Add context:
* scale
* SLOs
  *dependencies

3. Click Analyze Document
4. Review results (~30–60 seconds)

API Examples
Analyze Text
```bash
curl -X POST http://localhost:8000/api/analyze \
-H "Content-Type: application/json" \
-d '{
"document": "Your design document...",
"context": {
"scale": "10M req/day",
"slos": "99.9% uptime"
}
}'

```

Upload File
```bash
curl -X POST http://localhost:8000/api/upload \
-F "file=@design.md" \
-F "context_scale=10M req/day"
```

List Patterns
```bash
curl http://localhost:8000/api/patterns
```

Health Check
```bash
curl http://localhost:8000/api/health
```

Configuration

Edit .env:
```bash
# Model selection
OLLAMA_MODEL=qwen2.5:14b

# Timeouts
OLLAMA_TIMEOUT=180

# Analysis behavior
CONFIDENCE_THRESHOLD=0.7
MAX_DOCUMENT_SIZE=50000
MAX_FAILURE_MODES=15
```

### Common Issues
"Ollama connection failed"
* Ensure Ollama is running: ollama serve
* Verify URL in .env
* Confirm model is available: ollama list

Slow analysis
* Use a smaller model: llama3:8b
* Reduce document size
* Increase timeout

Out of memory

* Use quantized models: llama3:8b-q4_0
* Lower MAX_DOCUMENT_SIZE

## Testing
Install testing tools:
```bash
pip install pytest pytest-asyncio
```
Run tests
```bash
pytest test_basic.py -v
```

Quick manual test:
```bash
python -c "
import asyncio
from analyzer import DesignAnalyzer

async def test():
a = DesignAnalyzer()
with open('example_design.md') as f:
doc = f.read()
r = await a.analyze(doc)
print(r['summary'])

asyncio.run(test())
"
```
## Deployment
Development
```bash
uvicorn app:app --reload
```
Production
```bash
pip install gunicorn
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker \
--bind 0.0.0.0:8000
```
Docker
```bash
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Performance Tips

* Faster models: llama3:8b < qwen2.5 < llama3:70b
* Parallelism: Multiple workers for concurrent analysis
* Caching: Add Redis for repeated documents
* Batching: Analyze multiple docs programmatically

### Security Notes

* No authentication by default
* Input validation on uploads
* XSS protection in frontend
* Avoid logging sensitive documents

### Support & Debugging

* Logs: terminal output
* Health: http://localhost:8000/api/health
* Patterns: http://localhost:8000/api/patterns