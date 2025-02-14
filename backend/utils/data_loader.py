import pandas as pd
import logging
from pathlib import Path
from config import DATA_PATH, OUTPUT_DIR
from utils.string_matcher import match_airline_name
from datetime import datetime

def get_timestamp():
    """Get current timestamp formatted for filenames."""
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def clean_airlines_field(airlines_str):
    """Clean the airlines field by removing brackets and quotes."""
    return airlines_str.strip('[]\'\"').replace("'", "")

def load_dataset(path=DATA_PATH):
    """Load dataset from CSV file."""
    try:
        logging.info(f"Loading dataset from {path}")
        df = pd.read_csv(path)
        df['airlines'] = df['airlines'].apply(clean_airlines_field)
        return df
    except Exception as e:
        logging.error(f"Error loading dataset: {str(e)}")
        raise

def save_results(results, method):
    """Save extraction results to CSV file."""
    try:
        timestamp = get_timestamp()
        output_path = OUTPUT_DIR / f"results_{method}_{timestamp}.csv"
        
        # Load original dataset to get tweets and correct airlines
        data = load_dataset()
        
        # Create results DataFrame with all required columns
        results_data = []
        for i, (tweet, extracted) in enumerate(zip(data['tweet'], results)):
            correct = data['airlines'].iloc[i]
            is_exact, similarity = match_airline_name(extracted, correct)
            
            results_data.append({
                'tweet': tweet,
                'correct': correct,
                'extracted': extracted,
                'exact_match': is_exact,
                'similarity': f"{similarity:.1f}"
            })
        
        # Convert to DataFrame and save
        df = pd.DataFrame(results_data)
        df.to_csv(output_path, index=False)
        logging.info(f"Results saved to {output_path}")
        return output_path
    except Exception as e:
        logging.error(f"Error saving results: {str(e)}")
        raise

def save_comparison_metrics(all_metrics):
    """Save comparison metrics to CSV file."""
    try:
        timestamp = get_timestamp()
        comparison_data = []
        for method, metrics in all_metrics.items():
            comparison_data.append({
                'Method': metrics.method_name,
                'Accuracy': f"{metrics.accuracy:.1f}%",
                'Avg Similarity': f"{metrics.avg_similarity:.1f}%",
                'Total Time': f"{metrics.total_time:.2f}s",
                'Time/Tweet': f"{metrics.avg_time_per_tweet*1000:.1f}ms",
                'Total Tokens': metrics.total_tokens,
                'Tokens/Tweet': f"{metrics.avg_tokens_per_tweet:.1f}",
                'Cost/Tweet': f"${metrics.avg_cost_per_tweet:.4f}"
            })
        
        df = pd.DataFrame(comparison_data)
        output_path = OUTPUT_DIR / f"comparison_summary_{timestamp}.csv"
        df.to_csv(output_path, index=False)
        logging.info(f"Comparison metrics saved to {output_path}")
        return output_path
    except Exception as e:
        logging.error(f"Error saving comparison metrics: {str(e)}")
        raise
