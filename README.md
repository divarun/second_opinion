# Second Opinion

**Second Opinion** is a pre-mortem review tool that helps engineering teams identify potential failure modes in system design documents before they ship. By mapping designs against a curated library of distributed-systems failure archetypes, it surfaces subtle, emergent failure patterns that often only appear under real production load or during partial outages.

This tool grew out of years of running design reviews where the hardest failures weren't the obvious ones.

## Quick Start

```bash
git clone https://github.com/divarun/second_opinion
cd second_opinion
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
ollama pull llama3

# Create .env file
echo 'OLLAMA_MODEL_NAME="llama3"' > .env
echo 'OLLAMA_BASE_URL="http://localhost:11434"' >> .env

# Start the server
uvicorn app.main:app --reload
```

Then open **http://localhost:8000**

## Who This Is For

Second Opinion is designed for:
- **Staff+ engineers and architects** reviewing system designs
- **Engineering leaders** running design or RFC reviews
- **Teams operating distributed systems** at scale

It is **not** intended for:
- Replacing formal design reviews
- Automated approval or gating
- Greenfield learning projects

## What It Does

Second Opinion performs automated analysis of RFCs, design documents, and PR descriptions to identify:

- **Potential Failure Modes**: Ranked list of failure patterns that match your design
- **Implicit Assumptions**: Unstated expectations embedded in the design
- **Ruled-Out Risks**: Common risks that are explicitly not applicable to your design
- **Known Unknowns**: Areas where critical information is missing or unspecified

The tool is intentionally conservative—it prefers silence over speculation and focuses on explainable, evidence-based findings rather than generic advice.

## Failure Patterns

Second Opinion maps designs against 16+ curated distributed-systems failure patterns, including:

- **Thundering herd amplification** - Cascading load spikes from coordinated retries
- **Hidden synchronous dependencies** - Unseen blocking calls in critical paths
- **Load-shedding blind spots** - Missing circuit breakers or backpressure
- **Retry storms** - Exponential backoff failures causing amplification
- **Partial outage inconsistency** - Split-brain scenarios and degraded state handling
- **Cascading timeouts** - Chain reactions from upstream failures
- **Resource exhaustion** - Memory, connection, or CPU saturation patterns
- And more...

## Example Output

```
Failure Mode: Hidden Synchronous Dependency
Confidence: High
Evidence: "All write paths synchronously call Service B"
Match: 85%

Trigger Conditions:
- Service B experiences latency degradation
- Network partitions between services
- Service B enters degraded mode but remains partially available

Why This Is Easy to Miss:
- Synchronous calls may be abstracted behind libraries
- Design documents often focus on happy path
- Degraded-but-not-down states are rarely tested

Discussion Questions:
- What happens when Service B is degraded but not down?
- Can writes proceed with stale data or should they fail fast?
- Is there a fallback mechanism for Service B unavailability?
```

## Prerequisites

- **Python 3.8+**
- **Ollama** installed and running locally
- An LLM model pulled via Ollama (recommended: `llama3`, `qwen2.5`, or `granite4`)

## Usage

1. **Submit a Design Document**: Upload a file (`.md`, `.txt`, `.rst`, `.adoc`) or paste text directly
2. **Provide Optional Context**: Add expected scale, SLOs, and dependencies for better analysis
3. **Review the Report**: Click "Analyze" to generate a pre-mortem review with ranked failure modes

Click on any failure mode to expand and see detailed evidence, trigger conditions, and discussion questions.

## Features

- 📄 **Multiple Input Formats**: Upload files or paste directly
- 🔍 **Pattern Matching**: Maps designs against 16+ curated failure patterns
- 🎯 **Confidence Scoring**: High/Medium/Low confidence based on match strength
- 📊 **Structured Reports**: Discussion-ready pre-mortem reviews
- 🔗 **Evidence Tracking**: Links findings to document sections

## Need More Details?

See [DETAILED.md](DETAILED.md) for:
- Complete installation instructions
- Troubleshooting guide
- Development setup
- Project structure
- Contributing guidelines

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Note**: Second Opinion is a tool to assist in design reviews, not a replacement for human judgment. It surfaces potential failure modes based on known patterns but does not guarantee completeness or correctness.
