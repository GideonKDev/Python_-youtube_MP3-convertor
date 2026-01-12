import sys
import os
sys.path.append('.')

from converter import youtube_to_mp3

# Test URL
test_url = "https://youtu.be/PQVWiAtNX58"

print("Testing youtube_to_mp3 function...")
print(f"URL: {test_url}")

try:
    result = youtube_to_mp3(test_url, "test_output", "192")
    print(f"Result type: {type(result)}")
    print(f"Result: {result}")
    
    # Try to access the result
    if isinstance(result, dict):
        print(f"Success: {result.get('success')}")
        print(f"Error: {result.get('error')}")
    else:
        print(f"ERROR: Result is not a dict! It's: {type(result)}")
        print(f"Result value: {result}")
        
except Exception as e:
    print(f"Exception during youtube_to_mp3: {e}")
    import traceback
    traceback.print_exc()