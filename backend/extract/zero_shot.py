from utils.openai_client import get_response
from utils.metrics_tracker import ExtractionMetrics
import time
from tqdm import tqdm

def extract_airlines_zero_shot(tweets, track_metrics=True):
    """Extract airlines using zero-shot prompting."""
    if not isinstance(tweets, list):
        tweets = [tweets]
        
    start_time = time.time()
    results = []
    total_tokens = 0
    costs = []
    
    # Process each tweet with progress tracking
    for tweet in tqdm(tweets, desc="Processing", leave=False):
        prompt = f"""What airline is mentioned in this tweet? Only respond with the official airline name, not an abbreviation or variation on the name. If there is no airline name, return "No airline found".

        Tweet: '{tweet}'"""
        
        result, usage = get_response(prompt, return_usage=True)
        results.append(result)
        
        if track_metrics:
            total_tokens += usage.total_tokens
            # Calculate cost (adjust rates as needed)
            cost = (usage.prompt_tokens * 0.0015 + usage.completion_tokens * 0.002) / 1000
            costs.append(cost)
    
    if track_metrics:
        metrics = ExtractionMetrics(
            method_name="Zero-shot",
            total_tokens=total_tokens,
            total_time=time.time() - start_time,
            total_tweets=len(tweets),
            exact_matches=0,  # This will be updated by the main process
            similarity_scores=[],  # This will be updated by the main process
            costs=costs
        )
        return results, metrics
    
    return results[0] if len(tweets) == 1 else results
