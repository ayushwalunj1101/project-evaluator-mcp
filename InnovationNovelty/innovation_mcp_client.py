#!/usr/bin/env python3
"""
MCP Client for Project Innovation and Novelty Evaluation
Updated for current MCP Python SDK structure
"""

import asyncio
import logging
import subprocess
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Callable, Awaitable

# Updated imports for current MCP SDK
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ProjectData:
    """Container for a single project."""
    name: str
    synopsis: str
    code_context: str = ""
    github_url: str = ""

class GitHubExtractor:
    """Extract information from GitHub repositories"""
    
    @staticmethod
    async def extract_repo_info(github_url: str) -> Dict[str, str]:
        """Extract basic info from a GitHub repository"""
        try:
            # Extract owner and repo from URL
            parts = github_url.replace("https://github.com/", "").split("/")
            if len(parts) >= 2:
                owner, repo = parts[0], parts[1]
                return {
                    "owner": owner,
                    "repo": repo,
                    "url": github_url,
                    "context": f"Repository: {owner}/{repo}"
                }
        except Exception as e:
            logger.error(f"Error extracting GitHub info: {e}")
            return {"context": f"GitHub URL: {github_url}"}

class ProjectEvaluationClient:
    """Client for interacting with the Project Evaluation MCP Server"""

    def __init__(self, server_script_path: str = "mcp_server.py"):
        self.server_script_path = server_script_path
        self.github_extractor = GitHubExtractor()

    async def _execute_with_server(self, operation: Callable[[ClientSession], Awaitable[Any]]) -> Any:
        """Execute an operation with the MCP server"""
        # Create server parameters
        server_params = StdioServerParameters(
            command="python",
            args=[self.server_script_path],
        )

        try:
            # Connect to server using stdio client
            async with stdio_client(server_params) as (read_stream, write_stream):
                # Create client session
                async with ClientSession(read_stream, write_stream) as session:
                    # Initialize the connection
                    await session.initialize()
                    
                    # Execute the operation
                    return await operation(session)
                    
        except Exception as e:
            logger.error(f"Error in server operation: {e}")
            raise

    async def _augment_context(self, project: ProjectData) -> str:
        """Augment code context with GitHub info if available"""
        ctx = project.code_context or ""
        if project.github_url:
            gh_info = await self.github_extractor.extract_repo_info(project.github_url)
            ctx += f"\n{gh_info.get('context', '')}"
        return ctx

    async def list_available_tools(self) -> List[str]:
        """List available tools from the server"""
        async def _op(session: ClientSession):
            tools = await session.list_tools()
            return [tool.name for tool in tools.tools]

        return await self._execute_with_server(_op)

    async def evaluate_single_project(self, project: ProjectData) -> str:
        """Evaluate a single project"""
        code_context = await self._augment_context(project)

        async def _op(session: ClientSession):
            result = await session.call_tool(
                "evaluate_innovation",
                {
                    "synopsis": project.synopsis,
                    "code_context": code_context,
                    "project_name": project.name,
                }
            )
            if result.content and len(result.content) > 0:
                return result.content[0].text
            else:
                return "No evaluation result received"

        return await self._execute_with_server(_op)

    async def evaluate_multiple_projects(self, projects: List[ProjectData]) -> str:
        """Evaluate multiple projects in batch"""
        async def _op(session: ClientSession):
            projects_data = []
            for project in projects:
                code_context = await self._augment_context(project)
                projects_data.append({
                    "name": project.name,
                    "synopsis": project.synopsis,
                    "code_context": code_context
                })

            result = await session.call_tool("batch_evaluate", {"projects": projects_data})
            if result.content and len(result.content) > 0:
                return result.content[0].text
            else:
                return "No batch evaluation result received"

        return await self._execute_with_server(_op)

    async def compare_projects(self, project1: ProjectData, project2: ProjectData) -> str:
        """Compare two projects"""
        async def _op(session: ClientSession):
            # Prepare project data
            p1_context = await self._augment_context(project1)
            p2_context = await self._augment_context(project2)
            
            result = await session.call_tool(
                "compare_projects",
                {
                    "project1": {
                        "name": project1.name,
                        "synopsis": project1.synopsis,
                        "code_context": p1_context
                    },
                    "project2": {
                        "name": project2.name,
                        "synopsis": project2.synopsis,
                        "code_context": p2_context
                    }
                }
            )
            if result.content and len(result.content) > 0:
                return result.content[0].text
            else:
                return "No comparison result received"

        return await self._execute_with_server(_op)

class InteractiveCLI:
    """Interactive command-line interface for the evaluation client"""

    def __init__(self):
        self.client = ProjectEvaluationClient()
        self.projects = []

    async def run(self):
        """Run the interactive CLI"""
        print("🚀 Project Innovation & Novelty Evaluator")
        print("=" * 50)
        
        # Test server connectivity
        print("Testing server connection...")
        try:
            tools = await self.client.list_available_tools()
            print(f"✅ Connected successfully! Available tools: {', '.join(tools)}")
        except Exception as e:
            print(f"❌ Failed to connect to server: {e}")
            print("Make sure mcp_server.py is available and working.")
            return

        while True:
            try:
                await self._show_menu()
                choice = input("Enter your choice (0-6): ").strip()
                
                if choice == "0":
                    break
                elif choice == "1":
                    await self._add_project()
                elif choice == "2":
                    await self._evaluate_single()
                elif choice == "3":
                    await self._evaluate_batch()
                elif choice == "4":
                    await self._compare_projects()
                elif choice == "5":
                    await self._list_projects()
                elif choice == "6":
                    await self._clear_projects()
                else:
                    print("❌ Invalid choice. Please try again.")
                print()
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")

        print("👋 Goodbye!")

    async def _show_menu(self):
        """Show the main menu"""
        print("\n📋 Menu:")
        print("1. Add project")
        print("2. Evaluate single project")
        print("3. Batch evaluate all projects")
        print("4. Compare two projects")
        print("5. List projects")
        print("6. Clear all projects")
        print("0. Exit")

    async def _add_project(self):
        """Add a new project"""
        print("\n➕ Adding new project")
        name = input("Project name: ").strip()
        synopsis = input("Project synopsis: ").strip()
        github_url = input("GitHub URL (optional): ").strip()
        code_context = input("Additional code context (optional): ").strip()

        if name and synopsis:
            project = ProjectData(
                name=name,
                synopsis=synopsis,
                code_context=code_context,
                github_url=github_url
            )
            self.projects.append(project)
            print(f"✅ Added project: {name}")
        else:
            print("❌ Name and synopsis are required")

    async def _evaluate_single(self):
        """Evaluate a single project"""
        if not self.projects:
            print("❌ No projects available. Add a project first.")
            return

        print("\n🔍 Select project to evaluate:")
        for i, project in enumerate(self.projects):
            print(f"{i + 1}. {project.name}")

        try:
            choice = int(input("Enter project number: ")) - 1
            if 0 <= choice < len(self.projects):
                project = self.projects[choice]
                print(f"\n🔄 Evaluating {project.name}...")
                result = await self.client.evaluate_single_project(project)
                print("\n📊 Evaluation Result:")
                print("-" * 50)
                print(result)
            else:
                print("❌ Invalid project number")
        except ValueError:
            print("❌ Please enter a valid number")

    async def _evaluate_batch(self):
        """Batch evaluate all projects"""
        if not self.projects:
            print("❌ No projects available. Add projects first.")
            return

        print(f"\n🔄 Batch evaluating {len(self.projects)} projects...")
        result = await self.client.evaluate_multiple_projects(self.projects)
        print("\n📊 Batch Evaluation Results:")
        print("-" * 50)
        print(result)

    async def _compare_projects(self):
        """Compare two projects"""
        if len(self.projects) < 2:
            print("❌ Need at least 2 projects for comparison.")
            return

        print("\n🔍 Select first project:")
        for i, project in enumerate(self.projects):
            print(f"{i + 1}. {project.name}")

        try:
            choice1 = int(input("Enter first project number: ")) - 1
            choice2 = int(input("Enter second project number: ")) - 1

            if (0 <= choice1 < len(self.projects) and
                0 <= choice2 < len(self.projects) and
                choice1 != choice2):
                
                project1 = self.projects[choice1]
                project2 = self.projects[choice2]
                print(f"\n🔄 Comparing {project1.name} vs {project2.name}...")
                result = await self.client.compare_projects(project1, project2)
                print("\n📊 Comparison Result:")
                print("-" * 50)
                print(result)
            else:
                print("❌ Invalid project selection")
        except ValueError:
            print("❌ Please enter valid numbers")

    async def _list_projects(self):
        """List all projects"""
        if not self.projects:
            print("❌ No projects available")
            return

        print(f"\n📋 Projects ({len(self.projects)}):")
        for i, project in enumerate(self.projects, 1):
            print(f"{i}. {project.name}")
            print(f"   Synopsis: {project.synopsis[:100]}{'...' if len(project.synopsis) > 100 else ''}")
            if project.github_url:
                print(f"   GitHub: {project.github_url}")
            print()

    async def _clear_projects(self):
        """Clear all projects"""
        if self.projects:
            confirm = input(f"Clear all {len(self.projects)} projects? (y/N): ").strip().lower()
            if confirm == 'y':
                self.projects.clear()
                print("✅ All projects cleared")
        else:
            print("❌ No projects to clear")

# Example usage and demo
async def demo():
    """Demo function showing how to use the client programmatically"""
    client = ProjectEvaluationClient()

    # Create sample projects
    project1 = ProjectData(
        name="AI Code Assistant",
        synopsis="An AI-powered code assistant that helps developers write better code by providing real-time suggestions, bug detection, and optimization recommendations.",
        code_context="Uses transformer models for code analysis",
        github_url="https://github.com/example/ai-code-assistant"
    )

    project2 = ProjectData(
        name="Blockchain Voting System",
        synopsis="A decentralized voting system built on blockchain technology to ensure transparent and tamper-proof elections.",
        code_context="Smart contracts written in Solidity"
    )

    # Evaluate single project
    print("Evaluating single project...")
    result = await client.evaluate_single_project(project1)
    print(result)

    # Compare projects
    print("\nComparing projects...")
    comparison = await client.compare_projects(project1, project2)
    print(comparison)

async def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        await demo()
    else:
        cli = InteractiveCLI()
        await cli.run()

if __name__ == "__main__":
    asyncio.run(main())