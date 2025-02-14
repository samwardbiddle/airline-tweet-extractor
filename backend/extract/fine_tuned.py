from utils.openai_client import client
import pandas as pd
import json
from pathlib import Path
import time
import logging
import sys
from utils.metrics_tracker import ExtractionMetrics
from tqdm import tqdm

logger = logging.getLogger(__name__)

def prepare_training_data(training_file=None):
    """Convert training data to fine-tuning format for chat models."""
    if training_file is None:
        training_file = Path(__file__).parent.parent.parent / 'data' / 'airline_train.csv'
    
    print(f"\n🔄 Loading training data from {training_file}")
    df = pd.read_csv(training_file)
    print(f"📊 Found {len(df)} training examples")
    
    training_data = []
    for idx, row in enumerate(df.iterrows(), 1):
        _, row = row  # Unpack the row
        airlines = row['airlines'].strip('[]\'\"')
        training_example = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that extracts airline names from tweets. Only respond with the official airline names, separated by commas if there are multiple airlines."
                },
                {
                    "role": "user",
                    "content": f"Extract airlines from this tweet: {row['tweet']}"
                },
                {
                    "role": "assistant",
                    "content": airlines
                }
            ]
        }
        training_data.append(training_example)
        if idx % 100 == 0:
            print(f"⏳ Processed {idx}/{len(df)} examples...")
    
    output_file = Path(__file__).parent.parent.parent / 'data' / 'fine_tuning.jsonl'
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"\n💾 Saving training data to {output_file}")
    with open(output_file, 'w') as f:
        for example in training_data:
            f.write(json.dumps(example) + '\n')
    
    print(f"✅ Successfully created training file with {len(training_data)} examples\n")
    return output_file

def create_fine_tuned_model(training_file):
    """Create a new fine-tuned model using the training data."""
    try:
        print("\n🚀 Starting fine-tuning process...")
        print("Step 1/4: Uploading training file to OpenAI...")
        
        upload_response = client.files.create(
            file=open(training_file, 'rb'),
            purpose='fine-tune'
        )
        file_id = upload_response.id
        print(f"✅ File uploaded successfully (ID: {file_id})")
        
        print("\nStep 2/4: Creating fine-tuning job...")
        job = client.fine_tuning.jobs.create(
            training_file=file_id,
            model="gpt-3.5-turbo",
            suffix="airline-extractor"
        )
        print(f"✅ Job created successfully (ID: {job.id})")
        
        print("\nStep 3/4: Training model (this may take 15-30 minutes)...")
        print("Current status: ", end="", flush=True)
        
        status_emoji = {
            'validating_files': '📋',
            'queued': '⏳',
            'running': '⚡',
            'succeeded': '✅',
            'failed': '❌'
        }
        
        last_status = None
        while job.status in ['validating_files', 'queued', 'running']:
            if job.status != last_status:
                emoji = status_emoji.get(job.status, '🔄')
                print(f"\n{emoji} Status: {job.status.upper()}")
                last_status = job.status
            print(".", end="", flush=True)
            time.sleep(10)
            job = client.fine_tuning.jobs.retrieve(job.id)
        
        print("\n\nStep 4/4: Finalizing...")
        if job.status == 'succeeded':
            print(f"\n✨ Success! Your new fine-tuned model is ready:")
            print(f"📎 Model ID: {job.fine_tuned_model}")
            print(f"🎯 Base Model: GPT-3.5 Turbo")
            print(f"📊 Training Examples: {job.training_file}")
            return job.fine_tuned_model
        else:
            print(f"\n❌ Fine-tuning failed with status: {job.status}")
            if hasattr(job, 'error'):
                print(f"Error details: {job.error}")
            raise Exception(f"Fine-tuning failed with status: {job.status}")
            
    except Exception as e:
        print(f"\n❌ Error during fine-tuning: {str(e)}")
        raise

def get_available_models():
    """Get list of available fine-tuned models from OpenAI."""
    try:
        models = client.models.list()
        
        # Filter for fine-tuned models
        fine_tuned_models = [
            model.id for model in models 
            if (model.owned_by == "organization-owner" or model.id.startswith('ft:')) 
            and "ckpt" not in model.id
        ]
        
        if fine_tuned_models:
            # Just return the IDs, let the shell script handle display
            return fine_tuned_models
        else:
            return []
            
    except Exception as e:
        print(f"\n❌ Error checking models: {str(e)}", file=sys.stderr)
        return []

def verify_model_exists(model_id):
    """Verify if a specific model ID exists and is available."""
    try:
        client.models.retrieve(model_id)
        return True
    except Exception:
        return False

def extract_airlines_fine_tuned(tweets, model_id=None, track_metrics=True):
    """Use the fine-tuned model to extract airlines."""
    if not isinstance(tweets, list):
        tweets = [tweets]
        
    start_time = time.time()
    results = []
    total_tokens = 0
    costs = []
    
    try:
        if not model_id:
            available_models = get_available_models()
            if not available_models:
                raise ValueError("No fine-tuned models available")
            model_id = available_models[0]
        
        # Only print model ID once at the start
        if not hasattr(extract_airlines_fine_tuned, 'model_printed'):
            print(f"\n🎯 Using fine-tuned model: {model_id}")
            extract_airlines_fine_tuned.model_printed = True
            
        for tweet in tqdm(tweets, desc="Processing", leave=False):
            response = client.chat.completions.create(
                model=model_id,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that extracts airline names from tweets. Only respond with the official airline names, separated by commas if there are multiple airlines."
                    },
                    {
                        "role": "user",
                        "content": f"Extract airlines from this tweet: {tweet}"
                    }
                ],
                temperature=0
            )
            
            result = response.choices[0].message.content.strip()
            results.append(result)
            print(f"✅ Successfully extracted: {result}")
            
            if track_metrics:
                total_tokens += response.usage.total_tokens
                cost = (response.usage.prompt_tokens * 0.003 + response.usage.completion_tokens * 0.006) / 1000
                costs.append(cost)
        
        if track_metrics:
            metrics = ExtractionMetrics(
                method_name="Fine-tuned",
                total_tokens=total_tokens,
                total_time=time.time() - start_time,
                total_tweets=len(tweets),
                exact_matches=0,  # Updated by main process
                similarity_scores=[],  # Updated by main process
                costs=costs
            )
            return results, metrics
            
        return results[0] if len(tweets) == 1 else results
            
    except Exception as e:
        print(f"\n❌ Error in extraction: {str(e)}")
        raise

def train_new_model():
    """Create a new fine-tuned model and return its ID."""
    try:
        print("\n🔄 Preparing training data...")
        training_file = prepare_training_data()
        
        print("\n🚀 Training new model...")
        model_id = create_fine_tuned_model(training_file)
        
        print(f"\n✅ Successfully created model: {model_id}")
        return model_id
    except Exception as e:
        print(f"\n❌ Error training model: {str(e)}")
        raise