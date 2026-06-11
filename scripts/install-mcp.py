#!/usr/bin/env python3
import os
import sys
import json
import subprocess
from pathlib import Path

def main():
    repo_root = Path(__file__).resolve().parents[1]
    venv_dir = repo_root / ".venv"
    
    print("=== AI Agent Standards MCP Auto-Installer ===")
    
    # 1. Setup virtual environment
    if not venv_dir.exists():
        print("Creating virtual environment (.venv)...")
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
    
    # Determine python executable path in venv
    if os.name == "nt":
        pip_exe = venv_dir / "Scripts" / "pip.exe"
        python_exe = venv_dir / "Scripts" / "python.exe"
    else:
        pip_exe = venv_dir / "bin" / "pip"
        python_exe = venv_dir / "bin" / "python"
        
    # 2. Install dependencies
    print("Installing packages and dependencies in editable mode...")
    subprocess.run([str(pip_exe), "install", "-e", "."], cwd=str(repo_root), check=True)
    
    # 3. Locate Claude Desktop config
    if sys.platform == "win32":
        claude_config_path = Path(os.environ.get("APPDATA", "")) / "Claude" / "claude_desktop_config.json"
    elif sys.platform == "darwin":
        claude_config_path = Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    else: # Linux
        claude_config_path = Path.home() / ".config" / "Claude" / "claude_desktop_config.json"
        
    print(f"Locating Claude Desktop config at: {claude_config_path}")
    
    # Load or initialize config
    config = {}
    if claude_config_path.exists():
        try:
            config = json.loads(claude_config_path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"Warning: Failed to read existing config: {e}. Starting fresh.")
            
    if "mcpServers" not in config:
        config["mcpServers"] = {}
        
    # Configure the server using direct venv python execution (Option A)
    pythonpath = str(repo_root / "src")
    config["mcpServers"]["ai-agent-standards-mcp"] = {
        "command": str(python_exe),
        "args": ["-m", "ai_agent_standards_mcp"],
        "env": {
            "PYTHONPATH": pythonpath
        }
    }
    
    # Write back config
    try:
        claude_config_path.parent.mkdir(parents=True, exist_ok=True)
        claude_config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")
        print(f"Successfully configured Claude Desktop! Added 'ai-agent-standards-mcp' server.")
    except Exception as e:
        print(f"Error writing Claude config file: {e}")
        
    print("\n=== Installation Completed Successfully! ===")
    print("Restart your Claude Desktop client to start using the server.")

if __name__ == "__main__":
    main()
