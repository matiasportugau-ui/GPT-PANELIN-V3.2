#!/usr/bin/env python3
"""
Claude Desktop MCP Setup Script
Automatically configures Claude Desktop to use Panelin GPT Deployer
"""

import json
import os
import platform
import subprocess
import sys
from pathlib import Path
import shutil

# ANSI colors for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    """Print formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")

def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def check_mcp_installed():
    """Check if MCP SDK is installed"""
    try:
        import mcp
        print_success("MCP SDK is installed")
        return True
    except ImportError:
        print_warning("MCP SDK not installed")
        return False

def install_mcp():
    """Install MCP SDK"""
    print_info("Installing MCP SDK...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "mcp"])
        print_success("MCP SDK installed successfully")
        return True
    except subprocess.CalledProcessError:
        print_error("Failed to install MCP SDK")
        return False

def get_claude_config_path():
    """Get Claude Desktop config file path based on OS"""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        path = Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    elif system == "Windows":
        path = Path(os.environ.get("APPDATA", "")) / "Claude" / "claude_desktop_config.json"
    elif system == "Linux":
        path = Path.home() / ".config" / "Claude" / "claude_desktop_config.json"
    else:
        print_error(f"Unsupported operating system: {system}")
        return None
    
    return path

def get_repo_path():
    """Get repository root path"""
    return Path(__file__).parent.resolve()

def backup_config(config_path):
    """Backup existing config file"""
    if config_path.exists():
        backup_path = config_path.with_suffix('.json.backup')
        shutil.copy2(config_path, backup_path)
        print_success(f"Backed up existing config to: {backup_path}")
        return True
    return False

def create_config(config_path, repo_path):
    """Create or update Claude Desktop config"""
    
    # MCP server configuration
    mcp_config = {
        "mcpServers": {
            "panelin-gpt-deployer": {
                "command": "python",
                "args": [
                    "-m",
                    "claude_mcp_deployer.server"
                ],
                "cwd": str(repo_path),
                "env": {
                    "PYTHONPATH": str(repo_path)
                }
            }
        }
    }
    
    # Load existing config if it exists
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                existing_config = json.load(f)
            
            # Merge MCP servers
            if "mcpServers" not in existing_config:
                existing_config["mcpServers"] = {}
            
            existing_config["mcpServers"]["panelin-gpt-deployer"] = mcp_config["mcpServers"]["panelin-gpt-deployer"]
            config_to_write = existing_config
            
            print_info("Updating existing configuration")
        except json.JSONDecodeError:
            print_warning("Existing config is invalid, creating new config")
            config_to_write = mcp_config
    else:
        print_info("Creating new configuration")
        config_to_write = mcp_config
    
    # Create directory if needed
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write config
    with open(config_path, 'w') as f:
        json.dump(config_to_write, f, indent=2)
    
    print_success(f"Configuration written to: {config_path}")
    return True

def check_claude_running():
    """Check if Claude Desktop is running"""
    system = platform.system()
    
    try:
        if system == "Darwin":  # macOS
            result = subprocess.run(
                ["pgrep", "-f", "Claude"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        elif system == "Windows":
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq Claude.exe"],
                capture_output=True,
                text=True
            )
            return "Claude.exe" in result.stdout
        elif system == "Linux":
            result = subprocess.run(
                ["pgrep", "-f", "claude"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
    except:
        pass
    
    return False

def main():
    """Main setup function"""
    
    print_header("Claude Desktop MCP Setup")
    print_info("Panelin GPT Deployer - Automatic Configuration")
    
    # Step 1: Check/Install MCP SDK
    print("\n📦 Step 1: Checking MCP SDK...")
    if not check_mcp_installed():
        response = input("Install MCP SDK now? (y/n): ").strip().lower()
        if response == 'y':
            if not install_mcp():
                print_error("Setup failed: Could not install MCP SDK")
                return 1
        else:
            print_warning("Setup cancelled: MCP SDK required")
            return 1
    
    # Step 2: Locate Claude config
    print("\n📁 Step 2: Locating Claude Desktop config...")
    config_path = get_claude_config_path()
    if not config_path:
        print_error("Setup failed: Could not determine config path")
        return 1
    
    print_info(f"Config path: {config_path}")
    
    # Step 3: Get repository path
    print("\n📂 Step 3: Detecting repository path...")
    repo_path = get_repo_path()
    print_info(f"Repository: {repo_path}")
    
    # Step 4: Backup existing config
    print("\n💾 Step 4: Backing up existing config...")
    backup_config(config_path)
    
    # Step 5: Create/Update config
    print("\n⚙️  Step 5: Creating configuration...")
    if not create_config(config_path, repo_path):
        print_error("Setup failed: Could not write configuration")
        return 1
    
    # Step 6: Check if Claude is running
    print("\n🔍 Step 6: Checking Claude Desktop status...")
    if check_claude_running():
        print_warning("Claude Desktop is currently running")
        print_info("Please restart Claude Desktop for changes to take effect")
        response = input("Would you like to see restart instructions? (y/n): ").strip().lower()
        if response == 'y':
            print("\n📝 Restart Instructions:")
            print("1. Quit Claude Desktop completely")
            print("2. Relaunch Claude Desktop")
            print("3. Look for MCP indicator showing 'panelin-gpt-deployer'")
    else:
        print_success("Claude Desktop is not running - configuration will load on next launch")
    
    # Step 7: Verification instructions
    print_header("Setup Complete!")
    
    print(f"""
{Colors.GREEN}✅ Configuration successfully installed!{Colors.END}

{Colors.BOLD}Next Steps:{Colors.END}

1. {Colors.BOLD}Launch Claude Desktop{Colors.END}
   (or restart if it's already running)

2. {Colors.BOLD}Verify MCP Connection{Colors.END}
   Look for "panelin-gpt-deployer" in the MCP indicator

3. {Colors.BOLD}Test the Setup{Colors.END}
   Ask Claude: "What deployment tools do you have?"
   
   Claude should respond with 6 tools:
   • check_deployment_status
   • generate_gpt_config
   • get_deployment_guide
   • get_github_actions_status
   • list_files_to_upload
   • get_openai_config

4. {Colors.BOLD}Deploy Your GPT{Colors.END}
   Simply say: "Deploy the Panelin GPT"
   
   Claude will handle the rest automatically!

{Colors.BOLD}Configuration Details:{Colors.END}
• Config file: {config_path}
• Repository: {repo_path}
• MCP Server: claude_mcp_deployer

{Colors.BOLD}Documentation:{Colors.END}
• Full guide: CLAUDE_MCP_SETUP_GUIDE.md
• Automation guide: CLAUDE_COMPUTER_USE_AUTOMATION.md

{Colors.BOLD}Troubleshooting:{Colors.END}
If Claude doesn't see the tools:
1. Verify config file exists
2. Check syntax is correct
3. Restart Claude completely
4. Check MCP indicator

{Colors.BLUE}{'='*70}{Colors.END}
    """)
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Setup failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
