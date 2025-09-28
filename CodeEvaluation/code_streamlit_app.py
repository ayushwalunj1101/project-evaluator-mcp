import streamlit as st
import json
import sys
import os
import tempfile
import base64
from datetime import datetime
from typing import Dict, Any
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import plotly.io as pio
pio.templates.default = "plotly_dark"


# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import MCP server functions
from code_mcp_server import CodeAnalyzer, generate_html_report

# Page configuration
st.set_page_config(
    page_title="Advanced Code Analysis Dashboard",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

def run_comprehensive_analysis(repo_url: str) -> Dict[str, Any]:
    """Run comprehensive code analysis"""
    analyzer = CodeAnalyzer()
    try:
        repo_path = analyzer.clone_repository(repo_url)
        
        # Get repository info and detect languages
        repo_info = analyzer.get_repository_info(repo_path)
        languages = repo_info.get('languages_detected', {})
        
        # Perform all analyses
        security_results = analyzer.analyze_security_comprehensive(repo_path, languages)
        quality_results = analyzer.analyze_quality_comprehensive(repo_path, languages)
        architecture_results = analyzer.analyze_architecture(repo_path, languages)
        
        # Calculate overall score
        security_score = security_results.get('security_score', 0)
        quality_score = quality_results.get('quality_score', 0)
        architecture_score = architecture_results.get('architecture_score', 0)
        overall_score = (security_score + quality_score + architecture_score) // 3
        
        return {
            "repository_info": repo_info,
            "security_analysis": security_results,
            "quality_analysis": quality_results,
            "architecture_analysis": architecture_results,
            "overall_score": overall_score,
            "timestamp": datetime.now().isoformat(),
            "success": True
        }
    except Exception as e:
        return {"error": str(e), "success": False}
    finally:
        analyzer.cleanup()

def create_score_gauge(score: int, title: str) -> go.Figure:
    """Create a gauge chart for scores"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title},
        delta = {'reference': 80},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, 80], 'color': "gray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(height=300)
    return fig

def create_language_chart(languages: Dict[str, int]) -> go.Figure:
    """Create pie chart for programming languages"""
    if not languages:
        return None
    
    df = pd.DataFrame(list(languages.items()), columns=['Language', 'Files'])
    fig = px.pie(df, values='Files', names='Language', title='Programming Languages Distribution')
    return fig

def display_detailed_security_analysis(security_data: Dict[str, Any]):
    """Display comprehensive security analysis with detailed findings"""
    st.subheader("🔒 Security Analysis")
    
    score = security_data.get("security_score", 0)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        fig = create_score_gauge(score, "Security Score")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.metric("Security Score", f"{score}/100")
        
        # Risk level indicator
        if score >= 80:
            st.success("🟢 Low Risk Level")
        elif score >= 60:
            st.warning("🟡 Medium Risk Level")
        else:
            st.error("🔴 High Risk Level")
    
    # Detailed Security Issues
    static_analysis = security_data.get('static_analysis', {})
    if 'results' in static_analysis and static_analysis['results']:
        st.subheader("🐛 Security Vulnerabilities & Bugs")
        
        issues = static_analysis['results']
        high_issues = [i for i in issues if i.get('issue_severity') == 'HIGH']
        medium_issues = [i for i in issues if i.get('issue_severity') == 'MEDIUM']
        low_issues = [i for i in issues if i.get('issue_severity') == 'LOW']
        
        # Summary metrics
        col_h, col_m, col_l = st.columns(3)
        with col_h:
            st.metric("🔴 High Severity", len(high_issues))
        with col_m:
            st.metric("🟡 Medium Severity", len(medium_issues))
        with col_l:
            st.metric("🟢 Low Severity", len(low_issues))
        
        # Detailed issue breakdown
        if high_issues:
            with st.expander(f"🔴 High Severity Issues ({len(high_issues)})", expanded=True):
                for idx, issue in enumerate(high_issues[:10], 1):  # Show first 10
                    st.error(f"**Issue #{idx}:** {issue.get('test_name', 'Unknown')}")
                    st.write(f"**File:** `{issue.get('filename', 'Unknown')}`")
                    st.write(f"**Line:** {issue.get('line_number', 'N/A')}")
                    st.write(f"**Description:** {issue.get('issue_text', 'No description')}")
                    st.write(f"**Confidence:** {issue.get('issue_confidence', 'Unknown')}")
                    st.write("---")
        
        if medium_issues:
            with st.expander(f"🟡 Medium Severity Issues ({len(medium_issues)})"):
                for idx, issue in enumerate(medium_issues[:10], 1):
                    st.warning(f"**Issue #{idx}:** {issue.get('test_name', 'Unknown')}")
                    st.write(f"**File:** `{issue.get('filename', 'Unknown')}`")
                    st.write(f"**Line:** {issue.get('line_number', 'N/A')}")
                    st.write(f"**Description:** {issue.get('issue_text', 'No description')}")
                    st.write("---")
        
        if low_issues:
            with st.expander(f"🟢 Low Severity Issues ({len(low_issues)})"):
                for idx, issue in enumerate(low_issues[:5], 1):  # Show first 5
                    st.info(f"**Issue #{idx}:** {issue.get('test_name', 'Unknown')}")
                    st.write(f"**File:** `{issue.get('filename', 'Unknown')}`")
                    st.write(f"**Line:** {issue.get('line_number', 'N/A')}")
                    st.write("---")
    else:
        st.success("✅ No security vulnerabilities detected!")
    
    # Exposed Secrets & API Keys
    secrets_analysis = security_data.get('secrets_analysis', {})
    if secrets_analysis and not secrets_analysis.get('error'):
        st.subheader("🔑 Exposed Secrets & API Keys")
        total_secrets = secrets_analysis.get('total_secrets', 0)
        
        if total_secrets > 0:
            risk_level = secrets_analysis.get('risk_level', 'MEDIUM')
            if risk_level == 'HIGH':
                st.error(f"🚨 CRITICAL: Found {total_secrets} potential secrets in the codebase!")
            elif risk_level == 'MEDIUM':
                st.warning(f"⚠️ WARNING: Found {total_secrets} potential secrets in the codebase!")
            else:
                st.info(f"ℹ️ INFO: Found {total_secrets} potential secrets in the codebase!")
            
            with st.expander("📋 View Detected Secrets Details", expanded=True):
                secrets_found = secrets_analysis.get('secrets_found', [])
                for idx, secret in enumerate(secrets_found, 1):
                    st.write(f"**🔍 Secret #{idx}**")
                    st.write(f"📁 **File:** `{secret.get('file', 'Unknown file')}`")
                    st.write(f"🎯 **Type:** {secret.get('type', 'Unknown type')}")
                    st.write(f"📊 **Matches:** {secret.get('matches', 0)} potential secrets")
                    st.write("**⚠️ Action Required:** Remove or secure these secrets immediately!")
                    st.write("---")
                
                # Recommendations for secrets
                st.subheader("🛡️ Security Recommendations for Secrets")
                st.write("""
                1. **Remove hardcoded secrets** from your source code
                2. **Use environment variables** for sensitive data
                3. **Implement secret management** tools (AWS Secrets Manager, Azure Key Vault, etc.)
                4. **Add .env files to .gitignore**
                5. **Rotate compromised keys** immediately
                6. **Use secret scanning tools** in your CI/CD pipeline
                """)
        else:
            st.success("✅ No exposed secrets detected!")
    
    # Dependency Vulnerabilities
    dependency_analysis = security_data.get('dependency_analysis', {})
    if dependency_analysis and not dependency_analysis.get('error'):
        st.subheader("📦 Dependency Vulnerabilities")
        total_vulns = dependency_analysis.get('total_vulnerabilities', 0)
        
        if total_vulns > 0:
            st.error(f"⚠️ Found {total_vulns} dependency vulnerabilities!")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🔴 High Severity", dependency_analysis.get('high_severity', 0))
            with col2:
                st.metric("🟡 Medium Severity", dependency_analysis.get('medium_severity', 0))
            with col3:
                st.metric("🟢 Low Severity", dependency_analysis.get('low_severity', 0))
            
            # Detailed vulnerability list
            vulnerabilities = dependency_analysis.get('vulnerabilities', [])
            if vulnerabilities:
                with st.expander(f"📋 Vulnerability Details ({len(vulnerabilities)})", expanded=True):
                    for idx, vuln in enumerate(vulnerabilities, 1):
                        severity_color = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(vuln.get('severity', 'unknown'), "⚪")
                        st.write(f"**{severity_color} Vulnerability #{idx}**")
                        st.write(f"📦 **Package:** {vuln.get('package', 'Unknown')}")
                        st.write(f"⚠️ **Severity:** {vuln.get('severity', 'Unknown').upper()}")
                        st.write(f"📄 **Title:** {vuln.get('title', 'No title')}")
                        st.write("---")
        else:
            st.success("✅ No known vulnerabilities in dependencies!")

def display_detailed_quality_analysis(quality_data: Dict[str, Any]):
    """Display comprehensive quality analysis with detailed findings"""
    st.subheader("⚡ Code Quality Analysis")
    
    score = quality_data.get("quality_score", 0)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        fig = create_score_gauge(score, "Quality Score")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.metric("Quality Score", f"{score}/100")
        
        # Quality level indicator
        if score >= 85:
            st.success("🟢 Excellent Quality")
        elif score >= 70:
            st.info("🔵 Good Quality")
        elif score >= 50:
            st.warning("🟡 Needs Improvement")
        else:
            st.error("🔴 Poor Quality")
    
    # Detailed Code Quality Issues
    code_quality = quality_data.get('code_quality', {})
    pylint_issues = code_quality.get('pylint_issues', [])
    
    if isinstance(pylint_issues, list) and pylint_issues:
        st.subheader("🐛 Code Quality Issues")
        
        errors = [i for i in pylint_issues if i.get('type') == 'error']
        warnings = [i for i in pylint_issues if i.get('type') == 'warning']
        conventions = [i for i in pylint_issues if i.get('type') == 'convention']
        refactors = [i for i in pylint_issues if i.get('type') == 'refactor']
        
        # Summary metrics
        col_e, col_w, col_c, col_r = st.columns(4)
        with col_e:
            st.metric("🔴 Errors", len(errors))
        with col_w:
            st.metric("🟡 Warnings", len(warnings))
        with col_c:
            st.metric("🔵 Conventions", len(conventions))
        with col_r:
            st.metric("🟢 Refactor", len(refactors))
        
        # Detailed issue breakdown
        if errors:
            with st.expander(f"🔴 Errors ({len(errors)})", expanded=True):
                for idx, error in enumerate(errors[:10], 1):
                    st.error(f"**Error #{idx}:** {error.get('message', 'Unknown error')}")
                    st.write(f"**File:** `{error.get('path', 'Unknown')}`")
                    st.write(f"**Line:** {error.get('line', 'N/A')}")
                    st.write(f"**Symbol:** {error.get('symbol', 'N/A')}")
                    st.write("---")
        
        if warnings:
            with st.expander(f"🟡 Warnings ({len(warnings)})"):
                for idx, warning in enumerate(warnings[:10], 1):
                    st.warning(f"**Warning #{idx}:** {warning.get('message', 'Unknown warning')}")
                    st.write(f"**File:** `{warning.get('path', 'Unknown')}`")
                    st.write(f"**Line:** {warning.get('line', 'N/A')}")
                    st.write("---")
        
        if conventions:
            with st.expander(f"🔵 Convention Issues ({len(conventions)})"):
                for idx, conv in enumerate(conventions[:5], 1):
                    st.info(f"**Convention #{idx}:** {conv.get('message', 'Unknown')}")
                    st.write(f"**File:** `{conv.get('path', 'Unknown')}`")
                    st.write("---")
    else:
        st.success("✅ No code quality issues detected!")
    
    # Test Coverage Analysis
    test_coverage = quality_data.get('test_coverage', {})
    if test_coverage and not test_coverage.get('error'):
        st.subheader("🧪 Test Coverage Analysis")
        
        coverage_pct = test_coverage.get('coverage_percentage', 0)
        test_files = test_coverage.get('test_files', 0)
        source_files = test_coverage.get('source_files', 0)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Coverage Percentage", f"{coverage_pct:.1f}%")
        with col2:
            st.metric("Test Files", test_files)
        with col3:
            st.metric("Source Files", source_files)
        
        # Coverage recommendations
        if coverage_pct < 50:
            st.error("🔴 Critical: Very low test coverage!")
            st.write("**Recommendations:**")
            st.write("- Add unit tests for critical functions")
            st.write("- Implement integration testing")
            st.write("- Set up automated testing in CI/CD")
        elif coverage_pct < 80:
            st.warning("🟡 Warning: Test coverage below recommended level")
            st.write("**Recommendations:**")
            st.write("- Increase test coverage to 80%+")
            st.write("- Focus on testing edge cases")
        else:
            st.success("✅ Good test coverage!")
        
        # Coverage gauge
        fig = create_score_gauge(int(coverage_pct), "Test Coverage")
        st.plotly_chart(fig, use_container_width=True)
    
    # Code Duplication Analysis
    duplication_analysis = quality_data.get('duplication_analysis', {})
    if duplication_analysis and not duplication_analysis.get('error'):
        st.subheader("🔄 Code Duplication Analysis")
        
        total_duplications = duplication_analysis.get('total_duplications', 0)
        duplication_score = duplication_analysis.get('duplication_score', 100)
        duplications_found = duplication_analysis.get('duplications_found', [])
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Duplications", total_duplications)
        with col2:
            st.metric("Duplication Score", f"{duplication_score}/100")
        
        if total_duplications > 0:
            st.warning(f"Found {total_duplications} code duplication issues")
            
            if duplications_found:
                with st.expander("📋 Duplication Details"):
                    for idx, dup in enumerate(duplications_found[:5], 1):
                        st.write(f"**Duplication #{idx}**")
                        st.write(f"**Message:** {dup.get('message', 'Unknown')}")
                        st.write(f"**File:** {dup.get('path', 'Unknown')}")
                        st.write("---")
        else:
            st.success("✅ No significant code duplication detected!")

def display_architecture_analysis(architecture_data: Dict[str, Any]):
    """Display architecture analysis"""
    st.subheader("🏗️ Architecture Analysis")
    
    score = architecture_data.get("architecture_score", 0)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        fig = create_score_gauge(score, "Architecture Score")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.metric("Architecture Score", f"{score}/100")
        
        # Architecture quality indicator
        if score >= 80:
            st.success("🟢 Well Structured")
        elif score >= 60:
            st.info("🔵 Moderately Structured")
        else:
            st.warning("🟡 Needs Better Structure")
    
    # Design patterns
    design_patterns = architecture_data.get('design_patterns', [])
    if design_patterns:
        st.subheader("🎨 Design Patterns Detected")
        col1, col2 = st.columns(2)
        
        for idx, pattern in enumerate(design_patterns):
            if idx % 2 == 0:
                with col1:
                    st.success(f"✅ {pattern}")
            else:
                with col2:
                    st.success(f"✅ {pattern}")
        
        st.info(f"💡 **Great!** Your code implements {len(design_patterns)} design patterns, showing good architectural practices.")
    else:
        st.info("💡 No common design patterns detected. Consider implementing design patterns for better code structure.")
    
    # Project structure
    project_structure = architecture_data.get('project_structure', {})
    if project_structure:
        st.subheader("📁 Project Structure Analysis")
        
        structure_data = []
        total_dirs = 0
        total_files = 0
        
        for folder, data in project_structure.items():
            dirs = data.get('directories', 0)
            files = data.get('files', 0)
            total_dirs += dirs
            total_files += files
            
            structure_data.append({
                'Folder': folder,
                'Directories': dirs,
                'Files': files,
                'File Types': len(data.get('file_types', {}))
            })
        
        if structure_data:
            df = pd.DataFrame(structure_data)
            st.dataframe(df, use_container_width=True)
            
            # Structure insights
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Directories", total_dirs)
            with col2:
                st.metric("Total Files", total_files)
            with col3:
                st.metric("Directory Depth", len(project_structure))
            
            # Structure recommendations
            if len(project_structure) < 3:
                st.warning("💡 Consider organizing your code into more structured directories")
            else:
                st.success("✅ Good directory structure organization")

def generate_comprehensive_recommendations(results: Dict[str, Any]):
    """Generate comprehensive recommendations based on analysis results"""
    st.subheader("💡 Comprehensive Recommendations")
    
    security = results.get("security_analysis", {})
    quality = results.get("quality_analysis", {})
    architecture = results.get("architecture_analysis", {})
    overall_score = results.get("overall_score", 0)
    
    recommendations = []
    
    # Security recommendations
    security_score = security.get('security_score', 0)
    if security_score < 70:
        recommendations.append({
            "category": "🔒 Security",
            "priority": "HIGH",
            "title": "Address Security Vulnerabilities",
            "description": "Your code has security issues that need immediate attention.",
            "actions": [
                "Review and fix high-severity security issues",
                "Implement input validation and sanitization",
                "Use secure coding practices",
                "Regular security audits"
            ]
        })
    
    secrets_found = security.get('secrets_analysis', {}).get('total_secrets', 0)
    if secrets_found > 0:
        recommendations.append({
            "category": "🔑 Secrets Management",
            "priority": "CRITICAL",
            "title": "Remove Exposed Secrets",
            "description": f"Found {secrets_found} potential secrets in your codebase.",
            "actions": [
                "Remove all hardcoded secrets immediately",
                "Use environment variables for sensitive data",
                "Implement proper secret management tools",
                "Rotate any compromised keys",
                "Add secret scanning to CI/CD pipeline"
            ]
        })
    
    # Quality recommendations
    quality_score = quality.get('quality_score', 0)
    if quality_score < 70:
        recommendations.append({
            "category": "⚡ Code Quality",
            "priority": "MEDIUM",
            "title": "Improve Code Quality",
            "description": "Code quality can be significantly improved.",
            "actions": [
                "Fix linting errors and warnings",
                "Reduce code complexity",
                "Implement code review process",
                "Use automated code formatting tools"
            ]
        })
    
    test_coverage = quality.get('test_coverage', {}).get('coverage_percentage', 0)
    if test_coverage < 80:
        recommendations.append({
            "category": "🧪 Testing",
            "priority": "HIGH" if test_coverage < 50 else "MEDIUM",
            "title": "Increase Test Coverage",
            "description": f"Current test coverage is {test_coverage:.1f}%.",
            "actions": [
                "Write unit tests for core functions",
                "Implement integration testing",
                "Add end-to-end testing",
                "Set up automated testing in CI/CD",
                "Aim for 80%+ test coverage"
            ]
        })
    
    # Architecture recommendations
    architecture_score = architecture.get('architecture_score', 0)
    if architecture_score < 70:
        recommendations.append({
            "category": "🏗️ Architecture",
            "priority": "MEDIUM",
            "title": "Improve Project Structure",
            "description": "Project architecture can be enhanced.",
            "actions": [
                "Organize code into logical modules",
                "Implement design patterns",
                "Improve separation of concerns",
                "Add proper documentation"
            ]
        })
    
    # Overall recommendations
    if overall_score > 85:
        recommendations.append({
            "category": "🎉 Excellent Work",
            "priority": "INFO",
            "title": "Maintain High Standards",
            "description": "Your code meets high quality standards!",
            "actions": [
                "Continue following best practices",
                "Regular code reviews",
                "Keep dependencies updated",
                "Monitor for new security vulnerabilities"
            ]
        })
    
    # Display recommendations
    for idx, rec in enumerate(recommendations, 1):
        priority_color = {
            "CRITICAL": "🔴",
            "HIGH": "🟠",
            "MEDIUM": "🟡",
            "LOW": "🟢",
            "INFO": "🔵"
        }.get(rec["priority"], "⚪")
        
        with st.expander(f"{priority_color} {rec['category']}: {rec['title']}", expanded=(rec["priority"] in ["CRITICAL", "HIGH"])):
            st.write(f"**Priority:** {rec['priority']}")
            st.write(f"**Description:** {rec['description']}")
            st.write("**Recommended Actions:**")
            for action in rec["actions"]:
                st.write(f"• {action}")

def display_repository_info(repo_data: Dict[str, Any]):
    """Display repository information"""
    st.subheader("📊 Repository Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Commits", repo_data.get("total_commits", 0))
    with col2:
        st.metric("Lines of Code", repo_data.get("total_lines_of_code", 0))
    with col3:
        st.metric("File Types", len(repo_data.get("file_types", {})))
    with col4:
        st.metric("Primary Language", repo_data.get("primary_language", "Unknown"))
    
    # Languages distribution
    languages = repo_data.get("languages_detected", {})
    if languages:
        st.subheader("💻 Programming Languages")
        fig = create_language_chart(languages)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    # File types breakdown
    file_types = repo_data.get("file_types", {})
    if file_types:
        st.subheader("📄 File Types Distribution")
        sorted_types = sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Create a nice display for file types
        file_type_data = []
        for ext, count in sorted_types:
            percentage = (count / sum(file_types.values())) * 100
            file_type_data.append({
                'Extension': ext,
                'Files': count,
                'Percentage': f"{percentage:.1f}%"
            })
        
        df = pd.DataFrame(file_type_data)
        st.dataframe(df, use_container_width=True)

def generate_downloadable_report(analysis_results: Dict[str, Any], format_type: str) -> str:
    """Generate downloadable report"""
    if format_type.lower() == "json":
        return json.dumps(analysis_results, indent=2)
    elif format_type.lower() == "html":
        # Generate summary for HTML report
        repo_info = analysis_results.get("repository_info", {})
        security = analysis_results.get("security_analysis", {})
        quality = analysis_results.get("quality_analysis", {})
        architecture = analysis_results.get("architecture_analysis", {})
        
        overall_score = analysis_results.get("overall_score", 0)
        security_score = security.get('security_score', 0)
        quality_score = quality.get('quality_score', 0)
        architecture_score = architecture.get('architecture_score', 0)
        
        # Generate recommendations (this was missing!)
        recommendations = []
        
        # Security recommendations
        if security_score < 70:
            recommendations.append("🔒 Address security vulnerabilities and implement security best practices")
        
        secrets_found = security.get('secrets_analysis', {}).get('total_secrets', 0)
        if secrets_found > 0:
            recommendations.append("🔑 Remove exposed secrets and implement proper secret management")
        
        # Quality recommendations
        if quality_score < 70:
            recommendations.append("⚡ Improve code quality by fixing linting issues and reducing complexity")
        
        test_coverage = quality.get('test_coverage', {}).get('coverage_percentage', 0)
        if test_coverage < 50:
            recommendations.append("🧪 Increase test coverage to improve code reliability")
        
        # Architecture recommendations
        if architecture_score < 70:
            recommendations.append("🏗️ Improve project structure and implement design patterns")
        
        if overall_score > 85:
            recommendations.append("🎉 Excellent work! Your code meets high standards across all areas")
        
        # Create report structure (now includes recommendations)
        report = {
            "executive_summary": {
                "overall_score": overall_score,
                "overall_grade": "A" if overall_score > 90 else "B" if overall_score > 80 else "C" if overall_score > 70 else "D" if overall_score > 60 else "F",
                "primary_language": repo_info.get("primary_language", "Unknown"),
                "total_files": len(repo_info.get("file_types", {})),
                "total_lines": repo_info.get("total_lines_of_code", 0)
            },
            "detailed_scores": {
                "security_score": security_score,
                "quality_score": quality_score,
                "architecture_score": architecture_score
            },
            "key_findings": {
                "security_issues": security.get('static_analysis', {}).get('results', []),
                "quality_issues": quality.get('code_quality', {}).get('pylint_issues', []),
                "secrets_detected": security.get('secrets_analysis', {}).get('total_secrets', 0),
                "vulnerabilities": security.get('dependency_analysis', {}).get('total_vulnerabilities', 0),
                "test_coverage": quality.get('test_coverage', {}).get('coverage_percentage', 0),
                "design_patterns": architecture.get('design_patterns', [])
            },
            "recommendations": recommendations,  # Added this line!
            "technical_details": {
                "languages_detected": repo_info.get("languages_detected", {}),
                "repository_url": repo_info.get("repository_url", ""),
                "analysis_timestamp": analysis_results.get("timestamp", "")
            }
        }
        
        return generate_html_report(report)


def create_download_button(content: str, filename: str, format_type: str):
    """Create download button for reports"""
    if format_type.lower() == "json":
        mime_type = "application/json"
    elif format_type.lower() == "html":
        mime_type = "text/html"
    else:
        mime_type = "text/plain"
    
    st.download_button(
        label=f"📥 Download {format_type.upper()} Report",
        data=content,
        file_name=filename,
        mime=mime_type
    )

def main():
    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 1rem 1rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    .stAlert {
        margin: 1rem 0;
    }
    .recommendation-high {
        border-left: 4px solid #ff4444;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: #fff5f5;
    }
    .recommendation-medium {
        border-left: 4px solid #ffaa00;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: #fffbf0;
    }
    .recommendation-low {
        border-left: 4px solid #00aa00;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: #f0fff4;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🔍 Advanced Code Analysis Dashboard</h1>
        <p>Comprehensive Security, Quality & Architecture Analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("🛠️ Configuration")
    repo_url = st.sidebar.text_input(
        "GitHub Repository URL",
        placeholder="https://github.com/user/repo",
        help="Enter the full GitHub repository URL"
    )
    
    # Analysis options
    st.sidebar.subheader("📋 Analysis Options")
    include_security = st.sidebar.checkbox("🔒 Security Analysis", value=True)
    include_quality = st.sidebar.checkbox("⚡ Quality Analysis", value=True)
    include_architecture = st.sidebar.checkbox("🏗️ Architecture Analysis", value=True)
    show_recommendations = st.sidebar.checkbox("💡 Show Recommendations", value=True)
    
    # Report format
    st.sidebar.subheader("📄 Report Format")
    report_format = st.sidebar.selectbox("Choose format", ["JSON", "HTML"])
    
    analyze_button = st.sidebar.button("🚀 Start Analysis", type="primary")
    
    # Main content
    if analyze_button and repo_url:
        if not repo_url.startswith(('https://github.com/', 'git@github.com:')):
            st.error("Please enter a valid GitHub repository URL")
            return
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("🔄 Cloning repository...")
        progress_bar.progress(10)
        
        with st.spinner("Running comprehensive analysis... This may take several minutes."):
            results = run_comprehensive_analysis(repo_url)
            progress_bar.progress(100)
            
            if not results.get("success", False):
                st.error(f"Analysis failed: {results.get('error', 'Unknown error')}")
                return
            
            status_text.text("✅ Analysis complete!")
            
            # Display results
            if "error" in results:
                st.error(f"Analysis error: {results['error']}")
                return
            
            # Summary section
            st.success("🎉 Analysis Complete!")
            
            overall_score = results.get("overall_score", 0)
            security_score = results.get("security_analysis", {}).get("security_score", 0)
            quality_score = results.get("quality_analysis", {}).get("quality_score", 0)
            architecture_score = results.get("architecture_analysis", {}).get("architecture_score", 0)
            
            # Overall metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                grade = "A" if overall_score > 90 else "B" if overall_score > 80 else "C" if overall_score > 70 else "D" if overall_score > 60 else "F"
                if grade in ["A", "B"]:
                    st.success(f"Overall Grade: {grade}")
                elif grade == "C":
                    st.warning(f"Overall Grade: {grade}")
                else:
                    st.error(f"Overall Grade: {grade}")
            
            with col2:
                st.metric("Overall Score", f"{overall_score}/100")
            with col3:
                st.metric("Security Score", f"{security_score}/100")
            with col4:
                st.metric("Quality Score", f"{quality_score}/100")
            
            # Generate and display download buttons
            st.subheader("📥 Download Reports")
            col1, col2 = st.columns(2)
            
            with col1:
                json_report = generate_downloadable_report(results, "json")
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                create_download_button(json_report, f"code_analysis_report_{timestamp}.json", "json")
            
            with col2:
                html_report = generate_downloadable_report(results, "html")
                create_download_button(html_report, f"code_analysis_report_{timestamp}.html", "html")
            
            # Detailed analysis sections
            st.markdown("---")
            
            # Repository info
            repo_info = results.get("repository_info", {})
            if repo_info and "error" not in repo_info:
                display_repository_info(repo_info)
                st.markdown("---")
            
            # Security analysis with detailed findings
            if include_security:
                security_analysis = results.get("security_analysis", {})
                if security_analysis and "error" not in security_analysis:
                    display_detailed_security_analysis(security_analysis)
                    st.markdown("---")
            
            # Quality analysis with detailed findings
            if include_quality:
                quality_analysis = results.get("quality_analysis", {})
                if quality_analysis and "error" not in quality_analysis:
                    display_detailed_quality_analysis(quality_analysis)
                    st.markdown("---")
            
            # Architecture analysis
            if include_architecture:
                architecture_analysis = results.get("architecture_analysis", {})
                if architecture_analysis and "error" not in architecture_analysis:
                    display_architecture_analysis(architecture_analysis)
                    st.markdown("---")
            
            # Comprehensive recommendations
            if show_recommendations:
                generate_comprehensive_recommendations(results)
                st.markdown("---")
            
            # Raw data expander
            with st.expander("📋 Raw Analysis Data"):
                st.json(results)
    
    elif analyze_button:
        st.error("Please enter a repository URL")
    
    # Sidebar information
    st.sidebar.markdown("---")
    st.sidebar.subheader("ℹ️ Enhanced Features")
    st.sidebar.write("""
    **🔍 Detailed Analysis:**
    - Security vulnerabilities with exact locations
    - Exposed API keys and secrets
    - Code quality issues breakdown
    - Comprehensive recommendations
    
    **📊 Rich Visualizations:**
    - Interactive gauge charts
    - Detailed issue listings
    - Priority-based recommendations
    - File structure analysis
    """)

if __name__ == "__main__":
    main()
