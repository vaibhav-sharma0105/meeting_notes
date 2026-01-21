import webvtt
import io
import json
from typing import List, Dict, Any
from models import TranscriptChunk, Task

def parse_vtt(file_content: str) -> List[Dict[str, Any]]:
    """
    Parses WebVTT content and merges consecutive turns by the same speaker.
    Returns a list of dicts suitable for creating TranscriptChunk objects.
    """
    buffer = io.StringIO(file_content)
    vtt = webvtt.read_buffer(buffer)

    chunks = []
    current_chunk = None

    for caption in vtt:
        start = in_seconds(caption.start)
        end = in_seconds(caption.end)
        # WebVTT often has "<v SpeakerName>Text</v>" or just "SpeakerName: Text"
        # We need a robust extraction. For Zoom, it's often "Speaker Name: Text"

        raw_text = caption.text.strip()
        speaker = "Unknown"
        text = raw_text

        if ":" in raw_text:
            parts = raw_text.split(":", 1)
            speaker = parts[0].strip()
            text = parts[1].strip()

        # Merge logic
        if current_chunk and current_chunk['speaker'] == speaker and (start - current_chunk['end_time'] < 1.0):
            current_chunk['end_time'] = end
            current_chunk['text'] += " " + text
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = {
                "start_time": start,
                "end_time": end,
                "speaker": speaker,
                "text": text
            }

    if current_chunk:
        chunks.append(current_chunk)

    return chunks

def in_seconds(timestamp_str: str) -> float:
    # webvtt-py might handle this, but to be safe or if using raw strings
    # format: HH:MM:SS.mmm
    parts = timestamp_str.split(':')
    seconds = 0.0
    if len(parts) == 3:
        seconds += float(parts[0]) * 3600
        seconds += float(parts[1]) * 60
        seconds += float(parts[2])
    elif len(parts) == 2:
        seconds += float(parts[0]) * 60
        seconds += float(parts[1])
    return seconds

def parse_summary(file_content: str, file_type: str = "json") -> Dict[str, Any]:
    """
    Parses a summary file.
    If JSON, expects keys like 'overview', 'decisions', 'tasks'.
    If Text, returns raw text for LLM processing later.
    """
    if file_type == "json":
        try:
            data = json.loads(file_content)
            return data
        except json.JSONDecodeError:
            return {"error": "Invalid JSON"}
    else:
        # For raw text, we just return the text wrapper
        return {"raw_text": file_content}

def extract_tasks_from_summary(summary_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extracts tasks from the parsed summary data.
    Assumes standard Zoom/LLM JSON structure if available.
    """
    tasks = []
    # Heuristic for common formats
    if "action_items" in summary_data:
        for item in summary_data["action_items"]:
            # item could be string or dict
            if isinstance(item, str):
                tasks.append({"description": item})
            elif isinstance(item, dict):
                tasks.append({
                    "description": item.get("action", item.get("description", "")),
                    "assignee": item.get("owner", item.get("assignee", None))
                })
    elif "tasks" in summary_data:
         for item in summary_data["tasks"]:
             if isinstance(item, str):
                tasks.append({"description": item})
             elif isinstance(item, dict):
                tasks.append({
                    "description": item.get("description", ""),
                    "assignee": item.get("assignee", None)
                })
    return tasks
