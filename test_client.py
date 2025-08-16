#!/usr/bin/env python3
"""
Test client for the Project Evaluator MCP Server
Run this to test the server functionality without Kiro
"""

import asyncio
import json
import os
import sys
from typing import Dict, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("💡 Tip: Install python-dotenv for .env file support: pip install python-dotenv")

# Import the server components
from project_evaluator_mcp.server import perplexity_client

async def test_evaluate_innovation():
    """Test the evaluate_innovation function"""
    
    synopsis = """
    A revolutionary AI-powered code review system that uses machine learning 
    to automatically detect bugs, security vulnerabilities, and performance 
    issues in real-time as developers write code. The system integrates 
    with popular IDEs and provides intelligent suggestions for code improvements.
    """
    
    code_context = "Uses Python, FastAPI, machine learning models, real-time analysis, IDE integration"
    
    print("🔄 Testing single project evaluation...")
    
    result = await perplexity_client.analyze_project(synopsis, code_context)
    
    if result["success"]:
        print("✅ Evaluation successful!")
        print(f"📊 Analysis Preview: {result['analysis'][:300]}...")
        print(f"🔢 Tokens used: {result.get('usage', {}).get('total_tokens', 'N/A')}")
        
        # Save full result to file
        with open('test_evaluation_result.md', 'w') as f:
            f.write(f"# Test Evaluation Result\n\n{result['analysis']}")
        print("💾 Full result saved to: test_evaluation_result.md")
        
    else:
        print(f"❌ Evaluation failed: {result['error']}")

async def test_batch_evaluation():
    """Test batch evaluation"""
    
    projects = [
        {
            "name": "AI Code Assistant",
            "synopsis": "AI-powered coding assistant that helps developers write better code with intelligent suggestions and auto-completion",
            "code_context": "Python, OpenAI API, VS Code extension, machine learning"
        },
        {
            "name": "Smart Documentation Generator", 
            "synopsis": "Automatically generates comprehensive documentation from code comments and structure using advanced NLP",
            "code_context": "NLP, Python, AST parsing, natural language processing"
        },
        {
            "name": "Blockchain Voting System",
            "synopsis": "Secure, transparent voting system using blockchain technology for elections and governance",
            "code_context": "Solidity, Ethereum, cryptography, web3, smart contracts"
        }
    ]
    
    print("🔄 Testing batch evaluation...")
    
    results = []
    total_tokens = 0
    
    for i, project in enumerate(projects, 1):
        print(f"   Evaluating {i}/{len(projects)}: {project['name']}")
        
        result = await perplexity_client.analyze_project(
            project["synopsis"], 
            project.get("code_context", "")
        )
        
        if result["success"]:
            print(f"   ✅ {project['name']}: Success")
            results.append(f"## {project['name']}\n{result['analysis']}\n")
            total_tokens += result.get('usage', {}).get('total_tokens', 0)
        else:
            print(f"   ❌ {project['name']}: {result['error']}")
            results.append(f"## {project['name']}\nError: {result['error']}\n")
    
    # Save batch results
    batch_report = f"""# Batch Evaluation Report

{chr(10).join(results)}

## Summary
- Projects evaluated: {len(projects)}
- Total tokens used: {total_tokens}
- Model: llama-3.1-sonar-large-128k-online
"""
    
    with open('test_batch_results.md', 'w') as f:
        f.write(batch_report)
    
    print(f"💾 Batch results saved to: test_batch_results.md")
    print(f"📊 Total tokens used: {total_tokens}")

async def test_comparison():
    """Test project comparison"""
    
    project1 = {
        "name": "AI Code Review",
        "synopsis": "Real-time AI-powered code review system with bug detection",
        "code_context": "Python, machine learning, real-time analysis"
    }
    
    project2 = {
        "name": "Traditional Code Review",
        "synopsis": "Manual code review process with human reviewers and checklists",
        "code_context": "Manual process, human reviewers, static analysis tools"
    }
    
    print("🔄 Testing project comparison...")
    
    # Get individual evaluations
    eval1 = await perplexity_client.analyze_project(
        project1["synopsis"], 
        project1.get("code_context", "")
    )
    
    eval2 = await perplexity_client.analyze_project(
        project2["synopsis"], 
        project2.get("code_context", "")
    )
    
    if eval1["success"] and eval2["success"]:
        # Generate comparison
        comparison_prompt = f"""
Compare these two project evaluations and provide a detailed comparison:

PROJECT 1 ({project1['name']}):
{eval1['analysis']}

PROJECT 2 ({project2['name']}):
{eval2['analysis']}

Provide a comprehensive comparison covering:
1. Innovation comparison
2. Novelty comparison  
3. Overall assessment
4. Recommendations for each project
5. Which project shows more promise and why
"""
        
        comparison_result = await perplexity_client.analyze_project(comparison_prompt)
        
        if comparison_result["success"]:
            print("✅ Comparison successful!")
            
            comparison_report = f"""# Project Comparison: {project1['name']} vs {project2['name']}

## Individual Evaluations

### {project1['name']}
{eval1['analysis']}

### {project2['name']}
{eval2['analysis']}

## Comparative Analysis
{comparison_result['analysis']}
"""
            
            with open('test_comparison_result.md', 'w') as f:
                f.write(comparison_report)
            
            print("💾 Comparison saved to: test_comparison_result.md")
        else:
            print(f"❌ Comparison failed: {comparison_result['error']}")
    else:
        print(f"❌ Individual evaluations failed")

def check_setup():
    """Check if everything is set up correctly"""
    
    print("🔍 Checking setup...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version >= (3, 8):
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"❌ Python {python_version.major}.{python_version.minor} (need 3.8+)")
        return False
    
    # Check API key
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if api_key:
        print(f"✅ Perplexity API key found (ends with: ...{api_key[-4:]})")
    else:
        print("❌ PERPLEXITY_API_KEY not found!")
        print("   Set it in your .env file or environment variables")
        return False
    
    # Check dependencies
    try:
        import httpx
        print("✅ httpx library available")
    except ImportError:
        print("❌ httpx not installed: pip install httpx")
        return False
    
    try:
        from project_evaluator_mcp.server import mcp, perplexity_client
        print("✅ MCP server components loaded")
    except ImportError as e:
        print(f"❌ Failed to import server components: {e}")
        print("   Try: pip install -e .")
        return False
    
    return True

async def main():
    """Main test function"""
    
    print("🚀 Project Evaluator MCP Server - Test Suite")
    print("=" * 60)
    
    # Check setup
    if not check_setup():
        print("\n❌ Setup check failed. Please fix the issues above.")
        return
    
    print("\n✅ Setup check passed!")
    print("=" * 60)
    
    try:
        # Test 1: Single evaluation
        print("\n📋 Test 1: Single Project Evaluation")
        print("-" * 40)
        await test_evaluate_innovation()
        
        print("\n📋 Test 2: Batch Evaluation")  
        print("-" * 40)
        await test_batch_evaluation()
        
        print("\n📋 Test 3: Project Comparison")
        print("-" * 40)
        await test_comparison()
        
        print("\n" + "=" * 60)
        print("🎉 All tests completed successfully!")
        print("\nGenerated files:")
        print("  - test_evaluation_result.md")
        print("  - test_batch_results.md") 
        print("  - test_comparison_result.md")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
