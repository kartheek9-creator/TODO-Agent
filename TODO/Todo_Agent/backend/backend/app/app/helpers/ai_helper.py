
import google.generativeai as genai
from app.helpers import data_helper as datah
import logging
from typing import Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


GEMINI_API_KEY = "AIzaSyCg5nIJmlIYr-8Ez_aZmO7RsxwNde4wfUE"
genai.configure(api_key=GEMINI_API_KEY)

# Pure functions for LLM operations
def create_gemini_client() -> genai.GenerativeModel:
    """Create and return a Gemini client."""
    return genai.GenerativeModel(model_name="gemini-1.5-flash")

def call_llm(prompt: str, client: genai.GenerativeModel) -> Dict:
    """Call LLM with given prompt."""
    try:
        response = client.generate_content(prompt)
        return datah.parse_llm_response(response.text)
    except Exception as e:
        logger.error(f"Error calling LLM: {e}")
        return {"error": str(e)}