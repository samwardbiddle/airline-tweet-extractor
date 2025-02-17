## Architecture

- `src/` - Core source code
  - `extract/` - Different extraction implementations
    - `prompt_based.py` - Prompt-based extraction (zero-shot, one-shot, few-shot)
    - `embeddings.py` - Embeddings extraction
    - `fine_tuned.py` - Trains and uses a fine-tuned model
    - `zero_shot.py` - Zero-shot classification using OpenAI (deprecated)
    - `few_shot.py` - Few-shot learning implementation (deprecated)
    - `fine_tuned.py` - Custom model handling (deprecated)
  - `pipeline/` - Main processing pipeline
  - `utils/` - Helper functions and utilities

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

The tool provides a simple command-line interface to experiment with different OpenAI API approaches for extracting airline names from tweets.

### Quick Start

1. Run the extraction script:

```bash
./run_extraction.sh
```

This interactive tool will guide you through:

1. Selecting a dataset from the `data/` directory
2. Choosing an extraction method
3. Optionally writing a single tweet prompt to verify results
4. Optionally running a comparison across all methods
5. Viewing accuracy, cost, and time metrics for each method
6. Reviewing a comparison summary

### Analyzing Results

To analyze the performance of different methods:

```bash
./analyze_results.sh
```

This will:

- Analyze extraction failures
- Suggest prompt improvements
- Generate detailed performance metrics
- Save results to the `output/` directory

### Output and Logs

Each run creates:

- A detailed log file in `logs/` with timestamps
- Results in `output/` including:
  - Extraction results
  - Accuracy metrics
  - Method comparisons
  - Cost analysis

### Available Methods

1. **Zero-shot**: Direct extraction without examples

   - Fastest and most token-efficient
   - Lower accuracy for specialized tasks
   - Lowest cost per API call

2. **One-shot**: Uses a single example

   - Balanced approach
   - Moderate token usage
   - Improved accuracy over zero-shot

3. **Few-shot**: Uses multiple examples

   - Better handling of edge cases
   - Higher token usage
   - Good accuracy for specific tasks

4. **Embeddings**: Uses semantic similarity

   - Good for fuzzy matching
   - Efficient for known airline lists
   - Moderate cost and accuracy

5. **Fine-tuned**: Uses custom-trained model
   - Highest accuracy
   - Initial training investment (30min-several hours)
   - Most cost-effective for large-scale use
   - Recommended for production use

For a video walkthrough of the tool, see: [Demo Video](https://www.loom.com/share/2e9196cdc6b445ad800a436456586a0f?sid=9f7289a4-7504-4772-aa01-6589f3cb2b0b)

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
