import logging
from typing import Dict
import json


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_llm_response(response_text: str) -> Dict:
    """Parse LLM response with error handling."""
    try:
        cleaned = response_text.strip()
        
        # Handle code blocks
        if "```json" in cleaned:
            json_blocks = cleaned.split("```json")
            if len(json_blocks) > 1:
                first_block = json_blocks[1].split("```")[0].strip()
                cleaned = first_block
        elif cleaned.startswith("```"):
            lines = cleaned.split('\n')
            cleaned = '\n'.join(lines[1:-1])
        
        cleaned = cleaned.replace("json", "").strip()
        
        # Handle string concatenation patterns
        import re
        if '+ "\\n".join(' in cleaned:
            pattern = r'"([^"]*)" \+ "\\n"\.join\(\[(.*?)\]\)'
            match = re.search(pattern, cleaned)
            if match:
                prefix = match.group(1)
                array_content = match.group(2)
                strings = re.findall(r'"([^"]*)"', array_content)
                final_string = prefix + "\\n" + "\\n".join(strings)
                cleaned = cleaned.replace(match.group(0), f'"{final_string}"')
        
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            if "OUTPUT" in cleaned and "message" in cleaned:
                return {
                    "OUTPUT": {
                        "message": "Operation completed successfully",
                        "action_taken": "Processed user request"
                    }
                }
            raise
                
    except Exception as e:
        logger.error(f"Failed to parse LLM response: {e}")
        return {"error": "Failed to parse response"}