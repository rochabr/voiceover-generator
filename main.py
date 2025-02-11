import os
import json
import time
import requests
import shutil
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def process_voiceovers(todo_dir, done_dir):
    # Get environment variables
    API_URL = os.getenv('TTS_API_URL')
    API_KEY = os.getenv('TTS_API_KEY')
    
    if not API_URL or not API_KEY:
        raise EnvironmentError("Missing required environment variables. Please check your .env file")

    # Create directories if they don't exist
    Path(todo_dir).mkdir(parents=True, exist_ok=True)
    Path(done_dir).mkdir(parents=True, exist_ok=True)

    # API configuration
    params = {"api-version": "2024-05-01-preview"}
    headers = {
        "api-key": API_KEY,
        "Content-Type": "application/json"
    }

    voiceover_count = 0

    # Process all JSON files in todo directory
    for filename in os.listdir(todo_dir):
        if not filename.endswith('.json'):
            continue

        file_path = os.path.join(todo_dir, filename)
        
        try:
            # Read JSON file
            with open(file_path, 'r') as f:
                data = json.load(f)

            # Create output directory based on title
            title = data.get('title', 'untitled').replace(" ", "_")
            output_dir = Path(f"output/{title}")
            output_dir.mkdir(parents=True, exist_ok=True)

            # Process each voiceover in the array
            for idx, text in enumerate(data['voiceover']):
                if voiceover_count >= 3:
                    print("Pausing for 60 seconds after 3 voiceovers...")
                    time.sleep(60)
                    voiceover_count = 0

                # Prepare request payload
                payload = {
                    "model": "tts-hd",
                    "input": text,
                    "voice": "echo"
                }

                # Generate output filename
                output_file = output_dir / f"voiceover_{idx + 1}.mp3"

                print(f"Generating voiceover {idx + 1} for {title}")

                # Make API request
                response = requests.post(API_URL, headers=headers, params=params, json=payload)
                
                if response.status_code == 200:
                    # Save the audio file
                    with open(output_file, 'wb') as f:
                        f.write(response.content)
                    print(f"Successfully generated {output_file}")
                    voiceover_count += 1
                else:
                    print(f"Error generating voiceover {idx + 1}: {response.status_code}")
                    print(response.text)
                    continue

            # Move processed file to done directory
            shutil.move(file_path, os.path.join(done_dir, filename))
            print(f"Moved {filename} to done directory")

        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
            continue

if __name__ == "__main__":
    TODO_DIR = "todo"
    DONE_DIR = "done"
    
    print("Starting voiceover generation process...")
    process_voiceovers(TODO_DIR, DONE_DIR)
    print("Process completed!")