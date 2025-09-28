#!/usr/bin/env python3
import streamlit as st
import asyncio
import sys
import os

from innovation_mcp_client import ProjectEvaluationClient, ProjectData

# Page configuration
st.set_page_config(
    page_title="Project Innovation Evaluator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .stAlert > div {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    .evaluation-result {
        background-color: #f8f9fa;
        color: #212529 !important;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #007bff;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_client():
    """Initialize and cache the MCP client"""
    try:
        return ProjectEvaluationClient()
    except Exception as e:
        st.error(f"Failed to initialize client: {e}")
        return None

def run_async_function(coro):
    """Helper function to run async functions in Streamlit"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    except Exception as e:
        st.error(f"Error running async function: {e}")
        return None
    finally:
        loop.close()

def main():
    st.title("🚀 Project Innovation & Novelty Evaluator")
    st.markdown("---")
    
    # Initialize client
    client = get_client()
    if not client:
        st.error("❌ Failed to initialize the evaluation client. Please check if mcp_server.py is available.")
        st.stop()
    
    # Test server connectivity
    if 'server_tested' not in st.session_state:
        with st.spinner("Testing server connection..."):
            try:
                tools = run_async_function(client.list_available_tools())
                if tools:
                    st.success(f"✅ Connected to server! Available tools: {', '.join(tools)}")
                    st.session_state.server_tested = True
                else:
                    st.error("❌ Failed to connect to server. Please ensure mcp_server.py is working.")
                    st.stop()
            except Exception as e:
                st.error(f"❌ Server connection failed: {e}")
                st.stop()
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    option = st.sidebar.selectbox(
        "Choose Operation",
        ["Single Project Evaluation", "Project Comparison", "Batch Evaluation"],
        index=0
    )
    
    # Main content based on selection
    if option == "Single Project Evaluation":
        single_project_evaluation(client)
    elif option == "Project Comparison":
        project_comparison(client)
    elif option == "Batch Evaluation":
        batch_evaluation(client)

def single_project_evaluation(client):
    """Handle single project evaluation"""
    st.header("📊 Single Project Evaluation")
    st.markdown("Evaluate the innovation and novelty of a single project.")
    
    # Initialize session state for results
    if 'single_evaluation_result' not in st.session_state:
        st.session_state.single_evaluation_result = None
        st.session_state.single_project_name = None
    
    with st.form("single_project_form", clear_on_submit=False):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            name = st.text_input(
                "Project Name *",
                placeholder="Enter your project name",
                help="A clear, descriptive name for your project"
            )
            
            synopsis = st.text_area(
                "Project Synopsis *",
                placeholder="Describe what your project does, its main features, and goals...",
                height=120,
                help="Provide a comprehensive description of your project"
            )
            
            code_context = st.text_area(
                "Code Context (Optional)",
                placeholder="Technical details, architecture, technologies used...",
                height=100,
                help="Additional technical information that might be relevant"
            )
        
        with col2:
            github_url = st.text_input(
                "GitHub URL (Optional)",
                placeholder="https://github.com/username/repo",
                help="Link to your project's repository"
            )
            
            st.markdown("### Quick Tips:")
            st.info("💡 **Synopsis**: Be specific about what makes your project unique")
            st.info("🔧 **Code Context**: Mention key technologies, algorithms, or architectural decisions")
            st.info("📁 **GitHub**: Helps provide additional context")
        
        submitted = st.form_submit_button(
            "🔍 Evaluate Project",
            type="primary",
            use_container_width=True
        )
        
        if submitted:
            if not name.strip():
                st.error("❌ Project name is required!")
            elif not synopsis.strip():
                st.error("❌ Project synopsis is required!")
            else:
                project_data = ProjectData(
                    name=name.strip(),
                    synopsis=synopsis.strip(),
                    code_context=code_context.strip(),
                    github_url=github_url.strip()
                )
                
                with st.spinner(f"🔄 Evaluating '{name.strip()}'... This may take a few moments."):
                    result = run_async_function(client.evaluate_single_project(project_data))
                    
                    if result:
                        st.session_state.single_evaluation_result = result
                        st.session_state.single_project_name = name.strip()
                        st.success("✅ Evaluation completed!")
                    else:
                        st.error("❌ Failed to evaluate project. Please try again.")
    
    # Display results outside the form
    if st.session_state.single_evaluation_result:
        with st.expander("📋 Full Evaluation Report", expanded=True):
            st.markdown(f'<div class="evaluation-result">{st.session_state.single_evaluation_result}</div>', 
                       unsafe_allow_html=True)
        
        # Download button outside the form
        st.download_button(
            label="📥 Download Report",
            data=st.session_state.single_evaluation_result,
            file_name=f"{st.session_state.single_project_name.replace(' ', '_')}_evaluation.md",
            mime="text/markdown"
        )

def project_comparison(client):
    """Handle project comparison"""
    st.header("⚖️ Project Comparison")
    st.markdown("Compare the innovation and novelty of two projects side-by-side.")
    
    # Initialize session state for comparison results
    if 'comparison_result' not in st.session_state:
        st.session_state.comparison_result = None
        st.session_state.comparison_name1 = None
        st.session_state.comparison_name2 = None
    
    with st.form("comparison_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Project 1")
            name1 = st.text_input("Project 1 Name *", key="p1_name")
            synopsis1 = st.text_area("Project 1 Synopsis *", height=100, key="p1_synopsis")
            context1 = st.text_area("Project 1 Code Context", height=80, key="p1_context")
            github1 = st.text_input("Project 1 GitHub URL", key="p1_github")
        
        with col2:
            st.subheader("Project 2")
            name2 = st.text_input("Project 2 Name *", key="p2_name")
            synopsis2 = st.text_area("Project 2 Synopsis *", height=100, key="p2_synopsis")
            context2 = st.text_area("Project 2 Code Context", height=80, key="p2_context")
            github2 = st.text_input("Project 2 GitHub URL", key="p2_github")
        
        submitted = st.form_submit_button(
            "⚖️ Compare Projects",
            type="primary",
            use_container_width=True
        )
        
        if submitted:
            if not all([name1.strip(), synopsis1.strip(), name2.strip(), synopsis2.strip()]):
                st.error("❌ Please provide names and synopses for both projects!")
            else:
                project1 = ProjectData(name=name1.strip(), synopsis=synopsis1.strip(), 
                                     code_context=context1.strip(), github_url=github1.strip())
                project2 = ProjectData(name=name2.strip(), synopsis=synopsis2.strip(), 
                                     code_context=context2.strip(), github_url=github2.strip())
                
                with st.spinner(f"🔄 Comparing '{name1.strip()}' vs '{name2.strip()}'... This may take a few moments."):
                    result = run_async_function(client.compare_projects(project1, project2))
                    
                    if result:
                        st.session_state.comparison_result = result
                        st.session_state.comparison_name1 = name1.strip()
                        st.session_state.comparison_name2 = name2.strip()
                        st.success("✅ Comparison completed!")
                    else:
                        st.error("❌ Failed to compare projects. Please try again.")
    
    # Display results outside the form
    if st.session_state.comparison_result:
        with st.expander("📊 Full Comparison Report", expanded=True):
            st.markdown(f'<div class="evaluation-result">{st.session_state.comparison_result}</div>', 
                       unsafe_allow_html=True)
        
        # Download button outside the form
        st.download_button(
            label="📥 Download Comparison",
            data=st.session_state.comparison_result,
            file_name=f"{st.session_state.comparison_name1}_vs_{st.session_state.comparison_name2}_comparison.md",
            mime="text/markdown"
        )

def batch_evaluation(client):
    """Handle batch evaluation"""
    st.header("📦 Batch Evaluation")
    st.markdown("Evaluate multiple projects at once.")
    
    # Initialize session state for projects and results
    if 'batch_projects' not in st.session_state:
        st.session_state.batch_projects = []
    if 'batch_result' not in st.session_state:
        st.session_state.batch_result = None
    
    # Add new project section
    st.subheader("➕ Add Projects")
    with st.form("add_project_form"):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            new_name = st.text_input("Project Name")
            new_synopsis = st.text_area("Project Synopsis", height=80)
            new_context = st.text_area("Code Context (Optional)", height=60)
            new_github = st.text_input("GitHub URL (Optional)")
        
        with col2:
            st.markdown("### Current Projects:")
            if st.session_state.batch_projects:
                for i, proj in enumerate(st.session_state.batch_projects):
                    st.write(f"{i+1}. {proj['name']}")
            else:
                st.write("No projects added yet")
        
        col_add, col_clear = st.columns(2)
        
        with col_add:
            add_submitted = st.form_submit_button("➕ Add Project", type="primary")
        
        with col_clear:
            clear_submitted = st.form_submit_button("🗑️ Clear All")
        
        if add_submitted:
            if new_name.strip() and new_synopsis.strip():
                project = {
                    'name': new_name.strip(),
                    'synopsis': new_synopsis.strip(),
                    'code_context': new_context.strip(),
                    'github_url': new_github.strip()
                }
                st.session_state.batch_projects.append(project)
                st.success(f"✅ Added '{new_name}' to batch evaluation list!")
                st.rerun()
            else:
                st.error("❌ Project name and synopsis are required!")
        
        if clear_submitted:
            st.session_state.batch_projects = []
            st.session_state.batch_result = None
            st.success("✅ Cleared all projects!")
            st.rerun()
    
    # Batch evaluation section
    if st.session_state.batch_projects:
        st.subheader(f"📊 Evaluate {len(st.session_state.batch_projects)} Projects")
        
        if st.button("🚀 Run Batch Evaluation", type="primary", use_container_width=True):
            projects_data = [
                ProjectData(
                    name=proj['name'],
                    synopsis=proj['synopsis'],
                    code_context=proj['code_context'],
                    github_url=proj['github_url']
                ) for proj in st.session_state.batch_projects
            ]
            
            with st.spinner(f"🔄 Evaluating {len(projects_data)} projects... This may take several minutes."):
                result = run_async_function(client.evaluate_multiple_projects(projects_data))
                
                if result:
                    st.session_state.batch_result = result
                    st.success("✅ Batch evaluation completed!")
                else:
                    st.error("❌ Failed to run batch evaluation. Please try again.")
    
    # Display batch results outside the form
    if st.session_state.batch_result:
        with st.expander("📋 Full Batch Evaluation Report", expanded=True):
            st.markdown(f'<div class="evaluation-result">{st.session_state.batch_result}</div>', 
                       unsafe_allow_html=True)
        
        # Download button outside the form
        st.download_button(
            label="📥 Download Batch Report",
            data=st.session_state.batch_result,
            file_name="batch_evaluation_report.md",
            mime="text/markdown"
        )

if __name__ == "__main__":
    main()