import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the project root directory
ROOT_DIR = Path(__file__).parent.parent

# Define paths
DATA_PATH = ROOT_DIR / 'data' / 'airline_test.csv'
TRAIN_DATA_PATH = ROOT_DIR / 'data' / 'airline_train.csv'
OUTPUT_DIR = ROOT_DIR / 'output'
LOG_DIR = ROOT_DIR / 'logs'

# Create directories if they don't exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# OpenAI API configuration
OPENAI_MODEL = "gpt-3.5-turbo"
OPENAI_TEMPERATURE = 0

# Cost tracking (per 1K tokens)
COSTS = {
    'gpt-3.5-turbo': {
        'input': 0.0015,
        'output': 0.002
    },
    'embeddings': {
        'input': 0.0001,
        'output': 0.0001
    },
    'fine-tuned': {
        'input': 0.003,
        'output': 0.006
    }
}

# OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY not found in environment variables. Please add it to your .env file.")

MODEL = "gpt-3.5-turbo"
TEMPERATURE = 0

# Directory configuration
DATA_DIR = ROOT_DIR / "data"
OUTPUT_DIR = ROOT_DIR / "output"
LOG_DIR = ROOT_DIR / "logs"

# Ensure directories exist
for directory in [DATA_DIR, OUTPUT_DIR, LOG_DIR]:
    directory.mkdir(exist_ok=True)
