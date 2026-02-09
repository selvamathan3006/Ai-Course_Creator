# video_finder.py
import os
import json
import re
import google.genai as genai
from google.genai import types
from gtts import gTTS  # For audio generation

# --- AI Configuration ---
MODEL_NAME = 'gemini-2.5-flash'
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

# --- Helper: Map full language names to gTTS codes ---
LANG_MAP = {
    "English": "en",
    "Tamil": "ta",
    "Hindi": "hi",
    "Malayalam": "ml",
    "Kannadam": "kn",
    "Telungu": "te",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Japanese": "ja",
    "Korean": "ko"
}

# --- Generate video script via Gemini AI ---
def _generate_video_script(lesson_title, course_title, language):
    prompt = f"""
    You are a scriptwriter specializing in short educational video content.
    The lesson topic is: "{lesson_title}" (part of the course: "{course_title}").
    Generate a concise, 60-second video script in {language} focusing on the main definition and 2-3 core concepts.
    STRICTLY return JSON in this format:
    {{
        "title": "<script title>",
        "script": [
            {{
                "time": "00:00-00:20",
                "audio_narration": "Text for audio",
                "visuals": "Description of visuals"
            }},
            ...
        ]
    }}
    """
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Error generating video script for '{lesson_title}': {e}")
        return None

# --- Generate audio from text ---
def _generate_audio(text, lesson_title, language="English", output_dir="downloads"):
    os.makedirs(output_dir, exist_ok=True)
    lang_code = LANG_MAP.get(language, "en")
    safe_title = re.sub(r'[^a-zA-Z0-9_-]', '_', lesson_title)
    filepath = os.path.join(output_dir, f"{safe_title}.mp3")

    if not text.strip():
        print(f"No text to generate audio for '{lesson_title}'")
        return None

    try:
        tts = gTTS(text=text, lang=lang_code)
        tts.save(filepath)
        print(f"Audio generated: {filepath}")
        return filepath
    except Exception as e:
        print(f"Error generating audio for '{lesson_title}': {e}")
        return None

# --- Main function: Generate scripts + audio for all lessons ---
def find_youtube_videos(scaffold, language="English"):
    course_title = scaffold.get("course_title", "")
    videos_data = []

    for module in scaffold.get("modules", []):
        for lesson in module.get("lessons", []):
            lesson_title = lesson if isinstance(lesson, str) else lesson.get("lesson_title", "Lesson")
            print(f"Generating script for: {lesson_title}...")

            script_data = _generate_video_script(lesson_title, course_title, language)
            lesson_videos = []

            if script_data:
                # Generate audio for each segment
                for segment in script_data.get("script", []):
                    segment_title = f"{lesson_title}_{segment.get('time','')}"
                    audio_file = _generate_audio(segment.get("audio_narration",""), segment_title, language)
                    segment["audio_file"] = audio_file

                # Generate full lesson audio (concatenate segments)
                full_text = " ".join([s.get("audio_narration","") for s in script_data.get("script",[])])
                full_audio_file = _generate_audio(full_text, lesson_title, language)

                lesson_videos.append({
                    "title": script_data.get("title", lesson_title),
                    "script_content": script_data.get("script"),
                    "duration": "PT1M0S",
                    "type": "AI-Generated Script",
                    "audio_file": full_audio_file
                })
            else:
                lesson_videos.append({
                    "title": f"Failed to generate script for {lesson_title}",
                    "script_content": [],
                    "duration": "N/A",
                    "type": "Failed",
                    "audio_file": None
                })

            videos_data.append({
                "lesson_title": lesson_title,
                "video_links": lesson_videos
            })

    return {
        "videos": videos_data,
        "course_title": course_title
    }
