import pandas as pd
from pathlib import Path
from utils.openai_client import get_response
from config import OUTPUT_DIR

ANALYSIS_PROMPT = """
Analyze these failed airline extractions and identify patterns in the errors.
Focus on why the model might have made these mistakes and how to improve the prompt.

Failed Examples:
{examples}

Please provide:
1. Common error patterns
2. Suggested improvements to the prompt
3. Specific examples of how these errors could be avoided
"""

def format_examples(failures, max_examples=10):
    """Format failure examples for the prompt."""
    examples = failures.sample(min(len(failures), max_examples))
    formatted = []
    for _, row in examples.iterrows():
        formatted.append(
            f"Tweet: '{row['tweet']}'\n"
            f"Expected: {row['expected']}\n"
            f"Extracted: {row['extracted']}\n"
        )
    return "\n".join(formatted)

def analyze_method_failures(method):
    """Analyze failures for a specific method and suggest improvements."""
    failures_file = OUTPUT_DIR / f"failures_{method}.csv"
    if not failures_file.exists():
        # Try reading from the results file instead
        results_file = OUTPUT_DIR / f"results_{method}.csv"
        if not results_file.exists():
            print(f"No data found for {method}")
            return
            
        # Read results and filter for failures
        results = pd.read_csv(results_file)
        failures = results[results['correct'] == False][['tweet', 'airlines', 'extracted']]
        # Rename column to match expected format
        failures = failures.rename(columns={'airlines': 'expected'})
    else:
        failures = pd.read_csv(failures_file)
    
    if len(failures) == 0:
        print(f"No failures to analyze for {method}")
        return
    
    print(f"\n🔍 Analyzing failures for {method}...")
    examples = format_examples(failures)
    prompt = ANALYSIS_PROMPT.format(examples=examples)
    
    analysis = get_response(prompt)
    
    print("\n📊 Analysis Results:")
    print("=" * 60)
    print(analysis)
    print("=" * 60)
    
    # Save analysis
    with open(OUTPUT_DIR / f"analysis_{method}.txt", "w") as f:
        f.write(f"Analysis for {method}\n")
        f.write("=" * 60 + "\n")
        f.write(analysis)

def analyze_failures():
    """Analyze failures for all methods."""
    methods = ["zero-shot", "one-shot", "few-shot", "embeddings"]
    for method in methods:
        analyze_method_failures(method)

if __name__ == "__main__":
    analyze_failures()