from utils.openai_client import get_response
from utils.metrics_tracker import ExtractionMetrics
import time
from tqdm import tqdm

EXAMPLES = """Tweet: '@AmericanAir your service is terrible!'
Airlines: American Airlines

Tweet: '@United to LAX then @SouthwestAir to Vegas'
Airlines: United Airlines, Southwest Airlines

Tweet: '@USAirways and @JetBlue both lost my bags today'
Airlines: US Airways, JetBlue Airways

Tweet: '@VirginAmerica best airline ever'
Airlines: Virgin America"""

def extract_airlines_few_shot(tweets, track_metrics=True):
    """Extract airlines using few-shot prompting."""
    if not isinstance(tweets, list):
        tweets = [tweets]
        
    start_time = time.time()
    results = []
    total_tokens = 0
    costs = []
    
    for tweet in tqdm(tweets, desc="Processing", leave=False):
        prompt = f"""Extract the official airline names from the tweet. Use the examples format below:

{EXAMPLES}

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
            method_name="Few-shot",
            total_tokens=total_tokens,
            total_time=time.time() - start_time,
            total_tweets=len(tweets),
            exact_matches=0,  # Updated by main process
            similarity_scores=[],  # Updated by main process
            costs=costs
        )
        return results, metrics
    
    return results[0] if len(tweets) == 1 else results
