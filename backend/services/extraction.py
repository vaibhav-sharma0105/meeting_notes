from typing import List, Dict, Any
import json
from litellm import completion
from core.config import settings

def extract_action_items(text: str) -> List[Dict[str, Any]]:
    """
    Uses the configured LLM to extract action items, assignees, and dates from text.
    Returns a list of dicts: {'description': str, 'assignee': str, 'due_date': str}
    """
    config = settings.get_llm_config()
    model_name = config.get("model", "gpt-4o")

    prompt = f"""
    You are an expert meeting analyst. Extract all action items (tasks) from the following text.
    For each task, identify:
    1. Description: What needs to be done.
    2. Assignee: Who is responsible (if mentioned, otherwise "Unassigned").
    3. Due Date: If mentioned (YYYY-MM-DD or relative), otherwise null.

    Return ONLY a JSON array of objects. Example:
    [
        {{"description": "Update the roadmap", "assignee": "Alice", "due_date": "2023-10-15"}},
        {{"description": "Fix login bug", "assignee": "Bob", "due_date": null}}
    ]

    Text to analyze:
    {text[:4000]}  # Truncate to avoid context limit for MVP
    """

    try:
        response = completion(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            api_key=config.get("api_key"),
            api_base=config.get("api_base"),
            format="json" # Force JSON if supported by provider
        )

        content = response.choices[0].message.content
        # Clean markdown code blocks if present
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        tasks = json.loads(content.strip())
        return tasks
    except Exception as e:
        print(f"Extraction failed: {e}")
        return []
