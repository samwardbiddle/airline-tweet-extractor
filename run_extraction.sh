#!/bin/bash

# Set up colors
GREEN=$(tput setaf 2)
YELLOW=$(tput setaf 3)
CYAN=$(tput setaf 6)
RED=$(tput setaf 1)
RESET=$(tput sgr0)

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$SCRIPT_DIR/backend"

# Set up logging - one file per run with timestamp
LOG_DIR="$SCRIPT_DIR/logs"
LOG_FILE="$LOG_DIR/extraction_$(date +"%Y-%m-%d_%H-%M-%S").log"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Function to log messages
log_message() {
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    echo "[$timestamp] $1" | tee -a "$LOG_FILE"
}

# Initialize
log_message "Starting extraction process"

# Dataset selection
echo "${CYAN}📂 Select a dataset or enter manually:${RESET}"
DATA_DIR="$SCRIPT_DIR/data"
mkdir -p "$DATA_DIR"

# Get available datasets
DATASETS=()
while IFS= read -r file; do
    DATASETS+=("$file")
done < <(find "$DATA_DIR" -type f -name "*.csv" -exec basename {} \;)

# Add manual entry as first option
DATASET=$(gum choose "manual entry" "${DATASETS[@]}")

# Get the CLI methods from Python
CLI_METHODS=$(cd "$BACKEND_DIR" && source venv/bin/activate && python -c "from main import CLI_METHODS; print(' '.join(CLI_METHODS))")

if [ "$DATASET" = "manual entry" ]; then
    echo "${CYAN}🧠 Choose an extraction method:${RESET}"
    METHOD=$(gum choose $CLI_METHODS)
    echo "✅ Selected method: ${YELLOW}$METHOD${RESET}"
    
    # Handle fine-tuned model selection if needed
    if [ "$METHOD" = "fine-tuned" ] || [ "$METHOD" = "compare-all" ]; then
        echo "${CYAN}🤖 Fine-tuned Model Options:${RESET}"
        
        # Get available models from OpenAI
        cd "$BACKEND_DIR"
        source venv/bin/activate
        
        # Get models and check if we got any
        MODELS=$(python -c "from extract.fine_tuned import get_available_models; models = get_available_models(); print('\n'.join(models) if models else '')")
        
        if [ ! -z "$MODELS" ]; then
            echo "${CYAN}Select a model:${RESET}"
            MODEL_ID=$(echo "$MODELS" | gum choose)
            echo "✅ Selected model: ${YELLOW}$MODEL_ID${RESET}"
        else
            echo "${YELLOW}No existing models found. Training new model...${RESET}"
            echo "${CYAN}This may take 15-30 minutes...${RESET}"
            MODEL_ID=$(python main.py --train-model)
        fi
    fi
    
    echo "${CYAN}Enter a tweet to test:${RESET}"
    TWEET=$(gum input --placeholder "Enter your tweet here...")
    
    # Run the test
    cd "$BACKEND_DIR"
    source venv/bin/activate
    if [ -n "$MODEL_ID" ]; then
        python main.py --method "$METHOD" --test-tweet "$TWEET" --model-id "$MODEL_ID"
    else
        python main.py --method "$METHOD" --test-tweet "$TWEET"
    fi
    exit 0
else
    echo "✅ Selected dataset: ${YELLOW}$DATASET${RESET}"
    DATASET="$DATA_DIR/$DATASET"
    
    echo "${CYAN}🧠 Choose an extraction method:${RESET}"
    METHOD=$(gum choose $CLI_METHODS)
    echo "✅ Selected method: ${YELLOW}$METHOD${RESET}"

    # Handle fine-tuned model selection/creation
    MODEL_ID=""
    if [ "$METHOD" = "fine-tuned" ] || [ "$METHOD" = "compare-all" ]; then
        echo "${CYAN}🤖 Fine-tuned Model Options:${RESET}"
        
        # Get available models from OpenAI
        cd "$BACKEND_DIR"
        source venv/bin/activate
        
        # Get models and check if we got any
        MODELS=$(python -c "from extract.fine_tuned import get_available_models; models = get_available_models(); print('\n'.join(models) if models else '')")
        
        if [ ! -z "$MODELS" ]; then
            echo "${CYAN}Select a model:${RESET}"
            MODEL_ID=$(echo "$MODELS" | gum choose)
            echo "✅ Selected model: ${YELLOW}$MODEL_ID${RESET}"
        else
            echo "${YELLOW}No existing models found. Training new model...${RESET}"
            echo "${CYAN}This may take 15-30 minutes...${RESET}"
            MODEL_ID=$(python main.py --train-model)
        fi
    fi
fi

# Navigate to backend and activate venv
cd "$BACKEND_DIR"
source venv/bin/activate

# Run extraction with live accuracy tracking
echo "${CYAN}Running extraction...${RESET}"
if [ -n "$MODEL_ID" ]; then
    python main.py --method "$METHOD" --dataset "$DATASET" --model-id "$MODEL_ID" 2> >(tee -a "$LOG_FILE" >&2)
else
    python main.py --method "$METHOD" --dataset "$DATASET" 2> >(tee -a "$LOG_FILE" >&2)
fi

echo "${GREEN}✅ Extraction completed${RESET}"
echo "📝 Log file: $LOG_FILE"

# Check if output directory and results file exist
OUTPUT_DIR="$SCRIPT_DIR/output"
RESULTS_FILE=$(ls -t "$OUTPUT_DIR"/results_${METHOD}_*.csv 2>/dev/null | head -n1)

if [ ! -d "$OUTPUT_DIR" ]; then
    echo "${YELLOW}Creating output directory...${RESET}"
    mkdir -p "$OUTPUT_DIR"
fi

if [ ! -f "$RESULTS_FILE" ]; then
    echo "${YELLOW}❌ No results file was generated${RESET}"
    exit 1
fi

# 5️⃣ Show Completion Message with Options
gum style \
    --border rounded \
    --margin "1" \
    --padding "1" \
    --foreground 212 \
    "🎉 Extraction Finished! 🎉"

echo "${CYAN}📊 Options:${RESET}"
CHOICE=$(gum choose "View Results" "Manual Test" "Run Another Method" "Save Log" "Exit")

case "$CHOICE" in
    "View Results")
        if [ "$METHOD" = "compare-all" ]; then
            SUMMARY_FILE="$OUTPUT_DIR/comparison_summary.csv"
            if [ -f "$SUMMARY_FILE" ]; then
                # Create a formatted table with headers
                echo "\n${CYAN}📊 Comparison Results:${RESET}"
                echo "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
                echo "Method      | Accuracy | Avg Similarity | Tokens Used | Cost ($) | Time (s)"
                echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                
                # Read and format each line of the summary
                while IFS=, read -r method accuracy similarity tokens cost time; do
                    # Skip header
                    if [ "$method" != "method" ]; then
                        printf "%-11s| %8.2f | %13.2f | %11d | %8.3f | %8.1f\n" \
                            "$method" "$accuracy" "$similarity" "$tokens" "$cost" "$time"
                    fi
                done < "$SUMMARY_FILE"
                echo "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}\n"
                
                # Save formatted table to a text file
                FORMATTED_FILE="$OUTPUT_DIR/comparison_summary_formatted.txt"
                {
                    echo "Comparison Results"
                    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                    echo "Method      | Accuracy | Avg Similarity | Tokens Used | Cost ($) | Time (s)"
                    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                    while IFS=, read -r method accuracy similarity tokens cost time; do
                        if [ "$method" != "method" ]; then
                            printf "%-11s| %8.2f | %13.2f | %11d | %8.3f | %8.1f\n" \
                                "$method" "$accuracy" "$similarity" "$tokens" "$cost" "$time"
                        fi
                    done < "$SUMMARY_FILE"
                    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                } > "$FORMATTED_FILE"
                
                echo "📝 Formatted results saved to: $FORMATTED_FILE"
            else
                echo "${YELLOW}❌ No comparison results found${RESET}"
            fi
        else
            RESULTS_FILE=$(ls -t "$OUTPUT_DIR"/results_${METHOD}_*.csv 2>/dev/null | head -n1)
            if [ -f "$RESULTS_FILE" ]; then
                column -s, -t < "$RESULTS_FILE" | less -R
            else
                echo "${YELLOW}❌ No results file found${RESET}"
            fi
        fi
        ;;
    "Manual Test")
        echo "${CYAN}Enter a tweet to test:${RESET}"
        TWEET=$(gum input --placeholder "Enter your tweet here...")
        
        # Run the test using the current method and model
        cd "$BACKEND_DIR"
        source venv/bin/activate
        
        # Format the output nicely
        echo "\n${CYAN}🔍 Testing extraction...${RESET}"
        echo "Tweet: ${YELLOW}$TWEET${RESET}"
        echo "${CYAN}Method: ${YELLOW}$METHOD${RESET}"
        if [ -n "$MODEL_ID" ]; then
            echo "${CYAN}Model: ${YELLOW}$MODEL_ID${RESET}"
            RESULT=$(python main.py --method "$METHOD" --test-tweet "$TWEET" --model-id "$MODEL_ID")
        else
            RESULT=$(python main.py --method "$METHOD" --test-tweet "$TWEET")
        fi
        
        # Extract just the airline name from the result
        AIRLINE=$(echo "$RESULT" | grep "Extracted Airline(s):" | cut -d':' -f2- | xargs)
        echo "${GREEN}✅ Extracted: ${YELLOW}$AIRLINE${RESET}\n"
        ;;
    "Run Another Method")
        # ... existing Run Another Method code ...
        ;;
    "Save Log")
        # ... existing Save Log code ...
        ;;
    "Exit")
        echo "👋 Exiting... Have a great day!"
        exit 0
        ;;
    *)
        echo "${YELLOW}❌ Invalid choice${RESET}"
        exit 1
        ;;
esac
