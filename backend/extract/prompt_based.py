from utils.openai_client import get_response
from utils.metrics_tracker import ExtractionMetrics
from .prompts import PROMPTS
import time
from tqdm import tqdm

def extract_airlines_prompt(tweets, method, track_metrics=True):
    """Extract airlines using prompt-based extraction."""
    if not isinstance(tweets, list):
        tweets = [tweets]
        
    start_time = time.time()
    results = []
    total_tokens = 0
    costs = []
    
    prompt_template = PROMPTS[method]
    
    for tweet in tqdm(tweets, desc="Processing", leave=False):
        prompt = prompt_template.format(tweet=tweet)
        result, usage = get_response(prompt, return_usage=True)
        results.append(result)
        
        if track_metrics:
            total_tokens += usage.total_tokens
            cost = (usage.prompt_tokens * 0.0015 + usage.completion_tokens * 0.002) / 1000
            costs.append(cost)
    
    if track_metrics:
        metrics = ExtractionMetrics(
            method_name=method.capitalize(),
            total_tokens=total_tokens,
            total_time=time.time() - start_time,
            total_tweets=len(tweets),
            exact_matches=0,  # Updated by main process
            similarity_scores=[],  # Updated by main process
            costs=costs
        )
        return results, metrics
    
    return results[0] if len(tweets) == 1 else results