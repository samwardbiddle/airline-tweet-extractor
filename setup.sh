#!/bin/bash

# Set up colors for output
GREEN=$(tput setaf 2)
YELLOW=$(tput setaf 3)
RESET=$(tput sgr0)
CYAN=$(tput setaf 6)
RED=$(tput setaf 1)

echo "${YELLOW}🚀 Setting up development environment...${RESET}"

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "${YELLOW}Installing Homebrew...${RESET}"
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Install required brew packages
echo "${YELLOW}Installing required Homebrew packages...${RESET}"
BREW_PACKAGES=("gum" "figlet" "pv")

for package in "${BREW_PACKAGES[@]}"; do
    if ! brew list "$package" &>/dev/null; then
        echo "Installing $package..."
        brew install "$package"
    else
        echo "$package already installed"
    fi
done

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$SCRIPT_DIR/backend"

# Create backend directory if it doesn't exist
if [ ! -d "$BACKEND_DIR" ]; then
    echo "Creating backend directory..."
    mkdir -p "$BACKEND_DIR"
fi

# Navigate to backend directory
cd "$BACKEND_DIR"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "${YELLOW}Creating Python virtual environment in backend directory...${RESET}"
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "${YELLOW}Installing Python requirements...${RESET}"
    pip install -r requirements.txt
fi

# Function to check if OpenAI API key is valid
check_openai_key() {
    local api_key=$1
    # Activate virtual environment for Python check
    source venv/bin/activate
    # Try to use the key with a simple API call
    if python3 -c "
import openai
openai.api_key = '$api_key'
try:
    openai.models.list()
    print('valid')
except Exception as e:
    print('invalid')
" | grep -q "valid"; then
        return 0
    else
        return 1
    fi
}

# Check for .env file and OpenAI API key
ENV_FILE="$SCRIPT_DIR/.env"
if [ ! -f "$ENV_FILE" ] || ! grep -q "OPENAI_API_KEY=" "$ENV_FILE" || [ -z "$(grep "OPENAI_API_KEY=" "$ENV_FILE" | cut -d'=' -f2)" ]; then
    echo "${YELLOW}OpenAI API key not found.${RESET}"
    
    # Keep asking until a valid key is provided
    while true; do
        echo "${CYAN}Please enter your OpenAI API key:${RESET}"
        read -r API_KEY
        
        echo "${YELLOW}Validating API key...${RESET}"
        if check_openai_key "$API_KEY"; then
            echo "${GREEN}✅ API key is valid!${RESET}"
            echo "OPENAI_API_KEY=$API_KEY" > "$ENV_FILE"
            break
        else
            echo "${RED}❌ Invalid API key. Please try again.${RESET}"
        fi
    done
else
    echo "${GREEN}✅ OpenAI API key found in .env file${RESET}"
    # Optionally validate existing key
    API_KEY=$(grep "OPENAI_API_KEY=" "$ENV_FILE" | cut -d'=' -f2)
    if ! check_openai_key "$API_KEY"; then
        echo "${RED}⚠️  Existing API key appears to be invalid.${RESET}"
        echo "${YELLOW}Would you like to enter a new API key? (y/n)${RESET}"
        read -r REPLACE_KEY
        if [[ $REPLACE_KEY =~ ^[Yy]$ ]]; then
            while true; do
                echo "${CYAN}Please enter your OpenAI API key:${RESET}"
                read -r API_KEY
                
                echo "${YELLOW}Validating API key...${RESET}"
                if check_openai_key "$API_KEY"; then
                    echo "${GREEN}✅ API key is valid!${RESET}"
                    echo "OPENAI_API_KEY=$API_KEY" > "$ENV_FILE"
                    break
                else
                    echo "${RED}❌ Invalid API key. Please try again.${RESET}"
                fi
            done
        fi
    fi
fi

echo "${GREEN}✨ Setup complete! Virtual environment is activated.${RESET}"
echo "${GREEN}🎉 All dependencies have been installed.${RESET}"
echo ""
echo "${YELLOW}Next steps:${RESET}"
echo "1. Place your dataset in the data/ directory"
echo "2. Run ./run_extraction.sh to start the extraction process"