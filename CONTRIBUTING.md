# Contributing to MindGuardian AI

## Welcome Contributors!

MindGuardian AI is an open research project. We welcome contributions from:
- Academic researchers
- Privacy & security specialists
- ML/AI engineers
- Frontend developers
- UX/Design professionals
- Documentation writers

---

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. All contributors must adhere to our Code of Conduct:

- **Respect**: Treat all contributors with dignity and respect
- **Inclusion**: Welcome diverse perspectives and backgrounds
- **Collaboration**: Foster constructive dialogue and feedback
- **Accountability**: Hold ourselves to high ethical standards
- **Transparency**: Be open about limitations and uncertainties

### Unacceptable Behavior
- Harassment, discrimination, or abuse
- Misrepresentation of research findings
- Violation of privacy or security
- Conflict of interest without disclosure

---

## How to Contribute

### 1. Report Issues

Issues help us track bugs, feature requests, and research gaps.

**Bug Reports Should Include:**
```
- Description of the issue
- Steps to reproduce
- Expected vs. actual behavior
- Environment (OS, Python version, browser)
- Relevant logs or screenshots
```

**Feature Requests Should Include:**
```
- Problem statement
- Proposed solution
- Alternative approaches considered
- Potential impact and risks
```

### 2. Submit Pull Requests

**Before Starting:**
1. Check existing issues/PRs to avoid duplication
2. Open an issue to discuss major changes first
3. Fork the repository
4. Create a feature branch: `git checkout -b feat/your-feature-name`

**PR Guidelines:**

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Enhancement
- [ ] Documentation
- [ ] Refactoring

## Related Issue
Closes #(issue number)

## Changes Made
- Point 1
- Point 2
- Point 3

## Testing
Describe testing performed.

## Validation Checklist
- [ ] Code follows style guide
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No breaking changes
- [ ] Tested locally
```

### 3. Research Contributions

**For AI/ML improvements:**
- Submit research proposal as issue
- Include methodology, expected improvements, validation plan
- Discuss with maintainers before implementation
- Provide experimental results with error bars
- Include reproducibility details

**For privacy/security research:**
- Responsible disclosure: Report vulnerabilities privately first
- Allow 90 days for fixes before public disclosure
- Include proof-of-concept if applicable
- Suggest mitigation strategies

---

## Development Workflow

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/revanthvenkat123401/Mindguardian-AI-.git
cd Mindguardian-AI-

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt
pip install -r backend/requirements-dev.txt  # For development

# Setup pre-commit hooks
pre-commit install

# Run tests
pytest tests/ -v
```

### Code Style

**Python:**
```bash
# Format code
black backend/

# Lint code
flake8 backend/ --max-line-length=100

# Type checking
mypy backend/

# Security scanning
bandit -r backend/
```

**JavaScript:**
```bash
# Format
prettier --write js/

# Lint
eslint js/
```

### Testing Requirements

**Unit Tests:**
```bash
pytest tests/unit/ -v --cov=backend --cov-report=html
```

**Integration Tests:**
```bash
pytest tests/integration/ -v
```

**Expected Coverage:**
- Backend: ≥ 80%
- Critical paths: 95%+
- Frontend: ≥ 70%

### Commit Messages

Follow conventional commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `style:` Code style (formatting, missing semicolons)
- `refactor:` Code refactoring
- `perf:` Performance improvement
- `test:` Test additions/modifications
- `chore:` Build process, dependencies
- `research:` Research-related changes

**Example:**
```
feat(vision-engine): add micro-expression detection

Implement microsaccade-based emotion detection using
Facial Action Unit framework. Improves burnout detection
accuracy by 12% on test set.

Closes #42
```

---

## Project Structure

```
Mindguardian-AI-/
├── backend/               # FastAPI backend
│   ├── routes/           # API endpoints
│   ├── ai_pipeline/      # ML components
│   ├── tests/            # Backend tests
│   └── requirements.txt
├── frontend/             # Web interface
│   ├── js/              # JavaScript modules
│   ├── css/             # Stylesheets
│   └── tests/           # Frontend tests
├── docs/                 # Documentation
├── .github/workflows/    # CI/CD pipelines
└── RESEARCH_FOUNDATION.md # Research specs
```

---

## Documentation Standards

### Code Documentation

**Python Docstrings (Google style):**
```python
def analyze_facial_expression(frame: np.ndarray) -> Dict[str, float]:
    """Analyze facial expression from video frame.
    
    Detects emotions and facial action units using
    DeepFace and FACS models. Results are locally cached.
    
    Args:
        frame: Input video frame (BGR format)
        
    Returns:
        Dictionary containing:
            - emotion (str): Primary emotion detected
            - emotion_scores (Dict): Confidence scores
            - action_units (Dict): FACS activation levels
            - confidence (float): Overall detection confidence
            
    Raises:
        ValueError: If frame dimensions invalid
        RuntimeError: If model fails to load
        
    Example:
        >>> results = analyze_facial_expression(frame)
        >>> print(results['emotion'])
        'neutral'
    """
```

### README Files

Each major component should have README explaining:
1. Purpose and scope
2. Key concepts
3. API/usage examples
4. Configuration options
5. Known limitations
6. Performance benchmarks (if applicable)

---

## Review Process

### PR Review Checklist

Maintainers will review PRs for:

- **Functionality**
  - [ ] Does it solve the stated problem?
  - [ ] Are edge cases handled?
  - [ ] Does it break existing functionality?

- **Code Quality**
  - [ ] Follows style guide
  - [ ] Well-documented
  - [ ] No unnecessary complexity
  - [ ] Appropriate error handling

- **Testing**
  - [ ] Unit tests added
  - [ ] Tests pass locally and in CI
  - [ ] Coverage maintained or improved

- **Security**
  - [ ] No hardcoded secrets
  - [ ] Input validation present
  - [ ] No security vulnerabilities

- **Documentation**
  - [ ] README updated
  - [ ] API docs updated
  - [ ] Changelog updated

- **Research Quality** (for ML changes)
  - [ ] Methodology clearly explained
  - [ ] Results reproducible
  - [ ] Validation metrics reported
  - [ ] Limitations acknowledged

### Timeline

- **Initial review**: 48 hours
- **Feedback response**: 72 hours (contributor)
- **Final approval**: 24 hours after all feedback addressed
- **Merge**: Upon approval and CI passing

---

## Release Process

### Version Numbering

Semantic versioning: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes, significant new research findings
- **MINOR**: New features, model improvements, new capabilities
- **PATCH**: Bug fixes, documentation updates

### Release Checklist

```
[ ] All tests passing
[ ] Documentation updated
[ ] CHANGELOG.md updated
[ ] Version number bumped
[ ] Research summary added (if applicable)
[ ] GitHub release notes created
[ ] Announcement posted
```

---

## Compensation & Recognition

### Attribution

Contributors will be:
- Listed in CONTRIBUTORS.md
- Credited in release notes
- Mentioned in research publications (if applicable)

### Major Contribution Recognition

Contributors with significant contributions may be invited to:
- Co-author research papers
- Join steering committee
- Lead research initiatives
- Present findings at conferences

---

## Questions?

- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and ideas
- **Email**: Open an issue for contact information
- **Paper**: See RESEARCH_FOUNDATION.md for academic details

---

**Thank you for contributing to MindGuardian AI! Together, we're building privacy-first AI for cognitive health.**
