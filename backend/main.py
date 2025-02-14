# main.py

import argparse
import logging
import traceback
from pathlib import Path
import pandas as pd
from tqdm import tqdm
from config import OUTPUT_DIR, LOG_DIR, DATA_PATH
from utils.data_loader import load_dataset, save_results, save_comparison_metrics
from utils.openai_client import verify_connection
from extract.zero_shot import extract_airlines_zero_shot
from extract.one_shot import extract_airlines_one_shot
from extract.few_shot import extract_airlines_few_shot
from extract.embeddings import extract_airlines_embeddings
from extract.fine_tuned import (
    extract_airlines_fine_tuned, 
    prepare_training_data,
    create_fine_tuned_model,
    train_new_model
)
from extract.prompt_based import extract_airlines_prompt
import re
from utils.string_matcher import match_airline_name
import numpy as np
import sys
from utils.metrics_tracker import ExtractionMetrics
import time

# Add after imports
CLI_METHODS = ["zero-shot", "one-shot", "few-shot", "embeddings", "fine-tuned", "compare-all"]
EXTRACTION_METHODS = ["zero-shot", "one-shot", "few-shot", "embeddings", "fine-tuned"]

# ANSI color codes
GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
RED = "\033[31m"
RESET = "\033[0m"

# Create formatters
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_formatter = logging.Formatter('%(levelname)s - %(message)s')

# Set up root logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create and configure file handler
file_handler = logging.FileHandler(LOG_DIR / 'extraction.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(file_formatter)

# Create and configure console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)  # Only WARNING and above for console
console_handler.setFormatter(console_formatter)

# Remove any existing handlers
for handler in logger.handlers[:]:
    logger.removeHandler(handler)

# Add both handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

def extract_airlines(tweet, method, model_id=None):
    """Select extraction method."""
    try:
        if method == "zero-shot":
            return extract_airlines_zero_shot(tweet)
        elif method == "one-shot":
            return extract_airlines_one_shot(tweet)
        elif method == "few-shot":
            return extract_airlines_few_shot(tweet)
        elif method == "embeddings":
            return extract_airlines_embeddings(tweet)
        elif method == "fine-tuned":
            if not model_id:
                raise ValueError("Fine-tuned model ID required")
            return extract_airlines_fine_tuned(tweet, model_id)
        else:
            raise ValueError(f"Invalid method: {method}")
    except Exception as e:
        logging.error(f"Error processing tweet: {str(e)}")
        return None

def clean_airline_name(airline_text):
    """Clean airline name by removing numbers, brackets, quotes, and extra whitespace."""
    if not airline_text:
        return ""
    # Remove numbered list format (e.g., "1. ", "2. ")
    cleaned = re.sub(r'^\d+\.\s*', '', airline_text)
    # Remove array formatting
    cleaned = cleaned.strip('[]\'\" ')
    # Handle common variations
    replacements = {
        'USAirways': 'US Airways',
        'SouthwestAir': 'Southwest Airlines',
        'AmericanAir': 'American Airlines'
    }
    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new)
    return cleaned.strip()

def run_extraction(tweets, method, model_id=None):
    """Run extraction with metrics tracking."""
    print(f"\nRunning {method} extraction...")
    
    # Get extraction function
    if method in ["zero-shot", "one-shot", "few-shot"]:
        results, metrics = extract_airlines_prompt(tweets, method, track_metrics=True)
    elif method == "embeddings":
        results, metrics = extract_airlines_embeddings(tweets, track_metrics=True)
    elif method == "fine-tuned":
        results, metrics = extract_airlines_fine_tuned(tweets, model_id=model_id, track_metrics=True)
    else:
        raise ValueError(f"Invalid method: {method}")
    
    # Load original data for comparison
    data = load_dataset()  # This now returns cleaned airlines data
    
    # Update accuracy metrics
    exact_matches = 0
    similarity_scores = []
    
    for result, expected in zip(results, data['airlines']):
        is_exact, similarity = match_airline_name(result, expected)
        if is_exact:
            exact_matches += 1
        similarity_scores.append(similarity)
    
    metrics.exact_matches = exact_matches
    metrics.similarity_scores = similarity_scores
    
    # Save results
    save_results(results, method)
    
    return results, metrics

def run_comparison(methods, dataset, model_id=None):
    """Run multiple methods and compare their performance."""
    results = {}
    data = load_dataset(dataset)
    total = len(data)
    
    print("\n🔍 Evaluating Extraction Methods")
    print("=" * 50)
    
    # Create comparison files
    comparison_file = OUTPUT_DIR / "comparison_results.csv"
    summary_file = OUTPUT_DIR / "comparison_summary.csv"
    comparison_data = []
    summary_data = []
    
    for method in methods:
        correct = 0
        similarity_scores = []
        method_results = []
        total_tokens = 0
        total_cost = 0
        start_time = time.time()
        
        pbar = tqdm(data.iterrows(), 
                   total=total,
                   desc=f"Testing {method:<12}",
                   colour='green',
                   leave=True)
        
        for _, row in pbar:
            tweet = row['tweet']
            expected = row['airlines'].strip('[]\'\"')
            extracted, metrics = run_extraction([tweet], method, model_id if method == "fine-tuned" else None)
            
            total_tokens += metrics.total_tokens
            total_cost += metrics.costs[0]
            
            is_exact, similarity = match_airline_name(extracted[0], expected)
            similarity_scores.append(similarity)
            
            if is_exact:
                correct += 1
            
            method_results.append({
                'method': method,
                'tweet': tweet,
                'expected': expected,
                'extracted': extracted[0],
                'exact_match': is_exact,
                'similarity': similarity
            })
        
        # Calculate metrics
        accuracy = (correct/total) * 100
        avg_similarity = np.mean(similarity_scores) * 100
        total_time = time.time() - start_time
        
        # Store summary data
        summary_data.append({
            'method': method,
            'accuracy': accuracy,
            'similarity': avg_similarity,
            'tokens': total_tokens,
            'cost': total_cost,
            'time': total_time
        })
        
        comparison_data.extend(method_results)
    
    # Save detailed comparison results
    pd.DataFrame(comparison_data).to_csv(comparison_file, index=False)
    
    # Save summary results
    pd.DataFrame(summary_data).to_csv(summary_file, index=False)
    
    return results

def test_single_tweet(tweet, method, model_id=None):
    """Test extraction on a single tweet."""
    if method == "compare-all":
        print("\n🔍 Testing all methods...")
        results = []
        
        # Print the tweet being analyzed
        print(f"\n{CYAN}Tweet: {YELLOW}{tweet}{RESET}\n")
        
        # Collect all results first
        method_results = []
        for method in EXTRACTION_METHODS:
            try:
                if method == "fine-tuned":
                    if not model_id:
                        method_results.append((method, "Skipping (no model ID)", 0, 0, 0))
                        continue
                    result, metrics = extract_airlines_fine_tuned([tweet], model_id=model_id, track_metrics=True)
                elif method == "embeddings":
                    try:
                        result, metrics = extract_airlines_embeddings([tweet], track_metrics=True)
                    except FileNotFoundError:
                        method_results.append((method, "Skipping (training data not found)", 0, 0, 0))
                        continue
                else:
                    if method == "zero-shot":
                        result, metrics = extract_airlines_zero_shot([tweet], track_metrics=True)
                    elif method == "one-shot":
                        result, metrics = extract_airlines_one_shot([tweet], track_metrics=True)
                    elif method == "few-shot":
                        result, metrics = extract_airlines_few_shot([tweet], track_metrics=True)
                
                # Store results
                method_results.append((
                    method,
                    result[0],
                    metrics.total_tokens,
                    metrics.costs[0],
                    metrics.total_time
                ))
                
            except Exception as e:
                method_results.append((method, f"Error: {str(e)}", 0, 0, 0))
                continue
        
        # Print table after collecting all results
        print(f"{YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        print(f"{'Method':<15} {'Extracted':<30} {'Tokens':>8} {'Cost ($)':>10} {'Time (s)':>10}")
        print(f"{YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        
        for method, extracted, tokens, cost, time in method_results:
            # Truncate long extractions
            extracted = extracted[:27] + "..." if len(extracted) > 30 else extracted
            print(f"{method:<15} {extracted:<30} {tokens:>8} {cost:>10.4f} {time:>10.2f}")
            
        print(f"{YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        return
    else:
        # Original code for single method testing
        if method == "zero-shot":
            result, metrics = extract_airlines_zero_shot([tweet], track_metrics=True)
        elif method == "one-shot":
            result, metrics = extract_airlines_one_shot([tweet], track_metrics=True)
        elif method == "few-shot":
            result, metrics = extract_airlines_few_shot([tweet], track_metrics=True)
        elif method == "embeddings":
            result, metrics = extract_airlines_embeddings([tweet], track_metrics=True)
        elif method == "fine-tuned":
            result, metrics = extract_airlines_fine_tuned([tweet], model_id=model_id, track_metrics=True)
        else:
            raise ValueError(f"Invalid method: {method}")
        
        print("\n📊 Results:")
        print(f"Extracted Airline(s): {result[0]}")
        print(f"Tokens Used: {metrics.total_tokens}")
        print(f"Cost: ${metrics.costs[0]:.4f}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--method', default='zero-shot', 
                       choices=CLI_METHODS)  # Use CLI_METHODS for command line choices
    parser.add_argument('--dataset', type=str, help='Path to dataset CSV file')
    parser.add_argument('--model-id', type=str, help='Fine-tuned model ID', default=None)
    parser.add_argument('--train-model', action='store_true', help='Train a new fine-tuned model')
    parser.add_argument('--test-tweet', type=str, help='Single tweet to test extraction on')
    args = parser.parse_args()
    
    # Handle single tweet test
    if args.test_tweet:
        test_single_tweet(args.test_tweet, args.method, args.model_id)
        return
    
    # Handle model training request
    if args.train_model:
        try:
            model_id = train_new_model()
            print(model_id)  # Print just the model ID for shell script to capture
            return
        except Exception as e:
            logger.error(f"Failed to train model: {str(e)}")
            sys.exit(1)
    
    # Create output directory if it doesn't exist
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Verify OpenAI connection
    if not verify_connection():
        return
    
    # If fine-tuned method is selected and no model ID, create one first
    if args.method == 'fine-tuned' and not args.model_id:
        logger.info("Creating new fine-tuned model...")
        try:
            training_file = prepare_training_data()
            args.model_id = create_fine_tuned_model(training_file)
            logger.info(f"Successfully created fine-tuned model: {args.model_id}")
        except Exception as e:
            logger.error(f"Failed to create fine-tuned model: {str(e)}")
            return
        
    # Load dataset
    data_path = Path(args.dataset) if args.dataset else DATA_PATH
    logger.info(f"Loading dataset from {str(data_path)}")
    data = load_dataset(data_path)
    
    if args.method == 'compare-all':
        all_metrics = {}
        for method in EXTRACTION_METHODS:  # Use EXTRACTION_METHODS instead
            results, metrics = run_extraction(data['tweet'].tolist(), method, args.model_id)
            all_metrics[method] = metrics
        
        # Print all metrics after completion
        for method, metrics in all_metrics.items():
            print(f"\n{metrics.format_table()}")
            
        # Save combined metrics
        save_comparison_metrics(all_metrics)
    else:
        results, metrics = run_extraction(data['tweet'].tolist(), args.method, args.model_id)
        # Print metrics only after completion
        print(f"\n{metrics.format_table()}")

if __name__ == "__main__":
    main()
