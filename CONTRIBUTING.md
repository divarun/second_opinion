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
   - Environment details (OS, Python version, Ollama model)

### Contributing Code

#### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/your-username/second_opinion.git
cd second_opinion
```

#### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
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
- Add comments for complex logic
- Update documentation if needed
- Test your changes locally

#### 5. Test Your Changes

```bash
# Start the server
uvicorn app:app --reload

# Or use Python directly
python app.py
```

# Test with sample documents
# Verify the UI works correctly
# Check that error handling is appropriate
```

#### 6. Commit Your Changes

```bash
git add .
git commit -m "Description of your changes"
```

**Commit Message Guidelines:**
- Use clear, descriptive messages
- Start with a verb (Add, Fix, Update, Remove, etc.)
- Keep the first line under 72 characters
- Add more details in the body if needed

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

## Development Guidelines

### Code Style

- Follow PEP 8 Python style guide
- Use meaningful variable and function names
- Keep functions focused and small
- Add docstrings for public functions and classes

### Project Structure

- **`app/`**: Main application code
  - `api.py`: FastAPI routes
  - `prompts.py`: Centralized prompt library
  - `matcher.py`: Pattern matching logic
  - `models.py`: Pydantic data models
  - `static/`: UI templates and styles
- **`data/`**: Data files (failure patterns JSON)

### Adding New Failure Patterns

1. Edit `data/failure_patterns.json`
2. Follow the existing pattern structure:
   ```json
   {
     "id": "unique_pattern_id",
     "name": "Pattern Name",
     "signals": ["keyword1", "keyword2"],
     "trigger_conditions": ["condition1", "condition2"],
     "why_subtle": ["reason1", "reason2"],
     "impact_surface": ["impact1", "impact2"],
     "discussion_questions": ["question1", "question2"],
     "required_context": ["context1", "context2"],
     "safety_signals": ["mitigation1", "mitigation2"]
   }
   ```
3. Test the pattern with sample documents
4. Update documentation if needed

### Modifying Prompts

- All prompts are in `app/prompts.py`
- Follow the existing prompt structure
- Test with various document types
- Ensure prompts maintain the conservative, non-prescriptive tone

### UI Changes

- HTML templates: `app/templates/index.html`
- CSS styles: `app/static/styles.css`
- JS: `app/static/script.js`
- Keep the UI clean and accessible
- Test on different screen sizes

### Testing

Before submitting:
- Test with different document types (Markdown, plain text)
- Test file uploads
- Test with various failure patterns
- Verify error handling works correctly
- Check that the UI displays correctly

## Areas for Contribution

### High Priority

- **New Failure Patterns**: Add more distributed-systems failure archetypes
- **Pattern Matching Improvements**: Enhance signal detection and scoring
- **UI/UX Enhancements**: Improve report readability and navigation
- **Error Handling**: Better error messages and recovery

### Medium Priority

- **Documentation**: Improve README, add examples, create tutorials
- **Testing**: Add unit tests, integration tests
- **Performance**: Optimize pattern matching for large documents
- **Accessibility**: Improve keyboard navigation, screen reader support

### Nice to Have

- **Export Features**: Export reports as PDF, Markdown, or JSON
- **History**: Save and view previous analyses
- **Pattern Suggestions**: Suggest patterns based on document content
- **Multi-language Support**: Support for non-English documents

## Questions?

If you have questions about contributing:
- Open an issue with the `question` label
- Check existing issues and discussions
- Review the codebase to understand patterns

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Second Opinion! 🎉
