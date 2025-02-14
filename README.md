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

```
git clone https://github.com/yourusername/airline-tweet-extractor.git
```

2. Install dependencies:

Run the setup script:

```
./setup.sh
```

This will install the dependencies and set up the environment. As long as you have the prerequisites installed, you should be able to run all setup scripts successfully. The setup script will also prompt you to enter your OpenAI API key, which will be saved in the `.env` file. The repository includes a `.env.example` file that shows the required variables and is set to ignore the `.env` file by default.

Alternatively, you can install the dependencies manually:

```
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Then create your `.env` file:

```
cp .env.example .env
```

Edit the `.env` file with your OpenAI API key:

```
OPENAI_API_KEY=your-api-key
```

## Usage

Run the extraction tool using the shell script:

```
./run_extraction.sh
```

This will give you the ability to select a dataset, and your method of choice. It also gives you the option to write a single tweet prompt and verify the results for test. You will be able to see the accuracy, cost, and time taken for each method and run comparison across all methods. The command line tool will prompt you to:

1. Select a dataset
2. Select a method
3. Optional: Write a single tweet prompt and verify the results for test
4. Optional: Run comparison across all methods
5. See the accuracy, cost, and time taken for each method
6. See the comparison summary

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

For a video walkthrough of the tool, please see the video here: https://www.loom.com/share/2e9196cdc6b445ad800a436456586a0f?sid=9f7289a4-7504-4772-aa01-6589f3cb2b0b
