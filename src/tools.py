import os
import requests
from typing import List, Dict, Any, Optional
import trafilatura
from src.services.togetherai import client

import logging
logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO) 


def start_agent():
    """Start the agent loop"""
    return {"status": "Agent started", "running": True}

def finalize_output():
    """Signal that the agent workflow is complete (no final text here)."""
    return {
        "status": "Agent stopped",
        "running": False
    }

def search_web(query: str, num_results: int = 5) -> Optional[List[Dict[str, Any]]]:
        """
        Search using Google Custom Search API
        
        Args:
            query: Search query
            num_results: Number of results to return (max 10 per request)
            start_index: Starting index for results
            
        Returns:
            List of search results or None if error
        """
        try:
            params = {
                'key': os.getenv("GOOGLE_API_KEY", ""),
                'cx': os.getenv("GOOGLE_SEARCH_ENGINE_ID", ""),
                'q': query,
                'num': min(num_results, 10),  # Google CSE max is 10 per request
                'start': 1
            }
            
            response = requests.get("https://www.googleapis.com/customsearch/v1", params=params)
            response.raise_for_status()
            
            data = response.json()

            logger.info(f"Search response: {data}")
            
            if 'items' in data:
                results = []
                for item in data['items']:
                    result = {
                        'title': item.get('title', ''),
                        'link': item.get('link', ''),
                        'snippet': item.get('snippet', ''),
                    }
                    results.append(result)
                
                logger.info(f"Found {len(results)} results for query: {query}")
                return results
            else:
                logger.warning(f"No results found for query: {query}")
                return []
                
        except requests.RequestException as e:
            logger.error(f"Request error during search: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error during search: {str(e)}")
            return None

def read_url(url: str, intent: str = "extract") -> Dict[str, Any]:
    """Process content using Trafilatura"""
    # Extract content using Trafilatura

    raw_data = requests.get(url)
    content = trafilatura.extract(raw_data)
    if not content:
        return None
    if intent:
        simplified_response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": f"You are a helpful assistant that simplifies content for the intent: {intent}."
                },
                {
                    "role": "user",
                    "content": content
                }
            ],
        )
        content = simplified_response.choices[0].message.content if intent else content 
        return {
            "url": url,
            "content": content,
            "status": "success"
        }
    return {
        'url': url,
        'content': content,
        'raw_text': content,
    }


# Define available tools
tools = [
    {
        "type": "function",
        "function": {
            "name": "finalize_output",
            "description": "Signal the agent workflow is complete. Call this exactly once when you are ready to produce the final synthesized answer.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the web for information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of search results to return (max 10)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_url",
            "description": "Read content from a URL",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to read"
                    },
                    "intent": {
                        "type": "string",
                        "description": "The intent for reading the URL, e.g., \"get key points for ...\"",
                        "default": "Key points"
                    }
                },
                "required": ["url"]
            }
        }
    }
]

# Function mapping
function_map = {
    "start_agent": start_agent,
    "finalize_output": finalize_output,
    "search_web": search_web,
    "read_url": read_url
}