# Claude Desktop Auto-Deployment Setup

## Overview

This configuration enables **automatic GPT deployment** when you open Claude Desktop. Claude will have access to deployment tools through an MCP (Model Context Protocol) server.

---

## What This Enables

When you open Claude Desktop with this configuration:

✅ **Automatic Tool Access**
- Claude sees your deployment status automatically
- Can generate GPT config with one command
- Has deployment guides readily available
- Knows the file upload sequence
- Can check GitHub Actions status

✅ **One-Prompt Deployment**
```
You: "Deploy the GPT"

Claude: 
- Checks deployment status
- Generates config if needed
- Opens deployment guide
- Uses Computer Use to upload files
- Completes deployment
```

---

## Installation

### Step 1: Install MCP SDK

```bash
pip install mcp
```

### Step 2: Configure Claude Desktop

**Option A: Automatic Setup (Recommended)**

Run the setup script:

```bash
python setup_claude_mcp.py
```

This will:
1. Install MCP SDK if needed
2. Find your Claude Desktop config location
3. Add the Panelin deployer configuration
4. Restart Claude Desktop if it's running

**Option B: Manual Setup**

1. **Find Claude Desktop config location:**

   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. **Edit the config file** and add:

```json
{
  "mcpServers": {
    "panelin-gpt-deployer": {
      "command": "python",
      "args": [
        "-m",
        "claude_mcp_deployer.server"
      ],
      "cwd": "/path/to/GPT-PANELIN-V3.3",
      "env": {
        "PYTHONPATH": "/path/to/GPT-PANELIN-V3.3"
      }
    }
  }
}
```

**Replace `/path/to/GPT-PANELIN-V3.3`** with the actual path to your repository.

3. **Restart Claude Desktop**

### Step 3: Verify Installation

1. Open Claude Desktop
2. Look for the MCP indicator (should show "panelin-gpt-deployer")
3. Ask Claude: "What deployment tools do you have?"
4. Claude should list 6 tools:
   - check_deployment_status
   - generate_gpt_config
   - get_deployment_guide
   - get_github_actions_status
   - list_files_to_upload
   - get_openai_config

---

## Usage

### Automatic Deployment

Once configured, simply open Claude Desktop and say:

```
"Please deploy the Panelin GPT configuration to OpenAI"
```

Claude will:
1. Check if configuration is ready
2. Generate config if needed
3. Get deployment instructions
4. Use Computer Use to navigate and upload
5. Complete the deployment

### Available Commands

**Check Status:**
```
"Check the GPT deployment status"
```

**Generate Config:**
```
"Generate the GPT configuration"
```

**Get Deployment Guide:**
```
"Show me the deployment guide"
```

**List Files:**
```
"What files need to be uploaded?"
```

**Get Configuration:**
```
"Show me the OpenAI configuration"
```

---

## How It Works

### Architecture

```
┌─────────────────────────────────────┐
│ Claude Desktop                      │
│                                     │
│ When opened, automatically connects │
│ to MCP server                       │
└─────────────┬───────────────────────┘
              │
              ↓ MCP Protocol
┌─────────────────────────────────────┐
│ Panelin MCP Server                  │
│ (claude_mcp_deployer/server.py)     │
│                                     │
│ Provides deployment tools to Claude │
└─────────────┬───────────────────────┘
              │
              ↓ Python calls
┌─────────────────────────────────────┐
│ Repository Scripts                  │
│ - autoconfig_gpt.py                 │
│ - validate_gpt_files.py             │
│ - GPT configuration files           │
└─────────────────────────────────────┘
```

### MCP Tools Provided

1. **check_deployment_status**
   - Checks if GPT_Deploy_Package exists
   - Lists files in the package
   - Verifies completeness

2. **generate_gpt_config**
   - Runs autoconfig_gpt.py automatically
   - Auto-approves configuration
   - Creates deployment package

3. **get_deployment_guide**
   - Returns DEPLOYMENT_GUIDE.md content
   - Falls back to CLAUDE_COMPUTER_USE_AUTOMATION.md
   - Provides step-by-step instructions

4. **get_github_actions_status**
   - Checks for generated artifacts
   - Reports package status

5. **list_files_to_upload**
   - Shows all 21 files in phase order
   - Includes pause timing
   - Shows file existence status

6. **get_openai_config**
   - Returns openai_gpt_config.json
   - Formatted for easy reading
   - Ready for copy-paste

---

## Workflow Example

### Scenario: You want to deploy GPT

**You open Claude Desktop and say:**
```
"Deploy the Panelin GPT"
```

**Claude automatically:**

1. **Checks status**
   ```
   Using tool: check_deployment_status
   ✅ Package ready for deployment
   ```

2. **Gets deployment guide**
   ```
   Using tool: get_deployment_guide
   📄 Deployment Guide loaded
   ```

3. **Lists files**
   ```
   Using tool: list_files_to_upload
   Phase 1: 4 files...
   ```

4. **Starts Computer Use**
   ```
   I'll now use Computer Use to deploy:
   - Opening OpenAI GPT Builder
   - Creating new GPT
   - Uploading files in phase order
   - Configuring settings
   ```

5. **Completes deployment**
   ```
   ✅ GPT deployed successfully!
   URL: https://chat.openai.com/g/...
   ```

**Total time: ~5 minutes (supervised)**

---

## Configuration Options

### Auto-Approve Mode (Default)

The MCP server auto-approves configuration generation:

```python
# In server.py
generate_gpt_config(auto_approve=True)
```

**To disable auto-approve:**

Edit `claude_mcp_deployer/server.py` and change:
```python
"default": True  # Change to False
```

### Custom Repository Path

If your repository is in a non-standard location, update the config:

```json
{
  "mcpServers": {
    "panelin-gpt-deployer": {
      "cwd": "/your/custom/path/GPT-PANELIN-V3.3"
    }
  }
}
```

---

## Troubleshooting

### Issue: Claude doesn't see MCP tools

**Solution:**
1. Check config file location is correct
2. Verify `claude_desktop_config.json` has correct syntax
3. Restart Claude Desktop completely
4. Check MCP indicator in Claude Desktop

### Issue: "MCP SDK not installed" error

**Solution:**
```bash
pip install mcp
```

### Issue: "autoconfig_gpt.py not found"

**Solution:**
- Verify `cwd` path in config is correct
- Check repository path exists
- Ensure all files are in the correct location

### Issue: Configuration generation fails

**Solution:**
1. Run manually first: `python autoconfig_gpt.py`
2. Check error messages
3. Verify all 21 files exist
4. Run `python validate_gpt_files.py`

### Issue: Claude can't use Computer Use

**Solution:**
- Enable Computer Use in Claude Desktop settings
- Settings → Features → Computer Use (Beta)
- Restart Claude Desktop

---

## Security Considerations

### MCP Server Access

The MCP server has access to:
- ✅ Read repository files
- ✅ Run Python scripts in repository
- ✅ Generate configuration packages
- ❌ No network access outside repository
- ❌ No system-wide access
- ❌ No credential storage

### Safe Operations

All operations are:
- Read-only on source files
- Write-only to GPT_Deploy_Package
- No modification of Git repository
- No deletion of files

---

## Advanced Usage

### Multiple Repositories

You can configure multiple MCP servers:

```json
{
  "mcpServers": {
    "panelin-dev": {
      "command": "python",
      "args": ["-m", "claude_mcp_deployer.server"],
      "cwd": "/path/to/dev/repo"
    },
    "panelin-prod": {
      "command": "python",
      "args": ["-m", "claude_mcp_deployer.server"],
      "cwd": "/path/to/prod/repo"
    }
  }
}
```

### Custom Workflows

Create custom deployment workflows by:

1. Extending `server.py` with new tools
2. Adding custom commands
3. Integrating with CI/CD

---

## Integration with GitHub Actions

### Combined Workflow

**Best Practice:**
1. Push changes → GitHub Actions generates config
2. Open Claude Desktop → MCP server detects new config
3. Claude automatically offers to deploy
4. One-prompt deployment completes

**Setup:**
```bash
# 1. Enable GitHub Actions (already done)
# 2. Configure Claude MCP (this guide)
# 3. Push changes
git push origin main

# 4. Open Claude and say:
"Is there a new GPT configuration ready?"

# Claude: "Yes! Would you like me to deploy it?"
```

---

## Comparison: Before vs After

### Before MCP Configuration

```
You: Open Claude Desktop
You: Give long prompt with all instructions
You: Manually guide each step
You: Approve every action
Time: 10-15 minutes
```

### After MCP Configuration

```
You: Open Claude Desktop
You: "Deploy the GPT"
Claude: Handles everything automatically
You: Approve final publication
Time: 5 minutes
```

**Time saved: 50-66% reduction**

---

## Updates and Maintenance

### Updating the MCP Server

```bash
# Pull latest changes
git pull origin main

# MCP server updates automatically
# No need to reconfigure Claude Desktop
```

### Disabling Auto-Deployment

To disable temporarily:

```json
{
  "mcpServers": {
    "panelin-gpt-deployer": {
      "disabled": true
    }
  }
}
```

---

## Summary

### What You Get

✅ **One-command deployment**
✅ **Automatic tool access for Claude**
✅ **50-66% time savings**
✅ **Seamless GitHub Actions integration**
✅ **Safe, sandboxed operations**

### Setup Time

- Initial: 5-10 minutes
- Per deployment: 5 minutes (vs. 15+ manual)
- ROI: Immediate

### Prerequisites

- Claude Desktop installed
- Python 3.11+
- MCP SDK (`pip install mcp`)
- This repository cloned locally

---

**Ready to start?**

Run: `python setup_claude_mcp.py`

Then open Claude Desktop and say: **"Deploy the GPT"**

---

**Last Updated:** 2026-02-16  
**Version:** 1.0  
**Status:** ✅ Production Ready
