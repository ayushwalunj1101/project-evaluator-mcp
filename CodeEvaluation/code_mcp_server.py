import os
import json
import tempfile
import subprocess
import shutil
import stat
from pathlib import Path
from typing import Dict, List, Any, Optional
import git
from fastmcp import FastMCP
from datetime import datetime
import re

# Initialize MCP server
mcp = FastMCP("Code Analysis Server")

class LanguageDetector:
    LANGUAGE_TOOLS = {
        'python': {
            'security': ['bandit', 'safety', 'semgrep'],
            'quality': ['pylint', 'flake8', 'mypy', 'black'],
            'complexity': ['radon', 'mccabe'],
            'coverage': ['coverage', 'pytest-cov']
        },
        'javascript': {
            'security': ['eslint-security', 'npm audit', 'semgrep'],
            'quality': ['eslint', 'jshint', 'prettier'],
            'complexity': ['complexity-report', 'jscpd'],
            'coverage': ['nyc', 'istanbul']
        },
        'java': {
            'security': ['spotbugs', 'dependency-check', 'semgrep'],
            'quality': ['checkstyle', 'pmd', 'spotless'],
            'complexity': ['metrics-maven-plugin'],
            'coverage': ['jacoco', 'cobertura']
        },
        'go': {
            'security': ['gosec', 'nancy', 'semgrep'],
            'quality': ['golint', 'gofmt', 'go vet'],
            'complexity': ['gocyclo'],
            'coverage': ['go test -cover']
        },
        'rust': {
            'security': ['cargo-audit', 'semgrep'],
            'quality': ['clippy', 'rustfmt'],
            'complexity': ['cargo-complexity'],
            'coverage': ['tarpaulin']
        }
    }

    @staticmethod
    def detect_languages(repo_path: str) -> Dict[str, int]:
        """Detect programming languages in repository"""
        language_counts = {}
        
        extensions_map = {
            '.py': 'python',
            '.js': 'javascript', '.jsx': 'javascript', '.ts': 'javascript', '.tsx': 'javascript',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.cpp': 'cpp', '.c': 'cpp', '.h': 'cpp', '.hpp': 'cpp',
            '.cs': 'csharp',
            '.rb': 'ruby',
            '.php': 'php'
        }
        
        for file_path in Path(repo_path).rglob("*"):
            if file_path.is_file() and not any(ignore in str(file_path) for ignore in ['.git', '__pycache__', 'node_modules']):
                ext = file_path.suffix.lower()
                if ext in extensions_map:
                    lang = extensions_map[ext]
                    language_counts[lang] = language_counts.get(lang, 0) + 1
        
        return language_counts

class SecurityAnalyzer:
    @staticmethod
    def analyze_secrets(repo_path: str) -> Dict[str, Any]:
        """Detect exposed secrets, API keys, passwords with enhanced details"""
        try:
            # Enhanced patterns with descriptions
            secrets_patterns = [
                (r'(?i)(api[_-]?key|secret[_-]?key|access[_-]?token)\s*[:=]\s*["\']?([a-zA-Z0-9_-]{20,})["\']?', 'API Key/Secret'),
                (r'(?i)(password|passwd|pwd)\s*[:=]\s*["\']?([^\s"\']{8,})["\']?', 'Password'),
                (r'["\']?[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}["\']?', 'UUID/Token'),
                (r'(?i)github[_-]?token\s*[:=]\s*["\']?([a-zA-Z0-9_]{40})["\']?', 'GitHub Token'),
                (r'(?i)aws[_-]?access[_-]?key[_-]?id\s*[:=]\s*["\']?([A-Z0-9]{20})["\']?', 'AWS Access Key'),
                (r'(?i)jwt[_-]?token\s*[:=]\s*["\']?([A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*)["\']?', 'JWT Token'),
                (r'(?i)(private[_-]?key|secret[_-]?key)\s*[:=]\s*["\']?([A-Za-z0-9+/=]{100,})["\']?', 'Private Key'),
                (r'(?i)slack[_-]?token\s*[:=]\s*["\']?(xox[a-zA-Z]-[a-zA-Z0-9-]+)["\']?', 'Slack Token'),
                (r'(?i)discord[_-]?token\s*[:=]\s*["\']?([A-Za-z0-9_-]{24}\.[A-Za-z0-9_-]{6}\.[A-Za-z0-9_-]{27})["\']?', 'Discord Token')
            ]
            
            secrets_found = []
            
            for file_path in Path(repo_path).rglob("*"):
                if file_path.is_file() and file_path.suffix in ['.py', '.js', '.java', '.go', '.rs', '.env', '.config', '.yml', '.yaml', '.json', '.xml']:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                            for line_num, line in enumerate(lines, 1):
                                for pattern, secret_type in secrets_patterns:
                                    matches = re.findall(pattern, line)
                                    if matches:
                                        # Mask the actual secret for display
                                        masked_line = line.strip()
                                        for match in matches:
                                            if isinstance(match, tuple):
                                                for part in match:
                                                    if len(part) > 4:
                                                        masked_line = masked_line.replace(part, part[:4] + '*' * (len(part) - 4))
                                            else:
                                                if len(match) > 4:
                                                    masked_line = masked_line.replace(match, match[:4] + '*' * (len(match) - 4))
                                        
                                        secrets_found.append({
                                            'file': str(file_path.relative_to(repo_path)),
                                            'line': line_num,
                                            'type': secret_type,
                                            'matches': len(matches),
                                            'context': masked_line[:100] + '...' if len(masked_line) > 100 else masked_line,
                                            'severity': 'HIGH' if secret_type in ['AWS Access Key', 'GitHub Token', 'Private Key'] else 'MEDIUM'
                                        })
                    except Exception:
                        continue
            
            return {
                'secrets_found': secrets_found,
                'total_secrets': len(secrets_found),
                'high_severity_secrets': len([s for s in secrets_found if s.get('severity') == 'HIGH']),
                'medium_severity_secrets': len([s for s in secrets_found if s.get('severity') == 'MEDIUM']),
                'risk_level': 'HIGH' if len(secrets_found) > 5 else 'MEDIUM' if len(secrets_found) > 0 else 'LOW',
                'files_affected': len(set([s['file'] for s in secrets_found]))
            }
        except Exception as e:
            return {'error': f'Secret analysis failed: {str(e)}'}

    @staticmethod
    def analyze_dependencies(repo_path: str, language: str) -> Dict[str, Any]:
        """Analyze dependency vulnerabilities with enhanced error handling"""
        try:
            vulnerabilities = []
            
            if language == 'python':
                # Check requirements.txt and setup.py
                req_files = list(Path(repo_path).glob('requirements*.txt'))
                req_files.extend(list(Path(repo_path).glob('setup.py')))
                
                for req_file in req_files:
                    try:
                        result = subprocess.run([
                            'safety', 'check', '-r', str(req_file), '--json'
                        ], capture_output=True, text=True, timeout=120)
                        
                        if result.stdout:
                            try:
                                safety_data = json.loads(result.stdout)
                                if isinstance(safety_data, list):
                                    vulnerabilities.extend(safety_data)
                                elif isinstance(safety_data, dict) and 'vulnerabilities' in safety_data:
                                    vulnerabilities.extend(safety_data['vulnerabilities'])
                            except json.JSONDecodeError:
                                pass
                    except FileNotFoundError:
                        return {'error': 'Safety tool not found. Install with: pip install safety'}
                    except subprocess.TimeoutExpired:
                        return {'error': 'Safety analysis timed out'}
                    except Exception:
                        pass
            
            elif language == 'javascript':
                # Check package.json
                package_json = Path(repo_path) / 'package.json'
                if package_json.exists():
                    try:
                        result = subprocess.run([
                            'npm', 'audit', '--json'
                        ], capture_output=True, text=True, timeout=120, cwd=repo_path)
                        
                        if result.stdout:
                            try:
                                audit_data = json.loads(result.stdout)
                                if 'vulnerabilities' in audit_data:
                                    for vuln_name, vuln_data in audit_data['vulnerabilities'].items():
                                        vulnerabilities.append({
                                            'package': vuln_name,
                                            'severity': vuln_data.get('severity', 'unknown'),
                                            'title': vuln_data.get('title', 'Unknown vulnerability'),
                                            'via': vuln_data.get('via', []),
                                            'range': vuln_data.get('range', 'unknown')
                                        })
                            except json.JSONDecodeError:
                                pass
                    except FileNotFoundError:
                        return {'error': 'npm not found. Make sure Node.js is installed'}
                    except Exception:
                        pass
            
            return {
                'vulnerabilities': vulnerabilities,
                'total_vulnerabilities': len(vulnerabilities),
                'critical_severity': len([v for v in vulnerabilities if v.get('severity') == 'critical']),
                'high_severity': len([v for v in vulnerabilities if v.get('severity') == 'high']),
                'medium_severity': len([v for v in vulnerabilities if v.get('severity') == 'medium']),
                'low_severity': len([v for v in vulnerabilities if v.get('severity') == 'low']),
                'packages_affected': len(set([v.get('package', '') for v in vulnerabilities if v.get('package')]))
            }
        except Exception as e:
            return {'error': f'Dependency analysis failed: {str(e)}'}

class QualityAnalyzer:
    @staticmethod
    def analyze_code_duplication(repo_path: str, language: str) -> Dict[str, Any]:
        """Detect code duplication with enhanced details"""
        try:
            if language == 'python':
                try:
                    result = subprocess.run([
                        'pylint', '--disable=all', '--enable=duplicate-code', 
                        '--output-format=json', '--recursive=y', repo_path
                    ], capture_output=True, text=True, timeout=300)
                    
                    duplications = []
                    if result.stdout:
                        try:
                            pylint_data = json.loads(result.stdout)
                            duplications = [item for item in pylint_data if item.get('message-id') == 'R0801']
                            
                            # Enhance duplication data with more details
                            enhanced_duplications = []
                            for dup in duplications:
                                enhanced_duplications.append({
                                    'message': dup.get('message', ''),
                                    'path': dup.get('path', ''),
                                    'line': dup.get('line', 0),
                                    'column': dup.get('column', 0),
                                    'symbol': dup.get('symbol', ''),
                                    'type': 'duplicate-code',
                                    'severity': 'medium'
                                })
                            duplications = enhanced_duplications
                        except json.JSONDecodeError:
                            pass
                    
                    return {
                        'duplications_found': duplications,
                        'total_duplications': len(duplications),
                        'duplication_score': max(0, 100 - (len(duplications) * 10)),
                        'files_affected': len(set([d.get('path', '') for d in duplications]))
                    }
                except FileNotFoundError:
                    return {'error': 'Pylint not found. Install with: pip install pylint'}
                except subprocess.TimeoutExpired:
                    return {'error': 'Pylint analysis timed out'}
                except Exception as e:
                    return {'error': f'Pylint analysis failed: {str(e)}'}
            
            return {'message': f'Code duplication analysis not implemented for {language}'}
        except Exception as e:
            return {'error': f'Duplication analysis failed: {str(e)}'}

    @staticmethod
    def analyze_test_coverage(repo_path: str, language: str) -> Dict[str, Any]:
        """Analyze test coverage with enhanced metrics"""
        try:
            coverage_data = {}
            
            if language == 'python':
                # Look for test files with more patterns
                test_patterns = ['test_*.py', '*_test.py', 'tests/*.py', 'test/*.py', '**/test_*.py', '**/tests/*.py']
                test_files = []
                
                for pattern in test_patterns:
                    test_files.extend(list(Path(repo_path).rglob(pattern)))
                
                # Remove duplicates
                test_files = list(set(test_files))
                
                # Find source files
                source_files = list(Path(repo_path).rglob('*.py'))
                source_files = [f for f in source_files if not any(test_indicator in str(f).lower() 
                                                                  for test_indicator in ['test', '__pycache__', '.pyc'])]
                
                # Calculate coverage metrics
                total_test_files = len(test_files)
                total_source_files = len(source_files)
                coverage_ratio = total_test_files / max(total_source_files, 1)
                coverage_percentage = min(100, coverage_ratio * 100)
                
                # Analyze test quality
                test_functions = 0
                for test_file in test_files[:10]:  # Check first 10 test files
                    try:
                        with open(test_file, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            test_functions += len(re.findall(r'def test_\w+', content))
                    except:
                        pass
                
                coverage_data = {
                    'test_files': total_test_files,
                    'source_files': total_source_files,
                    'coverage_ratio': coverage_ratio,
                    'coverage_percentage': coverage_percentage,
                    'test_functions': test_functions,
                    'coverage_grade': 'A' if coverage_percentage >= 80 else 'B' if coverage_percentage >= 60 else 'C' if coverage_percentage >= 40 else 'D'
                }
            
            elif language == 'javascript':
                # Look for test files with JS/TS patterns
                test_patterns = ['*.test.js', '*.spec.js', '*.test.ts', '*.spec.ts', 'test/*.js', 'tests/*.js', '__tests__/*.js']
                test_files = []
                
                for pattern in test_patterns:
                    test_files.extend(list(Path(repo_path).rglob(pattern)))
                
                test_files = list(set(test_files))
                
                source_files = list(Path(repo_path).rglob('*.js')) + list(Path(repo_path).rglob('*.ts'))
                source_files = [f for f in source_files if not any(exclude in str(f).lower() 
                                                                  for exclude in ['test', 'node_modules', 'dist', 'build'])]
                
                total_test_files = len(test_files)
                total_source_files = len(source_files)
                coverage_ratio = total_test_files / max(total_source_files, 1)
                coverage_percentage = min(100, coverage_ratio * 100)
                
                coverage_data = {
                    'test_files': total_test_files,
                    'source_files': total_source_files,
                    'coverage_ratio': coverage_ratio,
                    'coverage_percentage': coverage_percentage,
                    'coverage_grade': 'A' if coverage_percentage >= 80 else 'B' if coverage_percentage >= 60 else 'C' if coverage_percentage >= 40 else 'D'
                }
            
            return coverage_data
        except Exception as e:
            return {'error': f'Coverage analysis failed: {str(e)}'}

class CodeAnalyzer:
    def __init__(self):
        self.temp_dir = None
        self.language_detector = LanguageDetector()
        self.security_analyzer = SecurityAnalyzer()
        self.quality_analyzer = QualityAnalyzer()

    def clone_repository(self, repo_url: str) -> str:
        """Clone GitHub repository to temporary directory"""
        self.temp_dir = tempfile.mkdtemp()
        try:
            git.Repo.clone_from(repo_url, self.temp_dir)
            return self.temp_dir
        except Exception as e:
            raise Exception(f"Failed to clone repository: {str(e)}")

    def analyze_security_comprehensive(self, repo_path: str, languages: Dict[str, int]) -> Dict[str, Any]:
        """Comprehensive security analysis with enhanced reporting"""
        primary_language = max(languages.items(), key=lambda x: x[1])[0] if languages else 'unknown'
        
        security_results = {
            'primary_language': primary_language,
            'static_analysis': {},
            'secrets_analysis': {},
            'dependency_analysis': {},
            'security_score': 0
        }
        
        # Static analysis (bandit for Python)
        if primary_language == 'python':
            security_results['static_analysis'] = self.analyze_security_python(repo_path)
        
        # Secrets analysis
        security_results['secrets_analysis'] = self.security_analyzer.analyze_secrets(repo_path)
        
        # Dependency analysis
        security_results['dependency_analysis'] = self.security_analyzer.analyze_dependencies(repo_path, primary_language)
        
        # Calculate overall security score
        security_results['security_score'] = self._calculate_comprehensive_security_score(security_results)
        
        return security_results

    def analyze_quality_comprehensive(self, repo_path: str, languages: Dict[str, int]) -> Dict[str, Any]:
        """Comprehensive quality analysis with enhanced reporting"""
        primary_language = max(languages.items(), key=lambda x: x[1])[0] if languages else 'unknown'
        
        quality_results = {
            'primary_language': primary_language,
            'code_quality': {},
            'complexity_analysis': {},
            'duplication_analysis': {},
            'test_coverage': {},
            'coding_standards': {},
            'quality_score': 0
        }
        
        # Code quality (pylint for Python)
        if primary_language == 'python':
            quality_results['code_quality'] = self.analyze_quality_python(repo_path)
        
        # Duplication analysis
        quality_results['duplication_analysis'] = self.quality_analyzer.analyze_code_duplication(repo_path, primary_language)
        
        # Test coverage
        quality_results['test_coverage'] = self.quality_analyzer.analyze_test_coverage(repo_path, primary_language)
        
        # Calculate overall quality score
        quality_results['quality_score'] = self._calculate_comprehensive_quality_score(quality_results)
        
        return quality_results

    def analyze_architecture(self, repo_path: str, languages: Dict[str, int]) -> Dict[str, Any]:
        """Analyze software architecture and structure with enhanced details"""
        try:
            architecture_data = {
                'project_structure': {},
                'dependency_graph': {},
                'design_patterns': {},
                'architecture_score': 0,
                'complexity_metrics': {}
            }
            
            # Analyze project structure
            structure = {}
            total_files = 0
            total_directories = 0
            
            for root, dirs, files in os.walk(repo_path):
                # Skip hidden and irrelevant directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', '.git']]
                
                rel_root = os.path.relpath(root, repo_path)
                if rel_root == '.':
                    rel_root = 'root'
                
                total_files += len(files)
                total_directories += len(dirs)
                
                structure[rel_root] = {
                    'directories': len(dirs),
                    'files': len(files),
                    'file_types': {}
                }
                
                for file in files:
                    ext = Path(file).suffix.lower()
                    if ext:
                        structure[rel_root]['file_types'][ext] = structure[rel_root]['file_types'].get(ext, 0) + 1
            
            architecture_data['project_structure'] = structure
            architecture_data['complexity_metrics'] = {
                'total_files': total_files,
                'total_directories': total_directories,
                'directory_depth': len(structure),
                'avg_files_per_directory': total_files / max(len(structure), 1)
            }
            
            # Enhanced design pattern detection
            patterns_detected = []
            
            if 'python' in languages:
                for file_path in Path(repo_path).rglob("*.py"):
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read().lower()
                            
                            # Enhanced pattern detection
                            if re.search(r'class.*factory', content):
                                patterns_detected.append('Factory Pattern')
                            if re.search(r'class.*singleton', content):
                                patterns_detected.append('Singleton Pattern')
                            if 'def __enter__' in content and 'def __exit__' in content:
                                patterns_detected.append('Context Manager Pattern')
                            if '@property' in content:
                                patterns_detected.append('Property Pattern')
                            if re.search(r'class.*observer', content):
                                patterns_detected.append('Observer Pattern')
                            if re.search(r'class.*adapter', content):
                                patterns_detected.append('Adapter Pattern')
                            if re.search(r'class.*builder', content):
                                patterns_detected.append('Builder Pattern')
                            if 'abc' in content and 'abstractmethod' in content:
                                patterns_detected.append('Abstract Base Class Pattern')
                            if re.search(r'def\s+__call__', content):
                                patterns_detected.append('Callable Pattern')
                    except:
                        continue
            
            architecture_data['design_patterns'] = list(set(patterns_detected))
            
            # Calculate architecture score
            architecture_data['architecture_score'] = self._calculate_architecture_score(architecture_data)
            
            return architecture_data
        except Exception as e:
            return {'error': f'Architecture analysis failed: {str(e)}'}

    def analyze_security_python(self, repo_path: str) -> Dict[str, Any]:
        """Python-specific security analysis with enhanced error handling"""
        try:
            result = subprocess.run([
                'bandit', '-r', repo_path, '-f', 'json', '-ll'  # -ll for low level and above
            ], capture_output=True, text=True, timeout=300)
            
            if result.stdout:
                try:
                    security_data = json.loads(result.stdout)
                    
                    # Enhance the security data
                    if 'results' in security_data:
                        for issue in security_data['results']:
                            # Add more readable severity levels
                            severity = issue.get('issue_severity', 'UNKNOWN')
                            issue['severity_level'] = {
                                'HIGH': 'Critical',
                                'MEDIUM': 'Warning', 
                                'LOW': 'Info'
                            }.get(severity, 'Unknown')
                    
                    return security_data
                except json.JSONDecodeError:
                    return {"error": "Failed to parse bandit output"}
            else:
                return {"results": [], "metrics": {"_totals": {"CONFIDENCE.HIGH": 0, "CONFIDENCE.MEDIUM": 0, "CONFIDENCE.LOW": 0}}}
                
        except FileNotFoundError:
            return {"error": "Bandit is not installed. Install with: pip install bandit"}
        except subprocess.TimeoutExpired:
            return {"error": "Bandit analysis timed out"}
        except Exception as e:
            return {"error": f"Python security analysis failed: {str(e)}"}

    def analyze_quality_python(self, repo_path: str) -> Dict[str, Any]:
        """Python-specific quality analysis with enhanced error handling"""
        try:
            python_files = list(Path(repo_path).rglob("*.py"))
            if not python_files:
                return {"error": "No Python files found"}

            # Run Pylint with better error handling
            try:
                pylint_result = subprocess.run([
                    'pylint', '--output-format=json', '--recursive=y', repo_path,
                    '--disable=missing-module-docstring,missing-class-docstring,missing-function-docstring'
                ], capture_output=True, text=True, timeout=300)
                
                pylint_data = []
                if pylint_result.stdout:
                    try:
                        pylint_data = json.loads(pylint_result.stdout)
                        
                        # Enhance pylint data with categories
                        enhanced_data = []
                        for issue in pylint_data:
                            issue['category'] = self._categorize_pylint_issue(issue.get('type', ''))
                            enhanced_data.append(issue)
                        pylint_data = enhanced_data
                        
                    except json.JSONDecodeError:
                        pylint_data = []
            except FileNotFoundError:
                pylint_data = []
                
            # Run Radon for complexity with error handling
            try:
                radon_result = subprocess.run([
                    'radon', 'cc', repo_path, '--json'
                ], capture_output=True, text=True, timeout=300)
                
                radon_data = {}
                if radon_result.stdout:
                    try:
                        radon_data = json.loads(radon_result.stdout)
                    except json.JSONDecodeError:
                        radon_data = {}
            except FileNotFoundError:
                radon_data = {}

            return {
                "pylint_issues": pylint_data,
                "complexity_analysis": radon_data,
                "total_python_files": len(python_files),
                "issues_by_type": self._categorize_issues(pylint_data)
            }
        except Exception as e:
            return {"error": f"Python quality analysis failed: {str(e)}"}

    def _categorize_pylint_issue(self, issue_type: str) -> str:
        """Categorize pylint issues for better display"""
        categories = {
            'error': 'Error',
            'warning': 'Warning', 
            'refactor': 'Refactoring',
            'convention': 'Convention',
            'info': 'Information'
        }
        return categories.get(issue_type.lower(), 'Other')

    def _categorize_issues(self, pylint_data: List[Dict]) -> Dict[str, int]:
        """Categorize issues by type for summary"""
        if not isinstance(pylint_data, list):
            return {}
        
        categories = {}
        for issue in pylint_data:
            issue_type = issue.get('type', 'unknown')
            categories[issue_type] = categories.get(issue_type, 0) + 1
        
        return categories

    def get_repository_info(self, repo_path: str) -> Dict[str, Any]:
        """Get comprehensive repository information with enhanced details"""
        try:
            repo = git.Repo(repo_path)
            
            # Detect languages
            languages = self.language_detector.detect_languages(repo_path)
            
            # Count files and lines with more details
            file_counts = {}
            total_lines = 0
            total_files = 0
            
            for file_path in Path(repo_path).rglob("*"):
                if file_path.is_file() and not any(ignore in str(file_path) for ignore in ['.git', '__pycache__', '.pyc', 'node_modules']):
                    ext = file_path.suffix.lower()
                    if ext:
                        file_counts[ext] = file_counts.get(ext, 0) + 1
                        total_files += 1
                    
                    # Count lines for text files
                    if ext in ['.py', '.js', '.java', '.cpp', '.c', '.h', '.css', '.html', '.md', '.go', '.rs', '.ts', '.jsx', '.tsx']:
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                lines = len(f.readlines())
                                total_lines += lines
                        except:
                            pass

            # Get commit information
            try:
                commits = list(repo.iter_commits())
                total_commits = len(commits)
                
                # Get recent activity
                recent_commits = commits[:10] if commits else []
                recent_activity = []
                for commit in recent_commits:
                    recent_activity.append({
                        'sha': str(commit.hexsha[:8]),
                        'message': commit.message.strip()[:50] + '...' if len(commit.message.strip()) > 50 else commit.message.strip(),
                        'author': str(commit.author.name),
                        'date': commit.committed_datetime.isoformat()
                    })
            except:
                total_commits = 0
                recent_activity = []

            return {
                "repository_url": repo.remotes.origin.url if repo.remotes else "Unknown",
                "branch": repo.active_branch.name if repo.active_branch else "Unknown",
                "total_commits": total_commits,
                "recent_activity": recent_activity,
                "languages_detected": languages,
                "primary_language": max(languages.items(), key=lambda x: x[1])[0] if languages else "Unknown",
                "file_types": file_counts,
                "total_files": total_files,
                "total_lines_of_code": total_lines,
                "last_commit": str(repo.head.commit.hexsha[:8]) if repo.head.commit else "Unknown",
                "repository_size": sum(f.stat().st_size for f in Path(repo_path).rglob('*') if f.is_file()) / (1024 * 1024)  # Size in MB
            }
        except Exception as e:
            return {"error": f"Failed to get repository info: {str(e)}"}

    def _calculate_comprehensive_security_score(self, security_results: Dict[str, Any]) -> int:
        """Calculate comprehensive security score with enhanced logic"""
        score = 100
        
        # Static analysis impact
        static_analysis = security_results.get('static_analysis', {})
        if 'results' in static_analysis and isinstance(static_analysis['results'], list):
            issues = static_analysis['results']
            high_severity = sum(1 for issue in issues if issue.get('issue_severity') == 'HIGH')
            medium_severity = sum(1 for issue in issues if issue.get('issue_severity') == 'MEDIUM')
            low_severity = sum(1 for issue in issues if issue.get('issue_severity') == 'LOW')
            
            # More severe penalty for high severity issues
            score -= (high_severity * 25) + (medium_severity * 10) + (low_severity * 3)
        
        # Secrets analysis impact
        secrets_analysis = security_results.get('secrets_analysis', {})
        total_secrets = secrets_analysis.get('total_secrets', 0)
        high_severity_secrets = secrets_analysis.get('high_severity_secrets', 0)
        
        # Severe penalty for secrets, especially high severity ones
        score -= (high_severity_secrets * 30) + ((total_secrets - high_severity_secrets) * 15)
        
        # Dependency analysis impact
        dependency_analysis = security_results.get('dependency_analysis', {})
        critical_vulns = dependency_analysis.get('critical_severity', 0)
        high_vulns = dependency_analysis.get('high_severity', 0)
        medium_vulns = dependency_analysis.get('medium_severity', 0)
        
        score -= (critical_vulns * 20) + (high_vulns * 15) + (medium_vulns * 8)
        
        return max(0, min(100, score))

    def _calculate_comprehensive_quality_score(self, quality_results: Dict[str, Any]) -> int:
        """Calculate comprehensive quality score with enhanced logic"""
        score = 100
        
        # Code quality impact
        code_quality = quality_results.get('code_quality', {})
        pylint_issues = code_quality.get('pylint_issues', [])
        
        if isinstance(pylint_issues, list):
            errors = sum(1 for issue in pylint_issues if issue.get('type') == 'error')
            warnings = sum(1 for issue in pylint_issues if issue.get('type') == 'warning')
            refactors = sum(1 for issue in pylint_issues if issue.get('type') == 'refactor')
            conventions = sum(1 for issue in pylint_issues if issue.get('type') == 'convention')
            
            # Weight different issue types
            score -= (errors * 15) + (warnings * 8) + (refactors * 3) + (conventions * 2)
        
        # Test coverage impact
        test_coverage = quality_results.get('test_coverage', {})
        coverage_percentage = test_coverage.get('coverage_percentage', 0)
        
        if coverage_percentage < 20:
            score -= 40
        elif coverage_percentage < 50:
            score -= 25
        elif coverage_percentage < 70:
            score -= 15
        elif coverage_percentage < 80:
            score -= 8
        
        # Code duplication impact
        duplication_analysis = quality_results.get('duplication_analysis', {})
        total_duplications = duplication_analysis.get('total_duplications', 0)
        score -= total_duplications * 5
        
        return max(0, min(100, score))

    def _calculate_architecture_score(self, architecture_data: Dict[str, Any]) -> int:
        """Calculate architecture score with enhanced logic"""
        score = 70  # Start with a base score
        
        project_structure = architecture_data.get('project_structure', {})
        design_patterns = architecture_data.get('design_patterns', [])
        complexity_metrics = architecture_data.get('complexity_metrics', {})
        
        # Bonus for good structure
        directory_depth = len(project_structure)
        if directory_depth > 1:
            score += min(15, directory_depth * 3)  # Cap bonus at 15
        
        # Bonus for design patterns
        score += len(design_patterns) * 4
        
        # Bonus for reasonable project organization
        avg_files_per_dir = complexity_metrics.get('avg_files_per_directory', 0)
        if 3 <= avg_files_per_dir <= 15:  # Sweet spot for organization
            score += 10
        elif avg_files_per_dir > 25:  # Too many files per directory
            score -= 10
        
        # Penalty for too shallow or too deep structure
        if directory_depth == 1:
            score -= 10  # Too flat
        elif directory_depth > 10:
            score -= 5   # Too deep
        
        return max(0, min(100, score))

    def cleanup(self):
        """Clean up temporary directory with enhanced error handling"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                def handle_remove_readonly(func, path, exc):
                    if os.path.exists(path):
                        try:
                            os.chmod(path, stat.S_IWRITE)
                            func(path)
                        except:
                            pass

                if os.name == 'nt':
                    shutil.rmtree(self.temp_dir, onerror=handle_remove_readonly)
                else:
                    shutil.rmtree(self.temp_dir)
            except Exception as e:
                print(f"Warning: Could not clean up temporary directory: {self.temp_dir} - {e}")

# MCP Tools (keeping all existing tools)
@mcp.tool()
def detect_project_languages(repo_url: str) -> Dict[str, Any]:
    """Automatically detect programming languages in repository"""
    analyzer = CodeAnalyzer()
    try:
        repo_path = analyzer.clone_repository(repo_url)
        languages = analyzer.language_detector.detect_languages(repo_path)
        return {
            'languages_detected': languages,
            'primary_language': max(languages.items(), key=lambda x: x[1])[0] if languages else 'unknown',
            'total_files_analyzed': sum(languages.values())
        }
    except Exception as e:
        return {"error": f"Language detection failed: {str(e)}"}
    finally:
        analyzer.cleanup()

@mcp.tool()
def analyze_security_vulnerabilities(repo_url: str) -> Dict[str, Any]:
    """Advanced security vulnerability detection"""
    analyzer = CodeAnalyzer()
    try:
        repo_path = analyzer.clone_repository(repo_url)
        languages = analyzer.language_detector.detect_languages(repo_path)
        return analyzer.analyze_security_comprehensive(repo_path, languages)
    except Exception as e:
        return {"error": f"Security analysis failed: {str(e)}"}
    finally:
        analyzer.cleanup()

@mcp.tool()
def analyze_code_quality(repo_url: str) -> Dict[str, Any]:
    """Comprehensive code quality analysis"""
    analyzer = CodeAnalyzer()
    try:
        repo_path = analyzer.clone_repository(repo_url)
        languages = analyzer.language_detector.detect_languages(repo_path)
        return analyzer.analyze_quality_comprehensive(repo_path, languages)
    except Exception as e:
        return {"error": f"Quality analysis failed: {str(e)}"}
    finally:
        analyzer.cleanup()

@mcp.tool()
def analyze_architecture(repo_url: str) -> Dict[str, Any]:
    """Analyze software architecture and design patterns"""
    analyzer = CodeAnalyzer()
    try:
        repo_path = analyzer.clone_repository(repo_url)
        languages = analyzer.language_detector.detect_languages(repo_path)
        return analyzer.analyze_architecture(repo_path, languages)
    except Exception as e:
        return {"error": f"Architecture analysis failed: {str(e)}"}
    finally:
        analyzer.cleanup()

@mcp.tool()
def analyze_repository_comprehensive(repo_url: str) -> Dict[str, Any]:
    """Complete comprehensive analysis of repository"""
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
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": f"Comprehensive analysis failed: {str(e)}"}
    finally:
        analyzer.cleanup()

@mcp.tool()
def generate_comprehensive_report(analysis_results: Dict[str, Any], format: str = "json") -> Dict[str, Any]:
    """Generate comprehensive analysis report"""
    if "error" in analysis_results:
        return {"error": analysis_results["error"]}
    
    repo_info = analysis_results.get("repository_info", {})
    security = analysis_results.get("security_analysis", {})
    quality = analysis_results.get("quality_analysis", {})
    architecture = analysis_results.get("architecture_analysis", {})
    
    overall_score = analysis_results.get("overall_score", 0)
    
    # Generate enhanced recommendations
    recommendations = []
    
    # Security recommendations
    security_score = security.get('security_score', 0)
    if security_score < 70:
        recommendations.append("🔒 Address security vulnerabilities and implement security best practices")
    
    secrets_found = security.get('secrets_analysis', {}).get('total_secrets', 0)
    if secrets_found > 0:
        recommendations.append("🔑 Remove exposed secrets and implement proper secret management")
    
    # Quality recommendations
    quality_score = quality.get('quality_score', 0)
    if quality_score < 70:
        recommendations.append("⚡ Improve code quality by fixing linting issues and reducing complexity")
    
    test_coverage = quality.get('test_coverage', {}).get('coverage_percentage', 0)
    if test_coverage < 50:
        recommendations.append("🧪 Increase test coverage to improve code reliability")
    
    # Architecture recommendations
    architecture_score = architecture.get('architecture_score', 0)
    if architecture_score < 70:
        recommendations.append("🏗️ Improve project structure and implement design patterns")
    
    if overall_score > 85:
        recommendations.append("🎉 Excellent work! Your code meets high standards across all areas")
    
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
        "recommendations": recommendations,
        "technical_details": {
            "languages_detected": repo_info.get("languages_detected", {}),
            "repository_url": repo_info.get("repository_url", ""),
            "analysis_timestamp": analysis_results.get("timestamp", "")
        }
    }
    
    if format.lower() == "html":
        html_content = generate_html_report(report)
        return {"report": html_content, "format": "html"}
    else:
        return {"report": report, "format": "json"}

def generate_html_report(report: Dict[str, Any]) -> str:
    """Generate enhanced HTML report"""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Code Analysis Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .header {{ background: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 30px; }}
            .score {{ font-size: 2em; font-weight: bold; }}
            .grade-A {{ color: #28a745; }}
            .grade-B {{ color: #17a2b8; }}
            .grade-C {{ color: #ffc107; }}
            .grade-D {{ color: #fd7e14; }}
            .grade-F {{ color: #dc3545; }}
            .section {{ margin: 20px 0; padding: 20px; border: 1px solid #dee2e6; border-radius: 5px; }}
            .recommendation {{ background: #e7f3ff; padding: 10px; margin: 10px 0; border-left: 4px solid #007bff; }}
            .metric {{ display: inline-block; margin: 10px; padding: 10px; background: #f8f9fa; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🔍 Code Analysis Report</h1>
            <div class="score grade-{report['executive_summary']['overall_grade']}">
                Overall Grade: {report['executive_summary']['overall_grade']} ({report['executive_summary']['overall_score']}/100)
            </div>
            <p><strong>Primary Language:</strong> {report['executive_summary']['primary_language']}</p>
            <p><strong>Total Files:</strong> {report['executive_summary']['total_files']} | <strong>Lines of Code:</strong> {report['executive_summary']['total_lines']}</p>
        </div>
        
        <div class="section">
            <h2>📊 Detailed Scores</h2>
            <div class="metric">
                <strong>Security:</strong> {report['detailed_scores']['security_score']}/100
            </div>
            <div class="metric">
                <strong>Quality:</strong> {report['detailed_scores']['quality_score']}/100
            </div>
            <div class="metric">
                <strong>Architecture:</strong> {report['detailed_scores']['architecture_score']}/100
            </div>
        </div>
        
        <div class="section">
            <h2>🔍 Key Findings</h2>
            <p><strong>Security Issues:</strong> {len(report['key_findings']['security_issues'])}</p>
            <p><strong>Quality Issues:</strong> {len(report['key_findings']['quality_issues'])}</p>
            <p><strong>Secrets Detected:</strong> {report['key_findings']['secrets_detected']}</p>
            <p><strong>Vulnerabilities:</strong> {report['key_findings']['vulnerabilities']}</p>
            <p><strong>Test Coverage:</strong> {report['key_findings']['test_coverage']:.1f}%</p>
            <p><strong>Design Patterns:</strong> {', '.join(report['key_findings']['design_patterns']) if report['key_findings']['design_patterns'] else 'None detected'}</p>
        </div>
        
        <div class="section">
            <h2>💡 Recommendations</h2>
            {''.join([f'<div class="recommendation">{rec}</div>' for rec in report['recommendations']])}
        </div>
        
        <div class="section">
            <h2>🔧 Technical Details</h2>
            <p><strong>Repository URL:</strong> {report['technical_details']['repository_url']}</p>
            <p><strong>Analysis Timestamp:</strong> {report['technical_details']['analysis_timestamp']}</p>
            <p><strong>Languages Detected:</strong> {', '.join([f'{lang}: {count}' for lang, count in report['technical_details']['languages_detected'].items()])}</p>
        </div>
    </body>
    </html>
    """
    return html

if __name__ == "__main__":
    mcp.run()

from fastapi import FastAPI, Request
import uvicorn

app = FastAPI()

@app.post("/evaluate")
async def evaluate(request: Request):
    data = await request.json()

    try:
        result = await analyze_repository_comprehensive(
            repo_url=data.get("repo_url", "")
        )
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7903)

