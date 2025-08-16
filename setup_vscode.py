#!/usr/bin/env python3
"""
Quick setup script for VS Code users
Automates the initial setup process
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version >= (3, 8):
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} (compatible)")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor} (need 3.8+)")
        return False

def setup_virtual_environment():
    """Create and activate virtual environment"""
    if not Path("venv").exists():
        if run_command("python -m venv venv", "Creating virtual environment"):
            print("💡 Virtual environment created at ./venv")
            return True
        return False
    else:
        print("✅ Virtual environment already exists")
        return True

def install_dependencies():
    """Install project dependencies"""
    # Determine activation script based on OS
    if os.name == 'nt':  # Windows
        activate_cmd = "venv\\Scripts\\activate"
        pip_cmd = "venv\\Scripts\\pip"
    else:  # macOS/Linux
        activate_cmd = "source venv/bin/activate"
        pip_cmd = "venv/bin/pip"
    
    commands = [
        (f"{pip_cmd} install --upgrade pip", "Upgrading pip"),
        (f"{pip_cmd} install -e .", "Installing project in development mode"),
        (f"{pip_cmd} install -r requirements-dev.txt", "Installing development dependencies")
    ]
    
    for cmd, desc in commands:
        if not run_command(cmd, desc):
            return False
    
    return True

def setup_environment_file():
    """Create .env file from template"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        try:
            env_file.write_text(env_example.read_text())
            print("✅ Created .env file from template")
            print("⚠️  Please add your PERPLEXITY_API_KEY to .env file")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    elif env_file.exists():
        print("✅ .env file already exists")
        return True
    else:
        print("❌ .env.example not found")
        return False

def setup_pre_commit():
    """Set up pre-commit hooks"""
    if Path(".pre-commit-config.yaml").exists():
        return run_command("pre-commit install", "Setting up pre-commit hooks")
    else:
        print("⚠️  .pre-commit-config.yaml not found, skipping pre-commit setup")
        return True

def run_tests():
    """Run initial tests to verify setup"""
    # Determine python executable in venv
    if os.name == 'nt':  # Windows
        python_cmd = "venv\\Scripts\\python"
    else:  # macOS/Linux
        python_cmd = "venv/bin/python"
    
    print("🧪 Running setup verification...")
    
    # Test import
    test_cmd = f'{python_cmd} -c "import sys; sys.path.insert(0, \'src\'); from project_evaluator_mcp.server import mcp; print(\'✅ Import successful\')"'
    
    if run_command(test_cmd, "Testing imports"):
        print("🎉 Setup verification passed!")
        return True
    else:
        print("❌ Setup verification failed")
        return False

def main():
    """Main setup function"""
    print("🚀 Project Evaluator MCP Server - VS Code Setup")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        print("\n❌ Please install Python 3.8 or higher")
        return False
    
    # Setup steps
    steps = [
        ("Virtual Environment", setup_virtual_environment),
        ("Dependencies", install_dependencies),
        ("Environment File", setup_environment_file),
        ("Pre-commit Hooks", setup_pre_commit),
        ("Verification", run_tests)
    ]
    
    print("\n📋 Running setup steps...")
    print("-" * 40)
    
    for step_name, step_func in steps:
        print(f"\n🔧 Step: {step_name}")
        if not step_func():
            print(f"\n❌ Setup failed at step: {step_name}")
            return False
    
    print("\n" + "=" * 60)
    print("🎉 VS Code setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Add your PERPLEXITY_API_KEY to .env file")
    print("2. Open VS Code: code .")
    print("3. Install recommended extensions when prompted")
    print("4. Run test: python test_client.py")
    print("5. Try examples: python examples/basic_usage.py")
    
    print("\n🔧 VS Code features available:")
    print("- Press F5 to debug the MCP server")
    print("- Ctrl+Shift+P → 'Tasks: Run Task' for build tasks")
    print("- Use the integrated terminal for commands")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
