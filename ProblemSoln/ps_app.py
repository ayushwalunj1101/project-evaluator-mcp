# app.py
import streamlit as st
from gradio_client import Client
import json
import time
import threading

# Page configuration
st.set_page_config(
    page_title="Relevance Checker",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    .result-container {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin-top: 20px;
    }
    
    .error-container {
        background-color: #fee;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #e74c3c;
        margin-top: 20px;
    }
    
    .success-container {
        background-color: #eff;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #27ae60;
        margin-top: 20px;
    }
    
    .stTextArea textarea {
        font-size: 16px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .stButton button {
        background: linear-gradient(135deg, #1f77b4 0%, #17a2b8 100%);
        color: white;
        border: none;
        border-radius: 10px;
        font-size: 18px;
        font-weight: 600;
        padding: 0.75rem 2rem;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(31, 119, 180, 0.3);
    }
    
    .processing-info {
        background-color: #fff3cd;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown('<h1 class="main-header">🔍 Relevance Checker</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Analyze how well a solution addresses a given problem statement</p>', unsafe_allow_html=True)

# API client configuration
GRADIO_URL = "https://e470ee41b84fa72754.gradio.live/"

# Initialize session state
if 'result' not in st.session_state:
    st.session_state.result = None
if 'show_result' not in st.session_state:
    st.session_state.show_result = False
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False

# Create two columns for better layout
col1, col2 = st.columns([3, 1])

with col1:
    # Input form
    with st.form("relevance_form"):
        st.markdown("### 📝 Input Details")
        
        problem_statement = st.text_area(
            "Problem Statement",
            placeholder="Enter the problem statement you want to analyze...",
            height=150,
            help="Describe the problem that needs to be solved"
        )
        
        solution = st.text_area(
            "Solution",
            placeholder="Enter the proposed solution...",
            height=150,
            help="Provide the solution you want to evaluate for relevance"
        )
        
        submitted = st.form_submit_button("🚀 Check Relevance", use_container_width=True)

with col2:
    # API Status indicator
    st.markdown("### 🌐 API Status")
    try:
        # Simple ping to check if API is reachable
        client = Client(GRADIO_URL)
        st.success("✅ API Online")
    except:
        st.error("❌ API Offline")
    
    # Processing time warning
    st.markdown("### ⏱️ Processing Time")
    st.warning("⚠️ Analysis takes ~45 seconds\nPlease be patient!")
    
    # Instructions
    st.markdown("### ℹ️ How to Use")
    st.info("""
    1. Enter your problem statement
    2. Provide a proposed solution
    3. Click 'Check Relevance'
    4. **Wait patiently** (~45 seconds)
    5. Review the analysis results
    """)

# Handle form submission
if submitted:
    if not problem_statement.strip() or not solution.strip():
        st.error("❌ Please fill in both the problem statement and solution fields.")
    else:
        # Processing time warning
        st.markdown('<div class="processing-info">', unsafe_allow_html=True)
        st.warning("⏳ **Please wait patiently!** This analysis typically takes about 45 seconds to complete. Do not refresh the page or click the button again.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Progress bar and timer
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        with st.spinner("🔄 Deep analysis in progress... Please wait (this may take up to 60 seconds)"):
            try:
                start_time = time.time()
                st.session_state.analysis_complete = False
                
                def update_progress():
                    for i in range(50):
                        if st.session_state.analysis_complete:
                            break
                        time.sleep(0.9)
                        progress = min((i + 1) / 50, 0.95)
                        progress_bar.progress(progress)
                        elapsed = int(time.time() - start_time)
                        status_text.text(f"Processing... ({elapsed}s elapsed)")
                
                # Start progress thread
                progress_thread = threading.Thread(target=update_progress)
                progress_thread.start()
                
                # Using Gradio client for API call
                client = Client(GRADIO_URL)
                result = client.predict(
                    problem_statement=problem_statement.strip(),
                    solution=solution.strip(),
                    api_name="/check_relevance"
                )
                
                # Mark as complete
                st.session_state.analysis_complete = True
                progress_thread.join(timeout=1)
                
                # Complete progress bar
                progress_bar.progress(1.0)
                elapsed_total = int(time.time() - start_time)
                status_text.text(f"✅ Completed in {elapsed_total} seconds!")
                
                st.session_state.result = result
                st.session_state.show_result = True
                st.session_state.result_type = "success"
                    
            except Exception as e:
                st.session_state.analysis_complete = True
                progress_bar.empty()
                status_text.empty()
                st.session_state.result = f"An error occurred: {str(e)}"
                st.session_state.show_result = True
                st.session_state.result_type = "error"

# Display results
if st.session_state.show_result:
    st.markdown("---")
    st.markdown("### 📊 Analysis Results")
    
    if st.session_state.result_type == "success":
        st.markdown('<div class="success-container">', unsafe_allow_html=True)
        st.success("✅ Analysis completed successfully!")
        
        # Display the result in a formatted way
        if isinstance(st.session_state.result, (dict, list)):
            st.json(st.session_state.result)
        else:
            st.code(str(st.session_state.result), language="text")
            
        # Add download button for results
        result_json = json.dumps(st.session_state.result, indent=2)
        st.download_button(
            label="📥 Download Results (JSON)",
            data=result_json,
            file_name=f"relevance_check_results_{int(time.time())}.json",
            mime="application/json"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
    else:
        st.markdown('<div class="error-container">', unsafe_allow_html=True)
        st.error("❌ An error occurred during analysis")
        st.code(str(st.session_state.result), language="text")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Clear results button
    if st.button("🔄 Clear Results"):
        st.session_state.show_result = False
        st.session_state.result = None
        st.session_state.analysis_complete = False
        st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>🚀 Powered by Streamlit | Built for Relevance Analysis</p>
    <p><small>Processing time: ~45 seconds | Please be patient during analysis</small></p>
</div>
""", unsafe_allow_html=True)

# Sidebar with additional information
with st.sidebar:
    st.markdown("### 🛠️ Configuration")
    
    # API endpoint display (read-only)
    st.text_input(
        "API Endpoint",
        value=GRADIO_URL,
        disabled=True,
        help="Current API endpoint being used"
    )
    
    st.markdown("### ⏱️ Performance Info")
    st.markdown("""
    - **Processing Time**: ~45 seconds
    - **Connection**: Gradio Client
    - **Status Updates**: Real-time progress
    """)
    
    st.markdown("### 📋 Tips")
    st.markdown("""
    - **Be patient**: Analysis takes time for quality results
    - **Don't refresh**: Wait for the process to complete
    - **Check status**: Monitor the progress bar
    - **Stay connected**: Ensure stable internet connection
    """)
    
    st.markdown("### 🔧 Troubleshooting")
    with st.expander("Common Issues"):
        st.markdown("""
        **Long Processing**: Normal, analysis takes ~45 seconds
        
        **Gradio URL Expired**: Restart your Gradio app and update URL
        
        **Connection Lost**: Check internet and API status
        
        **Page Refresh**: Don't refresh during processing
        """)
