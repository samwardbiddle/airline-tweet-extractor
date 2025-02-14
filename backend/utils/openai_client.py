import openai
import logging
import time
from config import OPENAI_API_KEY, MODEL, TEMPERATURE
import os

# Initialize the client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

def verify_connection():
    """Verify OpenAI API connection."""
    try:
        # Simple test call with new API syntax
        client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5
        )
        logging.info("✅ OpenAI API connection successful")
        return True
    except Exception as e:
        logging.error(f"❌ OpenAI API connection failed: {str(e)}")
        return False

def get_response(prompt, return_usage=False):
    """Get response from OpenAI API."""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=TEMPERATURE
        )
        
        result = response.choices[0].message.content.strip()
        
        if return_usage:
            return result, response.usage
        return result
        
    except Exception as e:
        logging.error(f"❌ Error getting response: {str(e)}")
        raise
