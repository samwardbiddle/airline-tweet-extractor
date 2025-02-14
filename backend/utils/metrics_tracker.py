import time
from dataclasses import dataclass
from typing import List
import numpy as np

@dataclass
class ExtractionMetrics:
    method_name: str
    total_tokens: int
    total_time: float
    total_tweets: int
    exact_matches: int
    similarity_scores: List[float]
    costs: List[float]
    
    @property
    def accuracy(self) -> float:
        return (self.exact_matches / self.total_tweets) * 100 if self.total_tweets > 0 else 0
    
    @property
    def avg_similarity(self) -> float:
        return np.mean(self.similarity_scores) if self.similarity_scores else 0
    
    @property
    def avg_time_per_tweet(self) -> float:
        return self.total_time / self.total_tweets if self.total_tweets > 0 else 0
    
    @property
    def avg_tokens_per_tweet(self) -> float:
        return self.total_tokens / self.total_tweets if self.total_tweets > 0 else 0
    
    @property
    def avg_cost_per_tweet(self) -> float:
        return np.mean(self.costs) if self.costs else 0
    
    def format_table(self) -> str:
        """Return metrics formatted as a table string."""
        return f"""
📊 {self.method_name} Metrics
{'=' * 50}
🎯 Accuracy Metrics:
   • Exact Matches:    {self.exact_matches}/{self.total_tweets} ({self.accuracy:.1f}%)
   • Avg Similarity:   {self.avg_similarity:.1f}%

⏱️  Performance Metrics:
   • Total Time:       {self.total_time:.2f}s
   • Avg Time/Tweet:   {self.avg_time_per_tweet*1000:.1f}ms
   • Total Tokens:     {self.total_tokens:,}
   • Avg Tokens/Tweet: {self.avg_tokens_per_tweet:.1f}

💰 Cost Metrics:
   • Total Cost:       ${sum(self.costs):.4f}
   • Avg Cost/Tweet:   ${self.avg_cost_per_tweet:.4f}
{'=' * 50}
"""