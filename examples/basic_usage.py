#!/usr/bin/env python3
"""
Basic usage examples for the Project Evaluator MCP Server
"""

import asyncio
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from project_evaluator_mcp.server import perplexity_client

async def example_single_evaluation():
    """Example: Evaluate a single project"""
    
    print("🔍 Example: Single Project Evaluation")
    print("-" * 40)
    
    project_synopsis = """
    An AI-powered personal finance assistant that uses machine learning 
    to analyze spending patterns, predict future expenses, and provide 
    personalized budgeting recommendations. The app integrates with 
    multiple bank accounts and credit cards to provide real-time 
    financial insights.
    """
    
    code_context = """
    Technologies: Python, FastAPI, React Native, PostgreSQL, 
    Machine Learning (scikit-learn, TensorFlow), Plaid API for 
    bank integration, JWT authentication, Docker deployment
    """
    
    result = await perplexity_client.analyze_project(project_synopsis, code_context)
    
    if result["success"]:
        print("✅ Evaluation successful!")
        print(f"📊 Analysis preview: {result['analysis'][:200]}...")
        print(f"🔢 Tokens used: {result.get('usage', {}).get('total_tokens', 'N/A')}")
    else:
        print(f"❌ Error: {result['error']}")

async def example_batch_evaluation():
    """Example: Evaluate multiple projects"""
    
    print("\n🔍 Example: Batch Project Evaluation")
    print("-" * 40)
    
    projects = [
        {
            "name": "Smart Home IoT Platform",
            "synopsis": "Centralized platform for managing IoT devices with AI-powered automation",
            "code_context": "Python, MQTT, React, MongoDB, machine learning"
        },
        {
            "name": "Blockchain Supply Chain",
            "synopsis": "Transparent supply chain tracking using blockchain technology",
            "code_context": "Solidity, Ethereum, Node.js, React, IPFS"
        },
        {
            "name": "AR Shopping Assistant",
            "synopsis": "Augmented reality app for virtual product try-ons and shopping",
            "code_context": "Unity, ARCore/ARKit, C#, Firebase, computer vision"
        }
    ]
    
    print(f"Evaluating {len(projects)} projects...")
    
    for i, project in enumerate(projects, 1):
        print(f"  {i}. {project['name']}")
        
        result = await perplexity_client.analyze_project(
            project["synopsis"], 
            project.get("code_context", "")
        )
        
        if result["success"]:
            print(f"     ✅ Success - {result.get('usage', {}).get('total_tokens', 0)} tokens")
        else:
            print(f"     ❌ Error: {result['error']}")

async def example_comparison():
    """Example: Compare two projects"""
    
    print("\n🔍 Example: Project Comparison")
    print("-" * 40)
    
    project1 = {
        "name": "Traditional E-commerce",
        "synopsis": "Standard online shopping platform with cart and payment processing",
        "code_context": "PHP, MySQL, jQuery, traditional web architecture"
    }
    
    project2 = {
        "name": "AI-Powered E-commerce",
        "synopsis": "Next-gen shopping platform with AI recommendations and voice commerce",
        "code_context": "Python, microservices, AI/ML, voice recognition, personalization"
    }
    
    print(f"Comparing: {project1['name']} vs {project2['name']}")
    
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
        print("✅ Both evaluations successful!")
        
        # Create comparison prompt
        comparison_prompt = f"""
        Compare these two e-commerce projects:
        
        PROJECT 1: {project1['synopsis']}
        PROJECT 2: {project2['synopsis']}
        
        Which approach is more innovative and why?
        """
        
        comparison = await perplexity_client.analyze_project(comparison_prompt)
        
        if comparison["success"]:
            print("✅ Comparison analysis complete!")
            print(f"📊 Total tokens used: {eval1.get('usage', {}).get('total_tokens', 0) + eval2.get('usage', {}).get('total_tokens', 0) + comparison.get('usage', {}).get('total_tokens', 0)}")
        else:
            print(f"❌ Comparison failed: {comparison['error']}")
    else:
        print("❌ Individual evaluations failed")

async def main():
    """Run all examples"""
    
    # Check API key
    if not os.getenv("PERPLEXITY_API_KEY"):
        print("❌ PERPLEXITY_API_KEY environment variable not set!")
        print("Please set your API key before running examples.")
        return
    
    print("🚀 Project Evaluator MCP Server - Usage Examples")
    print("=" * 60)
    
    try:
        await example_single_evaluation()
        await example_batch_evaluation()
        await example_comparison()
        
        print("\n" + "=" * 60)
        print("🎉 All examples completed successfully!")
        print("\nNext steps:")
        print("- Try modifying the project descriptions")
        print("- Add your own projects to evaluate")
        print("- Experiment with different code contexts")
        
    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
