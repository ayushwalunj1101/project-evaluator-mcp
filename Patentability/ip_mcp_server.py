#!/usr/bin/env python3
"""
MCP Server for Intellectual Property Analysis
Provides patentability assessment and prior art search capabilities
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
import httpx
from mcp.server.fastmcp import FastMCP
from ip_analyzer.patentability import PatentabilityAnalyzer
#from ip_analyzer.prior_art import PriorArtSearcher
from ip_analyzer.prior_art_fixed import PriorArtSearcher
from config.settings import IP_CONFIG

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the MCP server instance
mcp = FastMCP("IP Analysis Server")

class IPAnalysisServer:
    """Main IP Analysis Server class"""
    
    def __init__(self):
        self.patentability_analyzer = PatentabilityAnalyzer()
        self.prior_art_searcher = PriorArtSearcher()
        logger.info("IP Analysis Server initialized")

# Initialize the IP analysis server
ip_server = IPAnalysisServer()

@mcp.tool()
async def assess_patentability(
    invention_description: str,
    technical_details: str = "",
    industry_sector: str = "",
    invention_type: str = "software"
) -> str:
    """
    Assess the patentability of an invention based on novelty, 
    non-obviousness, and utility criteria.
    
    Args:
        invention_description: Detailed description of the invention
        technical_details: Technical specifications and implementation details
        industry_sector: Industry/domain context (e.g., "healthcare", "fintech")
        invention_type: Type of invention ("software", "hardware", "method", "composition")
    
    Returns:
        Comprehensive patentability assessment report
    """
    
    if not invention_description.strip():
        return "Error: Invention description is required"
    
    try:
        logger.info(f"Starting patentability assessment for invention type: {invention_type}")
        
        # Prepare analysis data
        analysis_data = {
            "description": invention_description,
            "technical_details": technical_details,
            "industry_sector": industry_sector,
            "invention_type": invention_type
        }
        
        # Perform patentability analysis
        result = await ip_server.patentability_analyzer.analyze(analysis_data)
        
        # Format the response
        response = f"""# Patentability Assessment Report

## Executive Summary
**Overall Patentability Score**: {result['overall_score']}/100
**Recommendation**: {result['recommendation']}
**Confidence Level**: {result['confidence_level']}

## Detailed Analysis

### Novelty Assessment (Score: {result['novelty_score']}/100)
{result['novelty_analysis']}

### Non-Obviousness Evaluation (Score: {result['non_obviousness_score']}/100)
{result['non_obviousness_analysis']}

### Utility Assessment (Score: {result['utility_score']}/100)
{result['utility_analysis']}

### Subject Matter Eligibility
{result['subject_matter_analysis']}

## Key Strengths
{format_list(result['strengths'])}

## Potential Challenges
{format_list(result['challenges'])}

## Recommendations
{format_list(result['recommendations'])}

## Next Steps
{result['next_steps']}

---
*Analysis completed using IP Analysis MCP Server*
"""
        
        return response.strip()
        
    except Exception as e:
        logger.error(f"Error in patentability assessment: {e}")
        return f"Error analyzing patentability: {str(e)}"

@mcp.tool()
async def search_prior_art(
    search_query: str,
    technology_domain: str = "",
    search_scope: str = "comprehensive",
    max_results: int = 50,
    date_range: str = "all"
) -> str:
    """
    Search for prior art across multiple patent and literature databases.
    
    Args:
        search_query: Keywords and technical terms to search for
        technology_domain: Specific technology area (e.g., "AI", "blockchain", "biotech")
        search_scope: Search depth ("quick", "comprehensive", "exhaustive")
        max_results: Maximum number of results to return per database
        date_range: Time range ("1_year", "5_years", "10_years", "all")
    
    Returns:
        Comprehensive prior art search results with relevance analysis
    """
    
    if not search_query.strip():
        return "Error: Search query is required"
    
    try:
        logger.info(f"Starting prior art search with scope: {search_scope}")
        
        # Prepare search parameters
        search_params = {
            "query": search_query,
            "domain": technology_domain,
            "scope": search_scope,
            "max_results": max_results,
            "date_range": date_range
        }
        
        # Perform prior art search
        results = await ip_server.prior_art_searcher.search(search_params)
        
        # Format the response
        response = f"""# Prior Art Search Results

## Search Summary
**Query**: "{search_query}"
**Technology Domain**: {technology_domain or 'General'}
**Search Scope**: {search_scope}
**Total Results Found**: {results['total_results']}
**Databases Searched**: {', '.join(results['databases_searched'])}

## High-Relevance Patents ({len(results['high_relevance_patents'])})
{format_patent_results(results['high_relevance_patents'])}

## Medium-Relevance Patents ({len(results['medium_relevance_patents'])})
{format_patent_results(results['medium_relevance_patents'])}

## Academic Literature ({len(results['academic_papers'])})
{format_literature_results(results['academic_papers'])}

## Commercial Products ({len(results['commercial_products'])})
{format_product_results(results['commercial_products'])}

## Analysis Summary
### Patent Landscape Overview
{results['landscape_analysis']}

### Key Findings
{format_list(results['key_findings'])}

### Novelty Assessment
{results['novelty_gaps_identified']}

### Recommendations
{format_list(results['recommendations'])}

---
*Search completed using IP Analysis MCP Server*
"""
        
        return response.strip()
        
    except Exception as e:
        logger.error(f"Error in prior art search: {e}")
        return f"Error searching prior art: {str(e)}"

# Utility functions for formatting
def format_list(items: List[str]) -> str:
    """Format a list of items as markdown bullet points"""
    if not items:
        return "- None identified"
    return '\n'.join([f"- {item}" for item in items])

def format_patent_results(patents: List[Dict]) -> str:
    """Format patent search results"""
    if not patents:
        return "No patents found in this category."
    
    formatted = []
    for patent in patents[:10]:  # Limit to top 10
        formatted.append(f"""
### {patent['title']}
- **Patent Number**: {patent['patent_number']}
- **Publication Date**: {patent['pub_date']}
- **Relevance Score**: {patent['relevance_score']}/100
- **Inventor(s)**: {patent['inventors']}
- **Abstract**: {patent['abstract'][:200]}...
- **Key Claims**: {patent['key_claims']}
""")
    return '\n'.join(formatted)

def format_literature_results(papers: List[Dict]) -> str:
    """Format academic literature results"""
    if not papers:
        return "No academic papers found."
    
    formatted = []
    for paper in papers[:5]:  # Limit to top 5
        formatted.append(f"""
### {paper['title']}
- **Authors**: {paper['authors']}
- **Publication**: {paper['journal']} ({paper['year']})
- **Relevance Score**: {paper['relevance_score']}/100
- **Abstract**: {paper['abstract'][:150]}...
- **DOI**: {paper.get('doi', 'N/A')}
""")
    return '\n'.join(formatted)

def format_product_results(products: List[Dict]) -> str:
    """Format commercial product results"""
    if not products:
        return "No commercial products identified."
    
    formatted = []
    for product in products[:5]:
        formatted.append(f"""
### {product['name']}
- **Company**: {product['company']}
- **Launch Date**: {product.get('launch_date', 'Unknown')}
- **Relevance Score**: {product['relevance_score']}/100
- **Description**: {product['description'][:150]}...
- **Key Features**: {', '.join(product.get('key_features', []))}
""")
    return '\n'.join(formatted)

from fastapi import FastAPI, Request
import uvicorn
from ip_mcp_server import (  # or correct import for your analysis function
    assess_patentability,
    search_prior_art
)

if __name__ == "__main__":
    mcp.run() 
    
app = FastAPI()

@app.post("/evaluate")
async def evaluate(request: Request):
    data = await request.json()

    try:
        result = await assess_patentability(
            invention_description=data.get("invention_description", ""),
            technical_details=data.get("technical_details", ""),
            industry_sector=data.get("industry_sector", ""),
            invention_type=data.get("invention_type", "software")
        )
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7901)



