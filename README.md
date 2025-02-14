## Architecture

- `src/` - Core source code
  - `extractors/` - Different extraction implementations
    - `zero_shot.py` - Zero-shot classification using OpenAI
    - `few_shot.py` - Few-shot learning implementation
    - `fine_tuned.py` - Custom model handling
  - `pipeline/` - Main processing pipeline
  - `utils/` - Helper functions and utilities

## Features

### Extraction Methods

- **Zero-shot Classification**
  - Uses OpenAI's GPT-4 for direct classification
  - No training examples required
  - Configurable classification parameters
- **Few-shot Learning**
  - Leverages example-based learning
  - Customizable prompt templates
  - Dynamic example selection
- **Fine-tuned Models**
  - Custom models trained on airline data
  - Support for multiple model architectures
  - Model versioning and management

### Analysis Components

- Airline mention extraction
- Sentiment analysis (Positive/Negative/Neutral)
- Confidence scoring
- Entity relationship mapping

## Setup

1. Clone or unzip the repository

2. Install dependencies:

bash
pip install -r requirements.txt

3. Set up your OpenAI API key:

bash
export OPENAI_API_KEY='your-api-key'

## Usage

Run the extraction tool using the shell script:

bash
./run_extraction.sh

### Available Options

1. **Select Dataset**: Choose from available CSV files in the data directory
2. **Choose Method**:

   - Zero-shot: Direct extraction without examples
   - One-shot: Uses a single example
   - Few-shot: Uses multiple examples
   - Embeddings: Uses embedding similarity
   - Fine-tuned: Uses a custom-trained model
   - Compare All: Runs all methods and compares results

3. **View Results**: See detailed extraction results and accuracy metrics

## Fine-tuned Models

To use fine-tuned models:

1. Select "Fine-tuned" method
2. Choose to use an existing model or train a new one
3. View extraction results

## Output

Results are saved in the `output` directory with:

- Extraction results
- Accuracy metrics
- Comparison data (when using Compare All)

## Logs

Logs are stored in the `logs` directory with timestamps for tracking and debugging.
