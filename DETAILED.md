# Second Opinion - Detailed Documentation

This document contains expanded information for installation, troubleshooting, development, and contributing. For a quick overview, see [README.md](README.md).

## Installation

### 1. Install Ollama

Download and install [Ollama](https://ollama.com/download) for your operating system.

### 2. Pull an LLM Model

Use the Ollama CLI to pull a model. Recommended models:
- **Llama 3** (strong reasoning): `ollama pull llama3`
- **Qwen 2.5** (good balance): `ollama pull qwen2.5`
- **Granite 4** (IBM model): `ollama pull granite4`

```bash
ollama pull llama3
```

### 3. Clone and Setup Python Environment

```bash
# Clone the repository
git clone https://github.com/divarun/second_opinion
cd second_opinion

# Create a virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory:

```dotenv
# Ollama LLM Configuration
# MUST match the model you pulled with `ollama pull`
OLLAMA_MODEL_NAME="llama3"
# Default base URL for Ollama (usually this)
OLLAMA_BASE_URL="http://localhost:11434"

# Optional: Override system prompt
# LLM_SYSTEM_PROMPT="Your custom system prompt here"
```

**Important**: The `OLLAMA_MODEL_NAME` must exactly match the model you pulled. For example:
- If you ran `ollama pull llama3`, use `OLLAMA_MODEL_NAME="llama3"`
- If you ran `ollama pull qwen2.5`, use `OLLAMA_MODEL_NAME="qwen2.5"`

## Running the Application

### Start the Server

```bash
uvicorn app.main:app --reload
```

### Access the Application

Open your web browser and navigate to:

```
http://localhost:8000
```

The default port is `8000`. If you need to use a different port:

```bash
uvicorn app.main:app --reload --port 8080
```

## Usage

### 1. Submit a Design Document

You can provide input in two ways:

**Option A: Upload a File**
- Click "Upload RFC, design document, or PR description"
- Supported formats: `.md`, `.txt`, `.rst`, `.adoc`, `.asciidoc`, `.text`
- Drag and drop or click to browse

**Option B: Paste Text**
- Paste your RFC, design document, or PR description directly into the text area

### 2. Provide Optional Context (Recommended)

While not required, providing context improves analysis quality:

- **Expected scale (QPS)**: e.g., "10k QPS"
- **Expected data size**: e.g., "100GB"
- **Critical SLOs (latency)**: e.g., "p99 < 200ms"
- **Critical SLOs (availability)**: e.g., "99.9%"
- **Known dependencies**: e.g., "Redis, PostgreSQL, S3"

### 3. Review the Report

Click **"Analyze"** to generate the pre-mortem review. The report includes:

- **Overview**: Overall risk profile and primary concern
- **Potential Failure Modes**: Ranked list with confidence scores, evidence, and discussion questions
- **Implicit Assumptions**: Unstated expectations detected in the design
- **Ruled-Out Risks**: Common risks that don't apply to your design
- **Unknowns / Not Evaluated**: Missing information that could affect analysis

Click on any failure mode to expand and see detailed information.

## Project Structure

```
second_opinion/
├── app/
│   ├── api.py              # FastAPI routes and endpoints
│   ├── assumptions.py      # Implicit assumption extraction
│   ├── file_processor.py   # File upload handling
│   ├── ingestion.py        # Document parsing
│   ├── llm.py              # LLM integration (Ollama)
│   ├── main.py             # FastAPI application entry point
│   ├── matcher.py          # Pattern matching engine
│   ├── models.py           # Pydantic data models
│   ├── patterns.py         # Failure pattern library loader
│   ├── pattern_matcher.py  # Alternative semantic matching
│   ├── prompts.py          # Centralized prompt library
│   ├── report.py           # Report generation
│   ├── ruled_out.py        # Ruled-out risk detection
│   ├── synthesis.py        # Summary generation
│   ├── unknowns.py         # Unknown detection
│   ├── versioning.py       # Version tracking
│   └── static/
│       ├── index.html      # Web UI template
│       └── styles.css      # CSS styles
├── data/
│   └── failure_patterns.json  # Curated failure pattern library
├── .env                    # Environment variables (create this)
├── requirements.txt         # Python dependencies
└── README.md               # Main documentation
```

## Troubleshooting

### "Error: Model name not configured"

**Solution**: Ensure your `.env` file exists and contains `OLLAMA_MODEL_NAME` matching the model you pulled.

### "Could not call Ollama"

**Solutions**:
1. Verify Ollama is running: `ollama list` should show your models
2. Check that the model name in `.env` exactly matches the model you pulled
3. Ensure Ollama is accessible at `http://localhost:11434` (or your configured `OLLAMA_BASE_URL`)

### Port Already in Use

**Solution**: Use a different port:
```bash
uvicorn app.main:app --reload --port 8080
```

### Import Errors

**Solution**: Ensure you're in the virtual environment and dependencies are installed:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### File Upload Not Working

**Solution**: 
- Check file size (large files may timeout)
- Ensure file format is supported (`.md`, `.txt`, `.rst`, `.adoc`, etc.)
- Try pasting text directly instead

## Design Philosophy

Second Opinion is designed to:
- **Prefer silence over speculation** - Better to miss a pattern than generate false positives
- **Optimize for explainability over completeness** - Every finding should be traceable to evidence
- **Surface discussion, not decisions** - The tool prompts questions, not answers
- **Treat design reviews as socio-technical processes** - Context and team judgment matter

## Non-Goals

Second Opinion does not aim to:
- Automatically approve or reject designs
- Replace experienced human reviewers
- Detect all possible failure modes
- Provide guarantees about system reliability
- Evaluate business correctness or product requirements

## Development

### Running in Development Mode

The `--reload` flag enables auto-reload when code changes:

```bash
uvicorn app.main:app --reload
```

### Adding New Failure Patterns

Edit `data/failure_patterns.json` to add new patterns. Each pattern should include:
- `id`: Unique identifier
- `name`: Human-readable name
- `signals`: Keywords to match against
- `trigger_conditions`: Conditions that trigger the failure
- `why_subtle`: Why this failure is easy to miss
- `impact_surface`: Qualitative blast radius
- `discussion_questions`: Questions for the team
- `required_context`: Context needed to evaluate
- `safety_signals`: Mitigations that reduce risk

### Customizing Prompts

Edit `app/prompts.py` to modify LLM prompts. All prompts are centralized here for easy versioning and maintenance.

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details on:

- How to report issues
- How to submit pull requests
- Development guidelines
- Code style standards
- Areas where contributions are needed

We appreciate your help in making Second Opinion better!
