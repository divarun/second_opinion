# Second Opinion 

A streamlined pre-mortem review tool that helps engineering teams identify potential failure modes in system design documents. By mapping designs against a curated library of distributed-systems failure archetypes, it surfaces subtle, emergent failure patterns that often only appear under real production load or during partial outages.


This tool grew out of years of running design reviews where the hardest failures weren't the obvious ones.

## Features

- 🔍 **16+ Failure Patterns**: Curated distributed systems failure archetypes
- 🎯 **Confidence Scoring**: High/Medium/Low confidence levels
- 📊 **Structured Reports**: Clear, actionable analysis
- 🚀 **Fast Analysis**: Optimized LLM prompts
- 💻 **Clean UI**: Modern, responsive interface

## Quick Start

### Prerequisites

- Python 3.8 or higher
- Ollama installed and running locally
- An LLM model (recommended: `llama3`, `qwen2.5`, or `granite3`)

### Installation

```bash
# Clone or download this directory
cd second_opinion_simplified

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Pull an LLM model (if not already done)
ollama pull llama3

# Create .env file
cp .env.example .env
```

### Configuration

Edit `.env` to customize settings:

```env
OLLAMA_MODEL=llama3
OLLAMA_BASE_URL=http://localhost:11434
MAX_DOCUMENT_SIZE=50000
CONFIDENCE_THRESHOLD=0.6
```

### Run the Application

```bash
# Start the server
uvicorn app:app --reload

# Or use Python directly
python app.py
```

Then open **http://localhost:8000** in your browser.

## Usage

### 1. Paste Text
- Paste your design document directly into the text area
- Add optional context (scale, SLOs, dependencies)
- Click "Analyze Document"

### 2. Upload File
- Upload a file (.md, .txt, .rst, .adoc)
- Add optional context
- Click "Analyze Document"

### 3. Review Results
The analysis provides:
- **Failure Modes**: Ranked list of potential failures with evidence
- **Implicit Assumptions**: Unstated expectations in the design
- **Known Unknowns**: Missing critical information
- **Ruled Out Risks**: Patterns that don't apply

Click on any failure mode to see:
- Evidence from your document
- Trigger conditions
- Why it's easy to miss
- Discussion questions for your team

## Project Structure

```
second_opinion_simplified/
├── app.py              # Main FastAPI application
├── analyzer.py         # Core analysis engine
├── patterns.py         # Failure pattern definitions
├── llm.py             # Ollama LLM integration
├── models.py          # Pydantic data models
├── config.py          # Configuration management
├── templates/
│   └── index.html     # Main UI template
├── static/
│   ├── style.css      # Styles
│   └── script.js      # Frontend JavaScript
├── requirements.txt   # Python dependencies
└── .env.example       # Example configuration

Total: ~1,500 lines of code (simplified from original)
```

## API Endpoints

### POST `/api/analyze`
Analyze pasted text.

**Request:**
```json
{
  "document": "Design document text...",
  "context": {
    "scale": "10M requests/day",
    "slos": "99.9% uptime",
    "dependencies": "PostgreSQL, Redis"
  }
}
```

**Response:**
```json
{
  "failure_modes": [...],
  "implicit_assumptions": [...],
  "known_unknowns": [...],
  "ruled_out_risks": [...],
  "summary": "..."
}
```

### POST `/api/upload`
Upload and analyze a file.

**Form Data:**
- `file`: Design document file
- `context_scale`: Optional scale info
- `context_slos`: Optional SLO info
- `context_dependencies`: Optional dependencies

### GET `/api/patterns`
List all available failure patterns.

### GET `/api/health`
Check service health and Ollama connection.

## Failure Patterns

The tool analyzes against 16 curated patterns:

**Load Patterns:**
- Thundering Herd Amplification
- Load Shedding Blind Spot
- Retry Storm
- Hotspot/Hot Shard

**Dependency Patterns:**
- Hidden Synchronous Dependency
- Degraded but Not Dead

**Data Patterns:**
- Silent Data Loss
- Metadata Corruption
- Poison Message
- State Machine Explosion

**Timing Patterns:**
- Cascading Timeout
- Clock Skew Issues

**Resource Patterns:**
- Resource Exhaustion
- Unbounded Growth

**Distributed Patterns:**
- Partial Outage Inconsistency
- Version Skew
- Coordination Overhead

## Customization

### Add New Patterns
Edit `patterns.py`:

```python
FailurePattern(
    id="your_pattern_id",
    name="Your Pattern Name",
    description="What this pattern detects",
    category=PatternCategory.LOAD,
    indicators=["keyword1", "keyword2"],
    why_easy_to_miss="Explanation"
)
```

### Adjust Analysis
Edit `analyzer.py` to modify:
- LLM prompts
- Confidence thresholds
- Analysis steps

### Change LLM Model
Update `.env`:
```env
OLLAMA_MODEL=qwen2.5:14b
```

## Troubleshooting

### "Ollama connection failed"
- Ensure Ollama is running: `ollama serve`
- Check the URL in `.env`
- Verify model is pulled: `ollama list`

### Analysis is slow
- Use a smaller model: `llama3:8b` instead of `llama3:70b`
- Reduce document size
- Increase timeout in `.env`

### Out of memory
- Use a quantized model: `llama3:8b-q4_0`
- Reduce `MAX_DOCUMENT_SIZE` in `.env`

## Comparison with Original

**Simplified Version:**
- ~1,500 lines of code (vs ~3,000+)
- 7 core files (vs 15+)
- Single-file modules
- No complex abstractions
- Direct Ollama integration
- Flat data models

**Maintained Features:**
- All 16 failure patterns
- Complete analysis pipeline
- Web UI with file upload
- Confidence scoring
- Evidence tracking
- Discussion questions

**Removed Complexity:**
- Multiple route files
- Complex service layers
- Over-abstracted data models
- Nested module structure
- Redundant validations

## Development

### Run Tests
```bash
# Install dev dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

### Code Style
```bash
# Format code
pip install black
black .

# Lint
pip install flake8
flake8 .
```

## License

MIT License - See LICENSE file

## Contributing

This is a simplified educational version. For the full-featured version, see:
https://github.com/divarun/second_opinion

## Acknowledgments

Based on the original Second Opinion by divarun.
Simplified for clarity and ease of understanding.

---

**Note:** Second Opinion assists in design reviews but does not replace human judgment. It surfaces potential failure modes based on known patterns but does not guarantee completeness or correctness.