#!/bin/bash

# TaskMaster Setup Script
# Author: Abdelhamid Bouazi
# This script sets up the TaskMaster CLI tool with the 'tasks' alias

set -e  # Exit on any error

echo "🚀 TaskMaster Setup"
echo "=================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TASKMASTER_SCRIPT="${SCRIPT_DIR}/taskmaster.py"

# Check if taskmaster.py exists
if [ ! -f "$TASKMASTER_SCRIPT" ]; then
    echo -e "${RED}❌ Error: taskmaster.py not found in $SCRIPT_DIR${NC}"
    exit 1
fi

# Make the script executable
echo -e "${BLUE}🔧 Making taskmaster.py executable...${NC}"
chmod +x "$TASKMASTER_SCRIPT"

# Detect shell
SHELL_NAME=$(basename "$SHELL")
echo -e "${BLUE}🔍 Detected shell: $SHELL_NAME${NC}"

# Determine shell config file
case "$SHELL_NAME" in
    "zsh")
        SHELL_CONFIG="$HOME/.zshrc"
        ;;
    "bash")
        SHELL_CONFIG="$HOME/.bashrc"
        ;;
    "fish")
        SHELL_CONFIG="$HOME/.config/fish/config.fish"
        echo -e "${YELLOW}⚠️  Fish shell detected. You'll need to manually add the alias.${NC}"
        echo -e "${YELLOW}   Add this line to $SHELL_CONFIG:${NC}"
        echo -e "${YELLOW}   alias tasks='python3 $TASKMASTER_SCRIPT'${NC}"
        exit 0
        ;;
    *)
        echo -e "${YELLOW}⚠️  Unknown shell: $SHELL_NAME${NC}"
        echo -e "${YELLOW}   Please manually add this alias to your shell configuration:${NC}"
        echo -e "${YELLOW}   alias tasks='python3 $TASKMASTER_SCRIPT'${NC}"
        exit 0
        ;;
esac

# Check if shell config file exists
if [ ! -f "$SHELL_CONFIG" ]; then
    echo -e "${YELLOW}⚠️  Creating $SHELL_CONFIG...${NC}"
    touch "$SHELL_CONFIG"
fi

# Check if alias already exists
if grep -q "alias tasks=" "$SHELL_CONFIG"; then
    echo -e "${YELLOW}⚠️  TaskMaster alias already exists in $SHELL_CONFIG${NC}"
    echo -e "${YELLOW}   Current alias:${NC}"
    grep "alias tasks=" "$SHELL_CONFIG"
    echo ""
    read -p "Do you want to update it? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Remove existing alias
        sed -i.bak '/alias tasks=/d' "$SHELL_CONFIG"
        echo -e "${GREEN}✅ Removed old alias${NC}"
    else
        echo -e "${BLUE}🔄 Keeping existing alias. Setup cancelled.${NC}"
        exit 0
    fi
fi

# Add the alias
ALIAS_LINE="alias tasks='python3 $TASKMASTER_SCRIPT'"
echo "" >> "$SHELL_CONFIG"
echo "# TaskMaster CLI Tool - Added by setup script" >> "$SHELL_CONFIG"
echo "$ALIAS_LINE" >> "$SHELL_CONFIG"

echo -e "${GREEN}✅ TaskMaster alias added successfully!${NC}"
echo ""

# Check Python version
echo -e "${BLUE}🐍 Checking Python version...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo -e "${GREEN}✅ $PYTHON_VERSION found${NC}"
else
    echo -e "${RED}❌ Error: Python 3 is required but not found${NC}"
    echo -e "${RED}   Please install Python 3 and try again${NC}"
    exit 1
fi

# Test the installation
echo -e "${BLUE}🧪 Testing TaskMaster installation...${NC}"
python3 "$TASKMASTER_SCRIPT" --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ TaskMaster is working correctly!${NC}"
else
    echo -e "${RED}❌ Error: There seems to be an issue with TaskMaster${NC}"
    exit 1
fi

# Show next steps
echo ""
echo -e "${GREEN}🎉 Setup completed successfully!${NC}"
echo ""
echo -e "${BLUE}📋 Next Steps:${NC}"
echo "1. Restart your terminal or run: source $SHELL_CONFIG"
echo "2. Test the installation: tasks list"
echo "3. Create your first task: tasks create \"My first task\""
echo ""
echo -e "${BLUE}📖 Quick Commands:${NC}"
echo "• tasks list              - Show all tasks"
echo "• tasks create \"task\"     - Create a new task"
echo "• tasks show abc          - Show task details (using 3-char ID)"
echo "• tasks complete abc      - Mark task as complete"
echo "• tasks analytics         - View productivity analytics"
echo ""
echo -e "${BLUE}📚 Full documentation: See README.md${NC}"
echo ""
echo -e "${GREEN}Happy task managing! 🚀${NC}"