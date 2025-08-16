#!/usr/bin/env python3
"""
MCP Server for Project Innovation and Novelty Evaluation
Updated for global distribution via GitHub + uvx
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional
import httpx
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Perplexity API configuration - now uses environment variable
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"

if not PERPLEXITY_API_KEY:
    logger.warning("PERPLEXITY_API_KEY environment variable not set. Server will not function properly.")

# Create the MCP server instance
mcp = FastMCP("Project Evaluation Server")

class PerplexityClient:
    """Client for interacting with Perplexity API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    async def analyze_project(self, synopsis: str, code_context: str = "") -> Dict[str, Any]:
        """Analyze project for innovation and novelty using Perplexity"""
        if not self.api_key:
            return {
                "success": False,
                "error": "Perplexity API key not configured. Please set PERPLEXITY_API_KEY environment variable."
            }
            
        prompt = f"""
As an expert technology evaluator, analyze the following project for innovation and novelty:

PROJECT SYNOPSIS:
{synopsis}

{f"CODE CONTEXT: {code_context}" if code_context else ""}

Please provide a comprehensive evaluation covering:

1. INNOVATION SCORE (0-100): How innovative is this project compared to existing solutions?
2. NOVELTY SCORE (0-100): How novel are the approaches and techniques used?
3. OVERALL SCORE (0-100): Combined assessment of the project's value

For each score, provide detailed reasoning including:
- Key innovative aspects
- Novel techniques or approaches
- Comparison with existing solutions
- Technical complexity and creativity
- Market potential and impact

Also identify:
- STRENGTHS: Top 3-5 strongest aspects
- WEAKNESSES: Areas that could be improved
- RECOMMENDATIONS: Specific suggestions for enhancement

Format your response as a structured analysis with clear sections.
"""

        payload = {
            "model": "sonar",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert technology evaluator specializing in assessing innovation and novelty in software projects. Provide detailed, objective analysis with specific scores and actionable insights."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 2000,
            "temperature": 0.2,
            "stream": False
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    PERPLEXITY_API_URL,
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
                
                return {
                    "success": True,
                    "analysis": result["choices"][0]["message"]["content"],
                    "usage": result.get("usage", {})
                }
            except httpx.HTTPError as e:
                logger.error(f"HTTP error occurred: {e}")
                return {
                    "success": False,
                    "error": f"HTTP error: {str(e)}"
                }
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                return {
                    "success": False,
                    "error": f"Unexpected error: {str(e)}"
                }

# Create Perplexity client instance
perplexity_client = PerplexityClient(PERPLEXITY_API_KEY)

@mcp.tool()
async def evaluate_innovation(synopsis: str, code_context: str = "", project_name: str = "Unnamed Project") -> str:
    """Evaluate a project's innovation and novelty based on synopsis and optional code context"""
    
    if not synopsis:
        return "Error: Synopsis is required"
    
    # Analyze with Perplexity
    result = await perplexity_client.analyze_project(synopsis, code_context)
    
    if not result["success"]:
        return f"Error analyzing project: {result['error']}"
    
    # Format response
    response = f"""# Innovation & Novelty Evaluation: {project_name}

## Analysis Results

{result['analysis']}

## API Usage

- Tokens used: {result.get('usage', {}).get('total_tokens', 'N/A')}
- Model: llama-3.1-sonar-large-128k-online

---

*Evaluation completed using Perplexity API*
"""
    
    return response.strip()

@mcp.tool()
async def batch_evaluate(projects: List[Dict[str, str]]) -> str:
    """Evaluate multiple projects in batch"""
    
    if not projects:
        return "Error: No projects provided"
    
    results = []
    total_tokens = 0
    
    for i, project in enumerate(projects, 1):
        name = project.get("name", f"Project {i}")
        synopsis = project.get("synopsis", "")
        code_context = project.get("code_context", "")
        
        if not synopsis:
            results.append(f"## {name}\nError: Synopsis is required\n")
            continue
        
        result = await perplexity_client.analyze_project(synopsis, code_context)
        
        if result["success"]:
            results.append(f"## {name}\n{result['analysis']}\n")
            total_tokens += result.get('usage', {}).get('total_tokens', 0)
        else:
            results.append(f"## {name}\nError: {result['error']}\n")
    
    response = f"""# Batch Innovation & Novelty Evaluation

{chr(10).join(results)}

## Summary

- Projects evaluated: {len(projects)}
- Total tokens used: {total_tokens}
- Model: llama-3.1-sonar-large-128k-online

---

*Batch evaluation completed using Perplexity API*
"""
    
    return response.strip()

@mcp.tool()
async def compare_projects(project1: Dict[str, str], project2: Dict[str, str]) -> str:
    """Compare innovation and novelty between two projects"""
    
    # Get individual evaluations
    eval1 = await perplexity_client.analyze_project(
        project1.get("synopsis", ""),
        project1.get("code_context", "")
    )
    
    eval2 = await perplexity_client.analyze_project(
        project2.get("synopsis", ""),
        project2.get("code_context", "")
    )
    
    if not eval1["success"] or not eval2["success"]:
        return f"Error in evaluation: {eval1.get('error', '')} {eval2.get('error', '')}"
    
    # Generate comparison
    comparison_prompt = f"""
Compare these two project evaluations and provide a detailed comparison:

PROJECT 1 ({project1.get('name', 'Project 1')}):
{eval1['analysis']}

PROJECT 2 ({project2.get('name', 'Project 2')}):
{eval2['analysis']}

Provide a comprehensive comparison covering:
1. Innovation comparison
2. Novelty comparison
3. Overall assessment
4. Recommendations for each project
5. Which project shows more promise and why
"""
    
    comparison_result = await perplexity_client.analyze_project(comparison_prompt)
    
    response = f"""# Project Comparison: {project1.get('name', 'Project 1')} vs {project2.get('name', 'Project 2')}

## Individual Evaluations

### {project1.get('name', 'Project 1')}

{eval1['analysis']}

### {project2.get('name', 'Project 2')}

{eval2['analysis']}

## Comparative Analysis

{comparison_result.get('analysis', 'Comparison analysis failed') if comparison_result['success'] else 'Error in comparison analysis'}

---

*Comparison completed using Perplexity API*
"""
    
    return response.strip()

def main():
    """Main entry point for the MCP server"""
    mcp.run()

if __name__ == "__main__":
    main()
