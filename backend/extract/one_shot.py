from utils.openai_client import get_response
from utils.metrics_tracker import ExtractionMetrics
import time
from tqdm import tqdm

EXAMPLE = """Tweet: '@AmericanAir your service is terrible!'
Airlines: American Airlines"""

def extract_airlines_one_shot(tweets, track_metrics=True):
    """Extract airlines using one-shot prompting."""
    if not isinstance(tweets, list):
        tweets = [tweets]
        
    start_time = time.time()
    results = []
    total_tokens = 0
    costs = []
    
    for tweet in tqdm(tweets, desc="Processing", leave=False):
        prompt = f"""Extract the official airline name from the tweet. If there is no airline name, return "No airline found". Use the example format below:

{EXAMPLE}

Tweet: '{tweet}'
Airlines:"""
        
        result, usage = get_response(prompt, return_usage=True)
        results.append(result)
        
        if track_metrics:
            total_tokens += usage.total_tokens
            cost = (usage.prompt_tokens * 0.0015 + usage.completion_tokens * 0.002) / 1000
            costs.append(cost)
    
    if track_metrics:
        metrics = ExtractionMetrics(
            method_name="One-shot",
            total_tokens=total_tokens,
            total_time=time.time() - start_time,
            total_tweets=len(tweets),
            exact_matches=0,  # Updated by main process
            similarity_scores=[],  # Updated by main process
            costs=costs
        )
        return results, metrics
    
    return results[0] if len(tweets) == 1 else results
