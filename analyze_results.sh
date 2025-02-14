#!/bin/bash

# Set up colors
GREEN=$(tput setaf 2)
CYAN=$(tput setaf 6)
RESET=$(tput sgr0)

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$SCRIPT_DIR/backend"

cd "$BACKEND_DIR"
source venv/bin/activate

echo "${CYAN}🔍 Analyzing extraction failures...${RESET}"
python -c "from utils.analyze_failures import analyze_failures; analyze_failures()"

echo "${GREEN}✅ Analysis complete${RESET}"
echo "📝 Results saved in output directory"