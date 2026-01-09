"""
batch_processor.py - Handle batch downloads from files
"""
import os
import json

def read_urls_from_file(filepath):
    """Read URLs from text file"""
    urls = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    urls.append(line)
        return urls
    except Exception as e:
        print(f"Error reading file: {e}")
        return []

def save_batch_results(results, output_file="batch_results.json"):
    """Save batch download results to JSON file"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving results: {e}")
        return False

def validate_urls(urls):
    """Validate YouTube URLs"""
    validated = []
    invalid = []
    
    for url in urls:
        if 'youtube.com/watch' in url or 'youtu.be/' in url:
            validated.append(url)
        else:
            invalid.append(url)
    
    return validated, invalid