import os
import google.genai as genai
from google.genai import types
import json
import time
import re
from dotenv import load_dotenv


load_dotenv() 

# --- JSON Schema Definitions (Fixed) ---

CourseScaffoldSchema = {
    "type": "object",
    "properties": {
        "course_title": {"type": "string"},
        "modules": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "module_title": {"type": "string"},
                    "lessons": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "A list of 5 specific lesson titles for this module."
                    }
                },
                "required": ["module_title", "lessons"]
            }
        }
    },
    "required": ["course_title", "modules"]
}

LessonContentSchema = {
    "type": "object",
    "properties": {
        "content": {
            "type": "string",
            "description": "The full detailed educational content for the lesson, formatted as a long string."
        }
    },
    "required": ["content"]
}

QuizQuestionSchema = {
    "type": "object",
    "properties": {
        "question": {"type": "string"},
        "options": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 4,
            "maxItems": 4,
            "description": "Exactly 4 multiple-choice options."
        },
        "correct_answer": {
            "type": "string",
            "description": "The exact text of the correct option."
        }
    },
    "required": ["question", "options", "correct_answer"]
}

QuizSchema = {
    "type": "object",
    "properties": {
        "quiz": {
            "type": "array",
            "items": QuizQuestionSchema,
            "minItems": 20,
            "maxItems": 20,
            "description": "An array of 20 multiple-choice quiz questions."
        }
    },
    "required": ["quiz"]
}


MODEL_NAME = 'gemini-2.5-flash' 

# --- SAFE CLIENT CONFIGURATION ---
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("API Key not found. Please set the GEMINI_API_KEY or GOOGLE_API_KEY environment variable.")

# CRITICAL FIX: Initialize client to None globally. It will be set inside the function.
client = None 
# ---------------------------------


def get_gemini_response(prompt, schema: types.Schema = None):
    # CRITICAL: Initialize client only on the first call to the function.
    global client
    if client is None:
        try:
            client = genai.Client(api_key=api_key)
        except Exception as e:
            print(f"Gemini client initialization failed: {e}")
            return None
        
    config = {}
    
    if schema:
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=schema,
            temperature=0.2
        )
    
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=config
        )

        if not response.text:
            raise ValueError("The response from the API was empty or blocked.")

        if schema:
            return json.loads(response.text) 
        
        return response.text

    except Exception as e:
        print(f"Gemini API call failed: {e}")
        return None


def generate_course_scaffold(topic, language, detailed_scaffold: bool = False):
    
    detailed_instruction = ""
    if detailed_scaffold:
        detailed_instruction = (
            "The lessons for EACH of the 5 modules must be structured to systematically cover "
            "the following learning phases for that module's topic: basics/definition, core concepts/architecture, "
            "and implementation/execution. Aim for a balanced distribution of these concepts across the lessons."
        )
    
    prompt = f"""
    You are an expert curriculum designer. Your task is to create a course syllabus.
    Design a syllabus for a course on the topic: "{topic}".
    The syllabus must have exactly 5 modules, each with exactly 5 lessons.
    CRITICAL: Ensure each lesson title is prefixed with its module and lesson number, 
    e.g., "1.1: What is the topic", "1.2: Another topic", "2.1: New module topic".
    {detailed_instruction}
    The language for all content must be {language}.
    STRICTLY adhere to the required JSON schema for the entire response.
    """
    
    MAX_ATTEMPTS = 3
    scaffold_response = None
    
    for attempt in range(MAX_ATTEMPTS):
        scaffold_response = get_gemini_response(prompt, schema=CourseScaffoldSchema)

        if scaffold_response and isinstance(scaffold_response, dict) and scaffold_response.get('modules'):
            print(f"Scaffold successfully generated on attempt {attempt + 1}.")
            return scaffold_response
        

        print(f"Scaffold generation failed (attempt {attempt + 1}). Retrying in 5 seconds...")
        time.sleep(5)
        
    return None 

def generate_full_course_content(scaffold, language, microlessons_mode: bool = False):
    full_course_content = scaffold.copy()
    
    content_length_instruction = (
        "The content should be comprehensive, clear, and engaging. "
        "Include an introduction, core concepts with examples, and a concluding summary. "
    )
    if microlessons_mode:
        content_length_instruction = (
            "The content must be very brief and concise, structured as 3-5 short, separate paragraphs, "
            "suitable for a microlesson format. Use simple, direct language."
        )

    for module in full_course_content.get('modules', []):
        detailed_lessons = []
        MAX_ATTEMPTS = 3 

        for lesson_title in module.get('lessons', []): 
            print(f"Generating content for lesson: {lesson_title}...")
            
            prompt = f"""
            You are an expert educator and content writer.
            Write the detailed educational content for a lesson titled "{lesson_title}" as part of a larger course on "{scaffold.get('course_title', 'The Course')}".
            {content_length_instruction}
            The language for the content must be {language}.
            STRICTLY follow the required JSON schema for your response.
            """
            
            content_response = None
            
            for attempt in range(MAX_ATTEMPTS):
                content_response = get_gemini_response(prompt, schema=LessonContentSchema)
                
                if content_response and "content" in content_response:
                    break
                
                print(f"Attempt {attempt + 1} failed for '{lesson_title}'. Retrying in 5 seconds...")
                time.sleep(5) 

            if content_response and "content" in content_response:
                detailed_lessons.append({
                    "lesson_title": lesson_title,
                    "content": content_response["content"]
                })
                time.sleep(2) 
            else:
                 detailed_lessons.append({
                    "lesson_title": lesson_title,
                    "content": f"Content generation failed after {MAX_ATTEMPTS} attempts."
                })
                
        module['lessons'] = detailed_lessons
    
    if not full_course_content.get('modules'):
        return None 
        
    return full_course_content


def generate_quiz(full_content, language):
    all_text_content = "\n\n".join(
        lesson['content'] for module in full_content.get('modules', []) for lesson in module.get('lessons', [])
    )

    max_length = 15000
    if len(all_text_content) > max_length:
        all_text_content = all_text_content[:max_length]

    prompt = f"""
    You are a quiz master. Based on the following course material, create a comprehensive multiple-choice quiz with 20 questions.
    Each question should have 4 options and a single correct answer.
    The language for the quiz must be {language}.
    STRICTLY adhere to the required JSON schema for the entire response.

    Course Material:
    ---
    {all_text_content}
    ---
    """
    return get_gemini_response(prompt, schema=QuizSchema)