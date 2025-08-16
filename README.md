# Project Evaluator MCP Server

A Model Context Protocol (MCP) server that provides AI-powered project innovation and novelty evaluation using Perplexity AI.

## Features

- **Single Project Evaluation**: Analyze innovation and novelty of individual projects
- **Batch Evaluation**: Evaluate multiple projects simultaneously  
- **Project Comparison**: Head-to-head comparison of two projects
- **Detailed Scoring**: Innovation, novelty, and overall scores (0-100)
- **Comprehensive Analysis**: Strengths, weaknesses, and recommendations

## Installation

### Prerequisites

1. **uv/uvx**: Install from [https://docs.astral.sh/uv/getting-started/installation/](https://docs.astral.sh/uv/getting-started/installation/)
2. **Perplexity API Key**: Get from [https://www.perplexity.ai/](https://www.perplexity.ai/)

### Install via uvx

```bash
uvx --from git+https://github.com/ayushwalunj1101/project-evaluator-mcp.git project-evaluator-mcp
```

## Configuration

### 1. Set Environment Variable

```bash
# Windows
set PERPLEXITY_API_KEY=your_api_key_here

# macOS/Linux  
export PERPLEXITY_API_KEY=your_api_key_here
```

### 2. Configure in Kiro

Add to your `.kiro/settings/mcp.json`:

```json
{
  "mcpServers": {
    "project-evaluator": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/ayushwalunj1101/project-evaluator-mcp.git", "project-evaluator-mcp"],
      "env": {
        "PERPLEXITY_API_KEY": "your_api_key_here"
      },
      "disabled": false,
      "autoApprove": [
        "evaluate_innovation",
        "batch_evaluate",
        "compare_projects"
      ]
    }
  }
}
```

## Usage

### Single Project Evaluation

```python
# In Kiro chat
"Evaluate the innovation of my blockchain voting system project"
```

### Batch Evaluation

```python
# Evaluate multiple projects at once
"Run a batch evaluation on these 3 startup ideas"
```

### Project Comparison

```python
# Compare two projects
"Compare my AI assistant vs traditional chatbot approach"
```

## Tools Available

### `evaluate_innovation`
- **Parameters**: `synopsis` (required), `code_context` (optional), `project_name` (optional)
- **Returns**: Detailed innovation and novelty analysis with scores

### `batch_evaluate` 
- **Parameters**: `projects` (list of project dictionaries)
- **Returns**: Batch evaluation report with summary statistics

### `compare_projects`
- **Parameters**: `project1`, `project2` (project dictionaries)
- **Returns**: Head-to-head comparison analysis

## Example Output

```markdown
# Innovation & Novelty Evaluation: My AI Project

## Analysis Results

**INNOVATION SCORE: 85/100**
**NOVELTY SCORE: 78/100** 
**OVERALL SCORE: 82/100**

### STRENGTHS
- Novel approach to problem solving
- Strong technical implementation
- Clear market potential

### WEAKNESSES  
- Limited scalability considerations
- Competitive landscape challenges

### RECOMMENDATIONS
- Focus on unique differentiators
- Develop scalability roadmap
- Conduct market validation

## API Usage
- Tokens used: 1,234
- Model: llama-3.1-sonar-large-128k-online
```

## Development

### VS Code Setup (No Kiro Required)

For developers who want to use this without Kiro, see the detailed [VS Code Setup Guide](VSCODE_SETUP.md).

**Quick Start:**
```bash
git clone https://github.com/ayushwalunj1101/project-evaluator-mcp.git
cd project-evaluator-mcp
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -e .
cp .env.example .env  # Add your Perplexity API key
python test_client.py  # Test the server
```

### Local Development

```bash
git clone https://github.com/ayushwalunj1101/project-evaluator-mcp.git
cd project-evaluator-mcp
pip install -e .
export PERPLEXITY_API_KEY=your_key
python -m project_evaluator_mcp.server
```

### Testing

```bash
# Test the server with the included test client
python test_client.py

# Run usage examples
python examples/basic_usage.py

# Or test individual components
python src/project_evaluator_mcp/server.py
```

### Docker Support

Run with Docker for isolated environment:

```bash
# Build and run
docker-compose up mcp-server

# Development mode with live reload
docker-compose --profile dev up mcp-dev
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

- **Issues**: [GitHub Issues](https://github.com/ayushwalunj1101/project-evaluator-mcp/issues)
- **Documentation**: [GitHub Wiki](https://github.com/ayushwalunj1101/project-evaluator-mcp/wiki)
