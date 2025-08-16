# Contributing to Project Evaluator MCP Server

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Git
- Perplexity API key (for testing)

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/yourusername/project-evaluator-mcp.git
   cd project-evaluator-mcp
   ```

2. **Set up development environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -e .
   pip install python-dotenv pytest black flake8
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Add your PERPLEXITY_API_KEY to .env
   ```

4. **Test the setup**
   ```bash
   python test_client.py
   ```

## 📋 How to Contribute

### Reporting Issues

1. **Check existing issues** first to avoid duplicates
2. **Use issue templates** when available
3. **Provide clear reproduction steps**
4. **Include environment details** (Python version, OS, etc.)

### Suggesting Features

1. **Open an issue** with the "enhancement" label
2. **Describe the use case** and expected behavior
3. **Consider implementation complexity**
4. **Be open to discussion** and feedback

### Code Contributions

#### 1. **Create a Feature Branch**
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

#### 2. **Make Your Changes**
- Follow the existing code style
- Add tests for new functionality
- Update documentation as needed
- Keep commits focused and atomic

#### 3. **Code Quality Checks**
```bash
# Format code
black src/ test_client.py

# Lint code
flake8 src/ test_client.py

# Run tests
python test_client.py
```

#### 4. **Commit Guidelines**
Use clear, descriptive commit messages:
```bash
# Good examples:
git commit -m "Add batch evaluation timeout handling"
git commit -m "Fix API key validation in server startup"
git commit -m "Update README with new installation instructions"

# Avoid:
git commit -m "fix stuff"
git commit -m "updates"
```

#### 5. **Submit Pull Request**
1. **Push your branch** to your fork
2. **Create a pull request** against the main branch
3. **Fill out the PR template** completely
4. **Link related issues** using keywords (fixes #123)
5. **Wait for review** and address feedback

## 🔧 Development Guidelines

### Code Style

- **Follow PEP 8** Python style guidelines
- **Use Black** for code formatting (line length: 88)
- **Use type hints** where appropriate
- **Write docstrings** for functions and classes
- **Keep functions focused** and single-purpose

### Testing

- **Test new features** thoroughly
- **Include edge cases** in testing
- **Use the test client** for integration testing
- **Mock external API calls** when appropriate

### Documentation

- **Update README.md** for user-facing changes
- **Update VSCODE_SETUP.md** for development changes
- **Add docstrings** to new functions
- **Include examples** in documentation

## 🎯 Areas for Contribution

### High Priority
- **Error handling improvements**
- **Additional evaluation metrics**
- **Performance optimizations**
- **Better test coverage**

### Medium Priority
- **New MCP tools** (market analysis, technical feasibility, etc.)
- **Configuration options** for evaluation criteria
- **Caching mechanisms** to reduce API costs
- **Logging improvements**

### Nice to Have
- **Web interface** using FastAPI or Streamlit
- **Database integration** for evaluation history
- **Export formats** (PDF, JSON, etc.)
- **Integration examples** with other MCP clients

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Python version** and operating system
2. **Steps to reproduce** the issue
3. **Expected vs actual behavior**
4. **Error messages** or logs
5. **Environment details** (API key status, dependencies)

### Bug Report Template
```markdown
**Environment:**
- Python version: 3.x.x
- OS: Windows/macOS/Linux
- MCP Server version: x.x.x

**Steps to Reproduce:**
1. Step one
2. Step two
3. Step three

**Expected Behavior:**
What should happen

**Actual Behavior:**
What actually happens

**Error Messages:**
```
Paste any error messages here
```

**Additional Context:**
Any other relevant information
```

## 📝 Pull Request Guidelines

### PR Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Tests added/updated for changes
- [ ] Documentation updated if needed
- [ ] No breaking changes (or clearly documented)
- [ ] Commit messages are clear and descriptive

### PR Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tested locally with test_client.py
- [ ] Added new tests for functionality
- [ ] All existing tests pass

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes

## Related Issues
Fixes #(issue number)
```

## 🤝 Code of Conduct

### Our Standards
- **Be respectful** and inclusive
- **Welcome newcomers** and help them learn
- **Focus on constructive feedback**
- **Assume good intentions**
- **Respect different viewpoints**

### Unacceptable Behavior
- Harassment or discrimination
- Trolling or insulting comments
- Personal attacks
- Publishing private information
- Spam or off-topic content

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Email**: ayushwalunj1@gmail.com for private matters

## 🎉 Recognition

Contributors will be:
- **Listed in CONTRIBUTORS.md**
- **Mentioned in release notes**
- **Credited in documentation**

Thank you for contributing to the Project Evaluator MCP Server! 🚀
