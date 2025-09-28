#!/usr/bin/env python3
"""
Streamlit App for IP Analysis MCP Server
Provides a user-friendly interface for patentability assessment and prior art search
"""

import streamlit as st
import asyncio
import sys
import os

from datetime import datetime
from ip_mcp_client import IPAnalysisClient, IPAnalysisRequest

# Page configuration
st.set_page_config(
    page_title="IP Analysis Tool",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .stAlert > div {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    .analysis-result {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #007bff;
        margin: 1rem 0;
        font-family: 'Courier New', monospace;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.25rem;
        padding: 0.75rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.25rem;
        padding: 0.75rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_ip_client():
    """Initialize and cache the IP Analysis MCP client"""
    try:
        # Adjust the path to your IP MCP server
        return IPAnalysisClient("ip_mcp_server.py")
    except Exception as e:
        st.error(f"Failed to initialize IP client: {e}")
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

def display_server_status():
    """Display server connection status"""
    if 'server_status' not in st.session_state:
        st.session_state.server_status = 'checking'
    
    if st.session_state.server_status == 'checking':
        with st.spinner("🔄 Checking server connection..."):
            client = get_ip_client()
            if client:
                try:
                    tools = run_async_function(client.list_available_tools())
                    if tools:
                        st.session_state.server_status = 'connected'
                        st.session_state.available_tools = tools
                    else:
                        st.session_state.server_status = 'error'
                except Exception as e:
                    st.session_state.server_status = 'error'
                    st.session_state.error_message = str(e)
            else:
                st.session_state.server_status = 'error'
    
    # Display status
    if st.session_state.server_status == 'connected':
        st.success(f"✅ Connected to IP Analysis Server! Available tools: {', '.join(st.session_state.available_tools)}")
        return True
    elif st.session_state.server_status == 'error':
        error_msg = st.session_state.get('error_message', 'Unknown error')
        st.error(f"❌ Failed to connect to server: {error_msg}")
        
        if st.button("🔄 Retry Connection"):
            st.session_state.server_status = 'checking'
            st.rerun()
        
        st.info("💡 Make sure the IP MCP server is running: `python ip_mcp_server.py`")
        return False
    
    return False

def patentability_assessment_section():
    """Patentability Assessment Interface"""
    st.header("🔍 Patentability Assessment")
    st.markdown("Evaluate your invention based on USPTO criteria: novelty, non-obviousness, utility, and subject matter eligibility.")
    
    # Initialize session state
    if 'patent_assessment_result' not in st.session_state:
        st.session_state.patent_assessment_result = None
        st.session_state.patent_project_name = None
    
    with st.form("patentability_form", clear_on_submit=False):
        # Input fields
        col1, col2 = st.columns([2, 1])
        
        with col1:
            project_name = st.text_input(
                "🏷️ Invention/Project Name *",
                placeholder="e.g., Smart Hydration Tracking System",
                help="A clear, descriptive name for your invention"
            )
            
            invention_description = st.text_area(
                "📝 Invention Description *",
                placeholder="Describe what your invention does, its main features, functionality, and how it works...",
                height=150,
                help="Provide a comprehensive description of your invention's purpose and functionality"
            )
            
            technical_details = st.text_area(
                "🔧 Technical Implementation Details",
                placeholder="Describe the technical aspects: algorithms, hardware components, software architecture, materials, etc...",
                height=120,
                help="Include specific technical information that makes your invention unique"
            )
        
        with col2:
            st.markdown("### 🎯 Classification")
            
            industry_sector = st.selectbox(
                "Industry Sector",
                ["", "software", "hardware", "biotech", "fintech", "health-tech", 
                 "automotive", "aerospace", "energy", "telecommunications", 
                 "consumer-electronics", "medical-devices", "agriculture", "other"],
                help="Select the primary industry for your invention"
            )
            
            invention_type = st.selectbox(
                "Invention Type",
                ["software", "hardware", "method", "composition", "system", "process"],
                help="Choose the type that best describes your invention"
            )
            
            st.markdown("### 💡 Assessment Tips")
            st.info("**Be Specific**: Include unique features that differentiate your invention")
            st.info("**Technical Details**: Mention specific algorithms, components, or processes")
            st.info("**Problem Solving**: Explain what problem your invention solves")
        
        # Submit button
        submitted = st.form_submit_button(
            "🔍 Assess Patentability",
            type="primary",
            use_container_width=True
        )
        
        if submitted:
            if not project_name.strip():
                st.error("❌ Project name is required!")
            elif not invention_description.strip():
                st.error("❌ Invention description is required!")
            else:
                # Create analysis request
                request = IPAnalysisRequest(
                    invention_description=invention_description.strip(),
                    technical_details=technical_details.strip(),
                    industry_sector=industry_sector if industry_sector else "general",
                    invention_type=invention_type
                )
                
                # Run assessment
                with st.spinner(f"🔄 Assessing patentability of '{project_name}'... This may take 30-60 seconds."):
                    client = get_ip_client()
                    if client:
                        try:
                            result = run_async_function(client.assess_patentability(request))
                            if result:
                                st.session_state.patent_assessment_result = result
                                st.session_state.patent_project_name = project_name.strip()
                                st.success("✅ Patentability assessment completed!")
                            else:
                                st.error("❌ Failed to complete assessment. Please try again.")
                        except Exception as e:
                            st.error(f"❌ Assessment error: {str(e)}")
                    else:
                        st.error("❌ Client not available. Please check server connection.")
    
    # Display results outside form
    if st.session_state.patent_assessment_result:
        st.markdown("---")
        st.subheader(f"📊 Assessment Results for: {st.session_state.patent_project_name}")
        
        with st.expander("📋 Full Patentability Assessment Report", expanded=True):
            st.markdown(f'<div class="analysis-result">{st.session_state.patent_assessment_result}</div>', 
                       unsafe_allow_html=True)
        
        # Download button
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            st.download_button(
                label="📥 Download Report",
                data=st.session_state.patent_assessment_result,
                file_name=f"{st.session_state.patent_project_name.replace(' ', '_')}_patentability_assessment.md",
                mime="text/markdown"
            )
        
        with col2:
            if st.button("🗑️ Clear Results"):
                st.session_state.patent_assessment_result = None
                st.session_state.patent_project_name = None
                st.rerun()

def prior_art_search_section():
    """Prior Art Search Interface"""
    st.header("📚 Prior Art Search")
    st.markdown("Search multiple databases for existing patents, academic papers, and commercial products related to your invention.")
    
    # Initialize session state
    if 'prior_art_result' not in st.session_state:
        st.session_state.prior_art_result = None
        st.session_state.search_query_used = None
    
    with st.form("prior_art_form", clear_on_submit=False):
        # Input fields
        col1, col2 = st.columns([2, 1])
        
        with col1:
            search_query = st.text_area(
                "🔍 Search Query *",
                placeholder="e.g., smart water bottle IoT sensors hydration tracking mobile app",
                height=100,
                help="Enter keywords and technical terms that describe your invention"
            )
            
            technology_domain = st.text_input(
                "🏭 Technology Domain",
                placeholder="e.g., IoT health-tech wearable devices",
                help="Specific technology area or domain (optional but recommended)"
            )
        
        with col2:
            st.markdown("### ⚙️ Search Settings")
            
            search_scope = st.selectbox(
                "Search Depth",
                ["quick", "comprehensive", "exhaustive"],
                index=1,
                help="Quick: Fast search, Comprehensive: Balanced, Exhaustive: Thorough but slower"
            )
            
            max_results = st.slider(
                "Max Results per Database",
                min_value=10,
                max_value=100,
                value=50,
                step=10,
                help="Maximum number of results to return from each database"
            )
            
            date_range = st.selectbox(
                "Publication Date Range",
                ["all", "1_year", "5_years", "10_years"],
                index=2,
                help="Limit search to specific time period"
            )
            
            st.markdown("### 📊 Databases Searched")
            st.info("• Google Patents\n• USPTO Database\n• Google Scholar\n• Semantic Scholar")
        
        # Submit button
        submitted = st.form_submit_button(
            "🔍 Search Prior Art",
            type="primary",
            use_container_width=True
        )
        
        if submitted:
            if not search_query.strip():
                st.error("❌ Search query is required!")
            else:
                # Run prior art search
                with st.spinner(f"🔄 Searching for prior art... This may take 45-90 seconds."):
                    client = get_ip_client()
                    if client:
                        try:
                            result = run_async_function(client.search_prior_art(
                                search_query=search_query.strip(),
                                technology_domain=technology_domain.strip() if technology_domain else "",
                                search_scope=search_scope,
                                max_results=max_results,
                                date_range=date_range
                            ))
                            
                            if result:
                                st.session_state.prior_art_result = result
                                st.session_state.search_query_used = search_query.strip()
                                st.success("✅ Prior art search completed!")
                            else:
                                st.error("❌ Failed to complete search. Please try again.")
                        except Exception as e:
                            st.error(f"❌ Search error: {str(e)}")
                    else:
                        st.error("❌ Client not available. Please check server connection.")
    
    # Display results outside form
    if st.session_state.prior_art_result:
        st.markdown("---")
        st.subheader(f"🔍 Prior Art Search Results for: '{st.session_state.search_query_used}'")
        
        with st.expander("📚 Full Prior Art Search Report", expanded=True):
            st.markdown(f'<div class="analysis-result">{st.session_state.prior_art_result}</div>', 
                       unsafe_allow_html=True)
        
        # Download and action buttons
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            st.download_button(
                label="📥 Download Report",
                data=st.session_state.prior_art_result,
                file_name=f"prior_art_search_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown"
            )
        
        with col2:
            if st.button("🗑️ Clear Results"):
                st.session_state.prior_art_result = None
                st.session_state.search_query_used = None
                st.rerun()

def comprehensive_analysis_section():
    """Combined Analysis Interface"""
    st.header("🎯 Comprehensive IP Analysis")
    st.markdown("Perform both patentability assessment and prior art search in one comprehensive analysis.")
    
    # Initialize session state
    if 'comprehensive_result' not in st.session_state:
        st.session_state.comprehensive_result = None
        st.session_state.comprehensive_project_name = None
    
    with st.form("comprehensive_form", clear_on_submit=False):
        # Input fields
        project_name = st.text_input(
            "🏷️ Project/Invention Name *",
            placeholder="e.g., AI-Powered Plant Disease Detection System"
        )
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            invention_description = st.text_area(
                "📝 Complete Invention Description *",
                placeholder="Provide a comprehensive description of your invention including functionality, features, and benefits...",
                height=200
            )
            
            technical_details = st.text_area(
                "🔧 Technical Implementation *",
                placeholder="Detailed technical information: technologies used, algorithms, hardware, architecture...",
                height=150
            )
        
        with col2:
            st.markdown("### 🎯 Classification & Settings")
            
            industry_sector = st.selectbox(
                "Industry",
                ["software", "hardware", "biotech", "fintech", "health-tech", 
                 "automotive", "aerospace", "energy", "other"],
                help="Primary industry sector"
            )
            
            invention_type = st.selectbox(
                "Type",
                ["software", "hardware", "method", "composition", "system"],
                help="Invention category"
            )
            
            search_scope = st.selectbox(
                "Analysis Depth",
                ["comprehensive", "exhaustive"],
                help="Depth of prior art search"
            )
            
            st.markdown("### 📊 This Will Include:")
            st.info("✅ Novelty Assessment\n✅ Non-obviousness Analysis\n✅ Utility Evaluation\n✅ Subject Matter Check\n✅ Multi-database Prior Art Search\n✅ Patent Landscape Analysis")
        
        # Submit button
        submitted = st.form_submit_button(
            "🚀 Run Comprehensive Analysis",
            type="primary",
            use_container_width=True
        )
        
        if submitted:
            if not project_name.strip() or not invention_description.strip():
                st.error("❌ Project name and invention description are required!")
            else:
                client = get_ip_client()
                if not client:
                    st.error("❌ Client not available. Please check server connection.")
                    return
                
                # Progress tracking
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    # Step 1: Patentability Assessment
                    status_text.text("🔄 Step 1/2: Running patentability assessment...")
                    progress_bar.progress(25)
                    
                    request = IPAnalysisRequest(
                        invention_description=invention_description.strip(),
                        technical_details=technical_details.strip(),
                        industry_sector=industry_sector,
                        invention_type=invention_type
                    )
                    
                    patent_result = run_async_function(client.assess_patentability(request))
                    progress_bar.progress(50)
                    
                    if not patent_result:
                        st.error("❌ Failed to complete patentability assessment.")
                        return
                    
                    # Step 2: Prior Art Search
                    status_text.text("🔄 Step 2/2: Searching for prior art...")
                    progress_bar.progress(75)
                    
                    # Create search query from invention description
                    search_query = f"{project_name} {invention_description[:200]}"
                    
                    prior_art_result = run_async_function(client.search_prior_art(
                        search_query=search_query,
                        technology_domain=f"{industry_sector} {invention_type}",
                        search_scope=search_scope,
                        max_results=40
                    ))
                    
                    progress_bar.progress(100)
                    status_text.text("✅ Analysis completed!")
                    
                    if prior_art_result:
                        # Combine results
                        comprehensive_report = f"""# Comprehensive IP Analysis Report
## Project: {project_name}
**Analysis Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Industry**: {industry_sector} | **Type**: {invention_type}

---

{patent_result}

---

{prior_art_result}

---
*Report generated by IP Analysis MCP Server*
"""
                        
                        st.session_state.comprehensive_result = comprehensive_report
                        st.session_state.comprehensive_project_name = project_name.strip()
                        st.success("✅ Comprehensive analysis completed successfully!")
                    else:
                        st.warning("⚠️ Patentability assessment completed, but prior art search failed.")
                        st.session_state.comprehensive_result = patent_result
                        st.session_state.comprehensive_project_name = project_name.strip()
                
                except Exception as e:
                    st.error(f"❌ Analysis failed: {str(e)}")
                finally:
                    progress_bar.empty()
                    status_text.empty()
    
    # Display results
    if st.session_state.comprehensive_result:
        st.markdown("---")
        st.subheader(f"📊 Comprehensive Analysis: {st.session_state.comprehensive_project_name}")
        
        with st.expander("📋 Complete Analysis Report", expanded=True):
            st.markdown(f'<div class="analysis-result">{st.session_state.comprehensive_result}</div>', 
                       unsafe_allow_html=True)
        
        # Action buttons
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.download_button(
                label="📥 Download Full Report",
                data=st.session_state.comprehensive_result,
                file_name=f"{st.session_state.comprehensive_project_name.replace(' ', '_')}_comprehensive_analysis.md",
                mime="text/markdown"
            )
        
        with col2:
            if st.button("🗑️ Clear Results"):
                st.session_state.comprehensive_result = None
                st.session_state.comprehensive_project_name = None
                st.rerun()

def main():
    """Main Streamlit application"""
    
    # Header
    st.title("🔍 Intellectual Property Analysis Tool")
    st.markdown("**Comprehensive patentability assessment and prior art search powered by AI**")
    st.markdown("---")
    
    # Check server connection
    if not display_server_status():
        st.stop()
    
    # Sidebar navigation
    st.sidebar.title("🧭 Navigation")
    st.sidebar.markdown("Choose your analysis type:")
    
    analysis_type = st.sidebar.radio(
        "Analysis Options",
        [
            "🔍 Patentability Assessment",
            "📚 Prior Art Search", 
            "🎯 Comprehensive Analysis"
        ],
        help="Select the type of IP analysis you want to perform"
    )
    
    # Sidebar info
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📋 About This Tool")
    st.sidebar.info(
        """
        This tool provides AI-powered intellectual property analysis including:
        
        • **Patentability Assessment**: Evaluate novelty, non-obviousness, utility, and subject matter eligibility
        
        • **Prior Art Search**: Search patent databases and academic literature
        
        • **Comprehensive Analysis**: Combined assessment with detailed reporting
        """
    )
    
    st.sidebar.markdown("### ⚡ Quick Tips")
    st.sidebar.success(
        """
        • Be specific in your descriptions
        • Include technical details and unique features
        • Mention the problem your invention solves
        • Use relevant technical keywords
        """
    )
    
    # Main content based on selection
    if analysis_type == "🔍 Patentability Assessment":
        patentability_assessment_section()
    elif analysis_type == "📚 Prior Art Search":
        prior_art_search_section()
    elif analysis_type == "🎯 Comprehensive Analysis":
        comprehensive_analysis_section()
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 20px;'>
        <p>🔬 <strong>IP Analysis Tool</strong> | Powered by MCP Server Technology</p>
        <p><em>Disclaimer: This tool provides analysis for informational purposes only and does not constitute legal advice. 
        Consult with qualified patent attorneys for legal opinions.</em></p>
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
