# Changelog

All notable changes to the Project Evaluator MCP Server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Nothing yet

### Changed
- Nothing yet

### Fixed
- Nothing yet

## [1.0.0] - 2025-01-16

### Added
- Initial release of Project Evaluator MCP Server
- Three core MCP tools:
  - `evaluate_innovation` - Single project evaluation
  - `batch_evaluate` - Multiple project evaluation
  - `compare_projects` - Head-to-head project comparison
- Perplexity AI integration for comprehensive analysis
- Detailed scoring system (Innovation, Novelty, Overall scores 0-100)
- Comprehensive documentation and setup guides
- VS Code development environment support
- GitHub Actions CI/CD pipeline
- Professional project structure with proper packaging

### Features
- **AI-Powered Analysis**: Uses Perplexity's sonar model for research-backed evaluations
- **Detailed Reporting**: Provides strengths, weaknesses, and recommendations
- **Multiple Installation Methods**: uvx for Kiro users, local setup for VS Code
- **Environment Variable Configuration**: Secure API key management
- **Comprehensive Testing**: Included test client for validation
- **Cross-Platform Support**: Works on Windows, macOS, and Linux

### Documentation
- Complete README with installation and usage instructions
- VS Code setup guide for local development
- Contributing guidelines for open source collaboration
- Security policy for responsible disclosure
- Issue templates for bug reports and feature requests

### Development Tools
- VS Code configuration with debug support
- Automated testing and linting
- Code formatting with Black
- Type hints and proper documentation
- Professional Python package structure

## [0.1.0] - 2025-01-16

### Added
- Initial development version
- Basic MCP server structure
- Perplexity API integration prototype

---

## Release Notes

### Version 1.0.0 Highlights

This is the first stable release of the Project Evaluator MCP Server! 🎉

**Key Features:**
- **Professional AI Analysis**: Leverages Perplexity AI for comprehensive project evaluation
- **Multiple Evaluation Modes**: Single, batch, and comparison analysis
- **Developer-Friendly**: Works with Kiro, VS Code, and other MCP clients
- **Open Source**: MIT licensed with full source code available

**Getting Started:**
```bash
# For Kiro users
uvx --from git+https://github.com/ayushwalunj1101/project-evaluator-mcp.git project-evaluator-mcp

# For VS Code users
git clone https://github.com/ayushwalunj1101/project-evaluator-mcp.git
cd project-evaluator-mcp
pip install -e .
```

**What's Next:**
- Additional evaluation metrics
- Performance optimizations
- Web interface development
- Integration with more MCP clients

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute to this project.

## Security

See [SECURITY.md](SECURITY.md) for information about reporting security vulnerabilities.
