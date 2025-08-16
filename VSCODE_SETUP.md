# VS Code Setup Guide

This guide is for developers who want to clone and run the Project Evaluator MCP Server in VS Code without Kiro.

## 📋 Prerequisites

1. **Python 3.8+** installed on your system
2. **VS Code** with Python extension
3. **Git** installed
4. **Perplexity API Key** from [https://www.perplexity.ai/](https://www.perplexity.ai/)

## 🚀 Quick Setup

### Option 1: Automated Setup (Recommended)

```bash
git clone https://github.com/ayushwalunj1101/project-evaluator-mcp.git
cd project-evaluator-mcp
python setup_vscode.py
code .
```

### Option 2: Manual Setup

### 1. Clone the Repository

```bash
git clone https://github.com/ayushwalunj1101/project-evaluator-mcp.git
cd project-evaluator-mcp
```

### 2. Open in VS Code

```bash
code .
```

### 3. Set Up Python Environment

#### Option A: Using venv (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -e .
```

#### Option B: Using conda
```bash
conda create -n project-evaluator python=3.9
conda activate project-evaluator
pip install -e .
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# .env file
PERPLEXITY_API_KEY=your_perplexity_api_key_here
```

### 5. Install Additional Dependencies for Standalone Use

```bash
pip install python-dotenv
```

## 🔧 Running the Server

### Method 1: Direct Python Execution

```bash
# Set environment variable (if not using .env)
export PERPLEXITY_API_KEY=your_key_here  # macOS/Linux
set PERPLEXITY_API_KEY=your_key_here     # Windows

# Run the server
python src/project_evaluator_mcp/server.py
```

### Method 2: Using the Package Entry Point

```bash
project-evaluator-mcp
```

### Method 3: As a Module

```bash
python -m project_evaluator_mcp.server
```

## 🧪 Testing the Server

### Use the Included Test Client

The repository includes a comprehensive test client (`test_client.py`) that you can run directly:

```python
#!/usr/bin/env python3
"""
Test client for the Project Evaluator MCP Server
"""

import asyncio
import json
import os
from typing import Dict, Any

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import the server components
from src.project_evaluator_mcp.server import perplexity_client

async def test_evaluate_innovation():
    """Test the evaluate_innovation function"""
    
    synopsis = """
    A revolutionary AI-powered code review system that uses machine learning 
    to automatically detect bugs, security vulnerabilities, and performance 
    issues in real-time as developers write code.
    """
    
    code_context = "Uses Python, FastAPI, machine learning models, real-time analysis"
    
    print("🔄 Testing project evaluation...")
    
    result = await perplexity_client.analyze_project(synopsis, code_context)
    
    if result["success"]:
        print("✅ Evaluation successful!")
        print(f"📊 Analysis: {result['analysis'][:200]}...")
        print(f"🔢 Tokens used: {result.get('usage', {}).get('total_tokens', 'N/A')}")
    else:
        print(f"❌ Evaluation failed: {result['error']}")

async def test_batch_evaluation():
    """Test batch evaluation"""
    
    projects = [
        {
            "name": "AI Code Assistant",
            "synopsis": "AI-powered coding assistant that helps developers write better code",
            "code_context": "Python, OpenAI API, VS Code extension"
        },
        {
            "name": "Smart Documentation Generator", 
            "synopsis": "Automatically generates documentation from code comments",
            "code_context": "NLP, Python, AST parsing"
        }
    ]
    
    print("🔄 Testing batch evaluation...")
    
    for project in projects:
        result = await perplexity_client.analyze_project(
            project["synopsis"], 
            project.get("code_context", "")
        )
        
        if result["success"]:
            print(f"✅ {project['name']}: Success")
        else:
            print(f"❌ {project['name']}: {result['error']}")

async def main():
    """Main test function"""
    
    # Check if API key is set
    if not os.getenv("PERPLEXITY_API_KEY"):
        print("❌ PERPLEXITY_API_KEY not set!")
        print("Please set it in your .env file or environment variables")
        return
    
    print("🚀 Starting MCP Server Tests")
    print("=" * 50)
    
    # Test individual evaluation
    await test_evaluate_innovation()
    
    print("\n" + "=" * 50)
    
    # Test batch evaluation
    await test_batch_evaluation()
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    asyncio.run(main())
```

### Run the Test

```bash
python test_client.py
```

### Try the Examples

Run the included examples to see different usage patterns:

```bash
python examples/basic_usage.py
```

## 🔌 Using with Other MCP Clients

### Claude Desktop Configuration

Add to your Claude Desktop config:

```json
{
  "mcpServers": {
    "project-evaluator": {
      "command": "python",
      "args": ["/path/to/project-evaluator-mcp/src/project_evaluator_mcp/server.py"],
      "env": {
        "PERPLEXITY_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### Continue.dev Configuration

Add to your Continue config:

```json
{
  "mcpServers": [
    {
      "name": "project-evaluator",
      "command": "python",
      "args": ["/path/to/project-evaluator-mcp/src/project_evaluator_mcp/server.py"],
      "env": {
        "PERPLEXITY_API_KEY": "your_api_key_here"
      }
    }
  ]
}
```

## 🛠️ Development Workflow

### 1. VS Code Extensions (Recommended)

Install these VS Code extensions:
- Python
- Python Debugger
- GitLens
- Thunder Client (for API testing)

### 2. Debug Configuration

Create `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Run MCP Server",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/src/project_evaluator_mcp/server.py",
            "console": "integratedTerminal",
            "envFile": "${workspaceFolder}/.env"
        },
        {
            "name": "Test Client",
            "type": "python", 
            "request": "launch",
            "program": "${workspaceFolder}/test_client.py",
            "console": "integratedTerminal",
            "envFile": "${workspaceFolder}/.env"
        }
    ]
}
```

### 3. Tasks Configuration

Create `.vscode/tasks.json`:

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Install Dependencies",
            "type": "shell",
            "command": "pip",
            "args": ["install", "-e", "."],
            "group": "build"
        },
        {
            "label": "Run Tests",
            "type": "shell", 
            "command": "python",
            "args": ["test_client.py"],
            "group": "test"
        },
        {
            "label": "Start MCP Server",
            "type": "shell",
            "command": "python", 
            "args": ["src/project_evaluator_mcp/server.py"],
            "group": "build"
        }
    ]
}
```

## 📝 Creating Your Own Tools

### Add a New Tool

1. Open `src/project_evaluator_mcp/server.py`
2. Add a new function with the `@mcp.tool()` decorator:

```python
@mcp.tool()
async def analyze_market_potential(synopsis: str, target_market: str = "") -> str:
    """Analyze the market potential of a project"""
    
    prompt = f"""
    Analyze the market potential for this project:
    
    PROJECT: {synopsis}
    TARGET MARKET: {target_market}
    
    Provide:
    1. Market size estimation
    2. Competition analysis  
    3. Revenue potential
    4. Market entry strategy
    """
    
    result = await perplexity_client.analyze_project(prompt)
    
    if result["success"]:
        return f"# Market Analysis\n\n{result['analysis']}"
    else:
        return f"Error: {result['error']}"
```

### Test Your New Tool

Add to `test_client.py`:

```python
# Import your new function
from src.project_evaluator_mcp.server import analyze_market_potential

# Test it
result = await analyze_market_potential(
    "AI-powered fitness app", 
    "Health and wellness market"
)
print(result)
```

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   pip install -e .
   ```

2. **API Key Not Found**
   ```bash
   # Check your .env file exists and has the right key
   cat .env
   ```

3. **Module Not Found**
   ```bash
   # Make sure you're in the right directory
   pwd
   # Should show: /path/to/project-evaluator-mcp
   ```

4. **Permission Errors**
   ```bash
   # On macOS/Linux, you might need:
   chmod +x src/project_evaluator_mcp/server.py
   ```

### Debug Mode

Run with debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📚 Next Steps

1. **Customize the prompts** in `server.py` for your specific needs
2. **Add new evaluation criteria** or scoring methods
3. **Create a web interface** using FastAPI or Streamlit
4. **Add database storage** for evaluation history
5. **Implement caching** to reduce API costs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

Happy coding! 🚀
