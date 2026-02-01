# Quick Reference Guide

## Installation (5 Minutes)

```bash
# 1. Setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Edit .env if needed

# 3. Ensure Ollama is running
ollama serve  # In separate terminal
ollama pull llama3

# 4. Start
./start.sh  # Linux/Mac
start.bat   # Windows
# Or: python app.py
```

## Usage

1. Open http://localhost:8000
2. Paste document OR upload file
3. Add context (optional): scale, SLOs, dependencies
4. Click "Analyze Document"
5. Review results in ~30-60 seconds

## API Examples

### Analyze Text
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

## Configuration

Edit `.env`:
```env
# Use different model
OLLAMA_MODEL=qwen2.5:14b

# Increase timeout for large docs
OLLAMA_TIMEOUT=180

# Adjust thresholds
CONFIDENCE_THRESHOLD=0.7
MAX_FAILURE_MODES=15
```

## Common Issues

### "Ollama connection failed"
- Start Ollama: `ollama serve`
- Check URL matches `.env`
- Verify model: `ollama list`

### Slow analysis
- Use smaller model: `llama3:8b`
- Reduce document size
- Increase timeout

### Out of memory
- Use quantized: `llama3:8b-q4_0`
- Lower `MAX_DOCUMENT_SIZE`

## File Structure

```
7 core files + 3 directories:
├── app.py           - FastAPI app (180 lines)
├── analyzer.py      - Analysis engine (220 lines)
├── patterns.py      - Pattern library (230 lines)
├── llm.py          - Ollama client (100 lines)
├── models.py       - Data models (80 lines)
├── config.py       - Settings (30 lines)
├── templates/      - HTML template
├── static/         - CSS + JavaScript
└── tests/          - Basic tests
```

## Customization

### Add Pattern
Edit `patterns.py`:
```python
FailurePattern(
    id="my_pattern",
    name="My Pattern",
    description="What it detects",
    category=PatternCategory.LOAD,
    indicators=["keyword1", "keyword2"],
    why_easy_to_miss="Why..."
)
```

### Modify Analysis
Edit `analyzer.py`:
- Change prompts
- Add analysis steps
- Adjust scoring

### UI Changes
- `templates/index.html` - Structure
- `static/style.css` - Styling
- `static/script.js` - Behavior

## Testing

```bash
# Run tests
pip install pytest pytest-asyncio
pytest test_basic.py -v

# Test with example
python -c "
import asyncio
from analyzer import DesignAnalyzer

async def test():
    analyzer = DesignAnalyzer()
    with open('example_design.md') as f:
        doc = f.read()
    results = await analyzer.analyze(doc)
    print(results['summary'])

asyncio.run(test())
"
```

## Deployment

### Development
```bash
uvicorn app:app --reload
```

### Production
```bash
# Install production server
pip install gunicorn

# Run with workers
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Architecture Improvements Over Original

1. **Simplified Structure**
    - Single-file modules vs nested packages
    - 7 files vs 15+ files
    - ~1,500 lines vs ~3,000+ lines

2. **Direct Dependencies**
    - No abstraction layers
    - Direct Ollama API calls
    - Flat data models

3. **Cleaner Code**
    - Less boilerplate
    - Fewer classes
    - Clear responsibilities

4. **Maintained Features**
    - All 16 patterns
    - Full analysis pipeline
    - Complete UI
    - API endpoints

## Performance Tips

- **Faster models**: `llama3:8b` < `qwen2.5` < `llama3:70b`
- **Parallel analysis**: Run multiple workers
- **Caching**: Add Redis for repeated docs
- **Batch processing**: Analyze multiple docs

## Security Notes

- No authentication included (add if needed)
- Input validation on file uploads
- XSS protection in frontend
- No sensitive data in logs

## Support

- Issues: Check logs in terminal
- Health: http://localhost:8000/api/health
- Patterns: http://localhost:8000/api/patterns
- Example: Use `example_design.md`