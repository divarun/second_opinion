# Quick Reference Guide

This is a command-first guide for getting Second Opinion running quickly.  
For background, concepts, and failure patterns, see **README.md**.

---

## Installation (≈ 5 Minutes)

### 1. Docker (recommended)

```bash
docker compose up --build
```

Open 



(Ollama at http://localhost:11434)

### 2. Local with Ollama

```bash
python -m venv venv
venv\Scripts\activate      # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
ollama serve &
ollama pull llama3
uvicorn app.app:app --reload
```

Open http://localhost:8000

### 3. Local with Anthropic Claude

```bash
python -m venv venv
venv\Scripts\activate      # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt

# Set provider and key (or add to .env)
set LLM_PROVIDER=anthropic                # macOS/Linux: export LLM_PROVIDER=anthropic
set ANTHROPIC_API_KEY=sk-ant-...

uvicorn app.app:app --reload
```

Open http://localhost:8000

---

## Usage

1. Open the web UI
2. Paste a document or upload a file (.md, .txt, .rst, .adoc, or .pdf)
3. Optionally add context: scale, SLOs, dependencies
4. Click **Run Analysis**
5. Review results — live progress updates appear as each step completes (~30–60 seconds)
6. Export the report via **Copy as Markdown** or **Download JSON**

---

## API Examples

### Analyze Text (streaming)

```bash
curl -X POST http://localhost:8000/api/analyze/stream \
  -H "Content-Type: application/json" \
  -d '{
    "document": "Your design document...",
    "context": {
      "scale": "10M req/day",
      "slos": "99.9% uptime"
    }
  }'
```

### Analyze Text (non-streaming)

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

### Upload File

```bash
# Supports .md, .txt, .rst, .adoc, .pdf
curl -X POST http://localhost:8000/api/upload \
  -F "file=@design.md" \
  -F "context_scale=10M req/day"
```

### List Patterns

```bash
curl http://localhost:8000/api/patterns
```

### Health Check

```bash
curl http://localhost:8000/api/health
```

---

## Configuration

Use env vars or a `.env` file in the project root:

| Variable | Default | Description |
|---|---|---|
| `LLM_PROVIDER` | `ollama` | `ollama` or `anthropic` |
| `OLLAMA_MODEL` | `llama3` | Ollama model name |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Compose: `http://ollama:11434` |
| `OLLAMA_TIMEOUT` | `120` | Request timeout (seconds) |
| `ANTHROPIC_API_KEY` | _(empty)_ | Required when using Anthropic |
| `ANTHROPIC_MODEL` | `claude-sonnet-4-6` | Anthropic model ID |
| `CONFIDENCE_THRESHOLD` | `0.6` | Minimum score for a finding |
| `MAX_DOCUMENT_SIZE` | `50000` | Max input characters |
| `MAX_FAILURE_MODES` | `10` | Max findings returned |

---

## Common Issues

### "Ollama connection failed"
- Ensure Ollama is running: `ollama serve`
- Verify `OLLAMA_BASE_URL` in `.env`
- Confirm model is available: `ollama list`

### Slow analysis
- Use a smaller model: `OLLAMA_MODEL=llama3:8b`
- Reduce document size
- Increase `OLLAMA_TIMEOUT`
- Switch to Anthropic for faster, more reliable JSON output

### Out of memory (Ollama)
- Use a quantized model: `OLLAMA_MODEL=llama3:8b-q4_0`
- Lower `MAX_DOCUMENT_SIZE`

### PDF text extraction returns empty
- The PDF may be image-only or scanned; pypdf cannot extract text from rasterized PDFs
- Convert to text first using an OCR tool, then paste or upload as `.txt`

---

## Deployment

### Development

```bash
uvicorn app.app:app --reload
```

### Production

```bash
pip install gunicorn
gunicorn app.app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker

```bash
docker compose up --build
```

---

## Performance Tips

- Faster local models: `llama3:8b` is much quicker than `llama3:70b` with reasonable quality
- Anthropic Claude gives the most reliable structured JSON output
- Multiple gunicorn workers handle concurrent analyses without blocking
- Reduce `MAX_FAILURE_MODES` to shorten analysis time

---

## Security Notes

- No authentication by default — add a reverse proxy (nginx, Caddy) with auth for shared deployments
- Input validation on file uploads
- XSS protection in frontend (all user content is escaped before rendering)
- Avoid logging document contents in production

---

## Support & Debugging

- Logs: terminal output from uvicorn/gunicorn
- Health endpoint: http://localhost:8000/api/health
- Pattern list: http://localhost:8000/api/patterns
