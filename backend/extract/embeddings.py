from utils.openai_client import client
from utils.metrics_tracker import ExtractionMetrics
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from pathlib import Path
import time
from tqdm import tqdm
from config import TRAIN_DATA_PATH

def learn_from_training(training_file=None):
    """Learn common airline patterns from training data."""
    if training_file is None:
        training_file = TRAIN_DATA_PATH
    df = pd.read_csv(training_file)
    unique_airlines = set()
    
    # Extract unique airline names from training data
    for airlines in df['airlines'].dropna():
        airlines = airlines.strip('[]\'\"').split(',')
        unique_airlines.update([airline.strip() for airline in airlines])
    
    return list(unique_airlines)

def extract_airlines_embeddings(tweets, track_metrics=True):
    """Extract airlines using semantic similarity and embeddings."""
    if not isinstance(tweets, list):
        tweets = [tweets]
        
    try:
        # Load training data using the correct path
        training_data = pd.read_csv(TRAIN_DATA_PATH)
    except FileNotFoundError:
        print(f"Training data file not found at {TRAIN_DATA_PATH}")
        return
    
    start_time = time.time()
    results = []
    total_tokens = 0
    costs = []
    
    # Get known airlines once for all tweets
    known_airlines = learn_from_training()
    
    for tweet in tqdm(tweets, desc="Processing", leave=False):
        # Get embedding for the tweet
        tweet_emb_response = client.embeddings.create(
            input=tweet,
            model="text-embedding-ada-002"
        )
        tweet_embedding = tweet_emb_response.data[0].embedding
        tweet_tokens = tweet_emb_response.usage.total_tokens
        
        # Use the chat API with context
        prompt = f"""Extract airline names from this tweet. Common airlines include: {', '.join(known_airlines)}
        
        Tweet: '{tweet}'
        Airlines (one per line):"""
        
        chat_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Extract potential airline names from the tweet, one per line."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        
        potential_airlines = chat_response.choices[0].message.content.strip().split('\n')
        
        # Get embeddings for potential airlines
        airlines_emb_response = client.embeddings.create(
            input=potential_airlines,
            model="text-embedding-ada-002"
        )
        
        # Track metrics
        if track_metrics:
            total_tokens += (tweet_tokens + 
                           chat_response.usage.total_tokens + 
                           airlines_emb_response.usage.total_tokens)
            embedding_cost = (tweet_tokens + airlines_emb_response.usage.total_tokens) * 0.0001 / 1000
            chat_cost = ((chat_response.usage.prompt_tokens * 0.0015 + 
                         chat_response.usage.completion_tokens * 0.002) / 1000)
            costs.append(embedding_cost + chat_cost)
        
        # Find strong matches
        matches = []
        for airline, airline_emb in zip(potential_airlines, airlines_emb_response.data):
            similarity = cosine_similarity([tweet_embedding], [airline_emb.embedding])[0][0]
            if similarity > 0.8:
                matches.append(airline.strip())
        
        results.append(', '.join(matches) if matches else 'No airline found')
    
    if track_metrics:
        metrics = ExtractionMetrics(
            method_name="Embeddings",
            total_tokens=total_tokens,
            total_time=time.time() - start_time,
            total_tweets=len(tweets),
            exact_matches=0,  # Updated by main process
            similarity_scores=[],  # Updated by main process
            costs=costs
        )
        return results, metrics
    
    return results[0] if len(tweets) == 1 else results