# Contributing to Second Opinion

Thank you for your interest in contributing to Second Opinion! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow

## How to Contribute

### Reporting Issues

If you find a bug or have a feature request:

1. **Check existing issues** to see if it's already reported
2. **Create a new issue** with:
   - Clear title and description
   - Steps to reproduce (for bugs)
   - Expected vs. actual behavior
   - Environment details (OS, Python version, LLM provider and model)

### Contributing Code

#### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/your-username/second_opinion.git
cd second_opinion
```

#### 2. Set Up Development Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

#### 4. Make Changes

- Follow existing code style and patterns
- Update documentation if needed
- Test your changes locally

#### 5. Start the Server and Test

```bash
uvicorn app.app:app --reload
```

Then open http://localhost:8000, paste a sample design document, and verify:
- Analysis runs to completion
- Results display correctly
- Error handling works for invalid inputs

#### 6. Commit Your Changes

```bash
git add .
git commit -m "Description of your changes"
```

**Commit Message Guidelines:**
- Use clear, descriptive messages
- Start with a verb (Add, Fix, Update, Remove, etc.)
- Keep the first line under 72 characters

Examples:
- `Add support for .docx file uploads`
- `Fix pattern matching for retry amplification`
- `Update UI to show confidence percentages`

#### 7. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:
- Clear title and description
- Reference any related issues
- Describe what changed and why

---

## Development Guidelines

### Code Style

- Follow PEP 8 Python style guide
- Use meaningful variable and function names
- Keep functions focused and small

### Project Structure

- **`app/app.py`** — FastAPI routes and application entrypoint
- **`app/analyzer.py`** — Core analysis engine; prompts and LLM calls live here
- **`app/patterns.py`** — Failure pattern definitions (the curated pattern library)
- **`app/llm.py`** — Multi-provider LLM client (`OllamaClient`, `AnthropicLLMClient`)
- **`app/models.py`** — Pydantic data models (`FailurePattern`, `Finding`, etc.)
- **`app/config.py`** — Settings loaded from environment variables
- **`app/templates/`** — Jinja2 HTML templates
- **`app/static/`** — CSS and JavaScript

### Adding New Failure Patterns

1. Open `app/patterns.py`
2. Add a new `FailurePattern` to the `PATTERNS` list following this structure:

   ```python
   FailurePattern(
       id="unique_snake_case_id",
       name="Human Readable Pattern Name",
       description="One-sentence description of the failure mode",
       category=PatternCategory.LOAD,  # LOAD | DEPENDENCY | DATA | TIMING | RESOURCE | DISTRIBUTED
       indicators=[
           "keyword or phrase that signals this pattern",
           "another signal term",
       ],
       why_easy_to_miss="Why engineers typically overlook this in design reviews"
   )
   ```

3. Test the pattern by running the app and submitting a document that should trigger it
4. Update `README.md` if you're adding to the pattern list

### Modifying Analysis Behavior

Prompts, LLM call logic, and the analysis pipeline are all in `app/analyzer.py`. Key methods:

- `_match_patterns()` — main pattern detection prompt
- `_extract_assumptions()` — implicit assumption extraction
- `_find_known_unknowns()` — information gap detection
- `_identify_ruled_out_risks()` — ruled-out risk detection
- `_generate_summary()` — executive summary generation (no LLM call)

### Adding a New LLM Provider

1. Add a new class in `app/llm.py` that inherits from `BaseLLMClient`
2. Implement `generate_json()`, `check_health()`, and `close()`
3. Add the provider to `get_llm_client()` and document the required env vars in `app/config.py`

### UI Changes

- HTML template: `app/templates/index.html`
- CSS styles: `app/static/styles.css`
- JavaScript: `app/static/script.js`
- Keep the UI clean and accessible
- Test on different screen sizes

---

## Areas for Contribution

### High Priority

- **New Failure Patterns** — More distributed-systems failure archetypes
- **Pattern Matching Improvements** — Better signal detection and scoring
- **UI/UX Enhancements** — Improve report readability and navigation
- **Error Handling** — Better error messages and recovery

### Medium Priority

- **Testing** — Unit tests and integration tests
- **Documentation** — Examples, tutorials, sample documents
- **Accessibility** — Keyboard navigation, screen reader support
- **Performance** — Optimize for large documents

### Nice to Have

- **History** — Save and revisit previous analyses
- **Multi-language Support** — Analysis for non-English documents
- **`.docx` Upload** — Support Word documents via python-docx
- **OCR for Scanned PDFs** — Extract text from image-only PDFs

---

## Questions?

- Open an issue with the `question` label
- Check existing issues and discussions
- Review the codebase to understand patterns

---

Thank you for contributing to Second Opinion!
