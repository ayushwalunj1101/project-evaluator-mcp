#!/usr/bin/env python3
"""
IP Analysis MCP Client for testing and integration
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Callable, Awaitable

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class IPAnalysisRequest:
    """Container for IP analysis request data"""
    invention_description: str
    technical_details: str = ""
    industry_sector: str = ""
    invention_type: str = "software"

class IPAnalysisClient:
    """Client for interacting with the IP Analysis MCP Server"""
    
    def __init__(self, server_script_path: str = "ip_mcp_server.py"):
        self.server_script_path = server_script_path
    
    async def _execute_with_server(self, operation: Callable[[ClientSession], Awaitable[Any]]) -> Any:
        """Execute an operation with the MCP server"""
        server_params = StdioServerParameters(
            command="python",
            args=[self.server_script_path],
        )
        
        try:
            async with stdio_client(server_params) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    return await operation(session)
        except Exception as e:
            logger.error(f"Error in server operation: {e}")
            raise
    
    async def assess_patentability(self, request: IPAnalysisRequest) -> str:
        """Assess patentability of an invention"""
        async def _op(session: ClientSession):
            result = await session.call_tool(
                "assess_patentability",
                {
                    "invention_description": request.invention_description,
                    "technical_details": request.technical_details,
                    "industry_sector": request.industry_sector,
                    "invention_type": request.invention_type,
                }
            )
            
            if result.content and len(result.content) > 0:
                return result.content[0].text
            else:
                return "No patentability assessment received"
        
        return await self._execute_with_server(_op)
    
    async def search_prior_art(
        self, 
        search_query: str,
        technology_domain: str = "",
        search_scope: str = "comprehensive",
        max_results: int = 50,
        date_range: str = "all"
    ) -> str:
        """Search for prior art"""
        async def _op(session: ClientSession):
            result = await session.call_tool(
                "search_prior_art",
                {
                    "search_query": search_query,
                    "technology_domain": technology_domain,
                    "search_scope": search_scope,
                    "max_results": max_results,
                    "date_range": date_range,
                }
            )
            
            if result.content and len(result.content) > 0:
                return result.content[0].text
            else:
                return "No prior art search results received"
        
        return await self._execute_with_server(_op)
    
    async def list_available_tools(self) -> List[str]:
        """List available tools from the server"""
        async def _op(session: ClientSession):
            tools = await session.list_tools()
            return [tool.name for tool in tools.tools]
        
        return await self._execute_with_server(_op)

# Demo and testing functions
async def demo():
    """Demo function showing how to use the IP analysis client"""
    client = IPAnalysisClient()
    
    # Test patentability assessment
    print("=== Testing Patentability Assessment ===")
    request = IPAnalysisRequest(
        invention_description="""
        A machine learning system that automatically generates patent claims 
        by analyzing technical descriptions and comparing them against existing 
        patent databases. The system uses natural language processing to extract 
        key technical features and generates legally-compliant claim language 
        while ensuring proper dependency structures between claims.
        """,
        technical_details="""
        The system employs transformer-based models fine-tuned on patent data,
        with specific components for:
        1. Technical feature extraction using named entity recognition
        2. Claim template generation using sequence-to-sequence models
        3. Prior art comparison using semantic similarity
        4. Legal compliance checking using rule-based validation
        """,
        industry_sector="legal-tech",
        invention_type="software"
    )
    
    try:
        result = await client.assess_patentability(request)
        print(result)
    except Exception as e:
        print(f"Error in patentability assessment: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test prior art search
    print("=== Testing Prior Art Search ===")
    try:
        search_result = await client.search_prior_art(
            search_query="automatic patent claim generation machine learning NLP",
            technology_domain="legal-tech AI",
            search_scope="comprehensive",
            max_results=30
        )
        print(search_result)
    except Exception as e:
        print(f"Error in prior art search: {e}")

async def main():
    """Main entry point for testing"""
    print("🔍 IP Analysis MCP Client Demo")
    print("=" * 50)
    
    client = IPAnalysisClient()
    
    # Test server connectivity
    try:
        tools = await client.list_available_tools()
        print(f"✅ Connected! Available tools: {', '.join(tools)}")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return
    
    # Run demo
    await demo()

if __name__ == "__main__":
    asyncio.run(main())
