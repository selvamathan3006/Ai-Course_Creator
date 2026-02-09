import os
import time
from flask import Flask, request, jsonify, render_template, send_file
from dotenv import load_dotenv
from io import BytesIO
import zipfile

from modules.ai_engine import (
    generate_course_scaffold, 
    generate_full_course_content, 
    generate_quiz
)
from modules.file_generator import create_ppt, create_pdf, create_quiz_word, create_video_scripts_docx
from modules.video_finder import find_youtube_videos

load_dotenv()

app = Flask(__name__)
app.secret_key = '2a122348937fee6343cafa5df8eaffa15c94f88b67256bfa' 


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/generate-scaffold', methods=['POST'])
def generate_scaffold_and_content():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON input"}), 400

        course_name = data.get('course_name')
        language = data.get('language')
        output_formats = data.get('output_formats', []) 
        lesson_structure_mode = data.get('lesson_structure', 'simple')
        
        if not course_name or not language or not output_formats:
            return jsonify({"error": "Missing required fields (Course Name, Language, or at least one Output Format)."}), 400

        detailed_scaffold = lesson_structure_mode == 'detailed'
        scaffold = generate_course_scaffold(course_name, language, detailed_scaffold)
        
        if not scaffold or not scaffold.get('modules'):
            return jsonify({"error": "Failed to generate course scaffold from AI or scaffold was empty."}), 500

        # Track lesson logs & time
        lesson_logs = []
        start_time = time.time()

        content_needed = any(f in output_formats for f in ['pdf', 'ppt', 'quiz', 'microlessons'])
        full_content = None

        if content_needed:
            microlessons_mode = 'microlessons' in output_formats

            # Count total lessons for ETA calculation
            total_lessons = sum(len(module.get('lessons', [])) for module in scaffold.get('modules', []))
            lessons_completed = 0

            # Call original content generation function
            full_content = generate_full_course_content(scaffold, language, microlessons_mode)

            # Log lessons and ETA if content exists
            if full_content and "modules" in full_content:
                for module in full_content.get('modules', []):
                    for lesson in module.get('lessons', []):
                        lessons_completed += 1
                        elapsed = time.time() - start_time
                        avg_time = elapsed / lessons_completed
                        remaining = int((total_lessons - lessons_completed) * avg_time)

                        log_entry = f"Generated content for lesson: {lesson.get('lesson_title','(no title)')} - ETA: {remaining}s"
                        print(log_entry)
                        lesson_logs.append(log_entry)

            if not full_content:
                return jsonify({"error": "Failed to generate full course content from AI."}), 500

        response_data = {
            "course_name": course_name,
            "language": language,
            "output_formats": output_formats,
            "full_content": full_content,
            "scaffold": scaffold,
            "hidden_logs": lesson_logs  # <-- frontend can show this in hidden logs
        }
        
        return jsonify(response_data)

    except Exception as e:
        print(f"An unexpected error occurred in generate-scaffold: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/generate-file', methods=['POST'])
def generate_file():
    try:
        data = request.get_json()
        file_type = data.get('file_type')
        course_name = data.get('course_name')
        language = data.get('language')
        full_content = data.get('full_content')
        scaffold = data.get('scaffold')

        if not file_type or not course_name:
            return jsonify({"error": "Missing file type or course name."}), 400

        if file_type == 'quiz':
            if not full_content:
                return jsonify({"error": "Missing content for quiz."}), 400
            
            # Generate quiz data from AI engine
            quiz_data = generate_quiz(full_content, language)

            # Generate Word document
            filepath = create_quiz_word(quiz_data, course_name)
            filename = os.path.basename(filepath)
            return send_file(filepath, as_attachment=True, download_name=filename)

        elif file_type == 'video':
            if not scaffold:
                return jsonify({"error": "Missing scaffold for video generation."}), 400

            video_scripts_data = find_youtube_videos(scaffold, language)
            docx_filepath = create_video_scripts_docx(video_scripts_data, course_name)

            audio_files = []
            for lesson in video_scripts_data.get("videos", []):
                for video in lesson.get("video_links", []):
                    if video.get("audio_file") and os.path.exists(video["audio_file"]):
                        audio_files.append(video["audio_file"])
                    for segment in video.get("script_content", []):
                        if segment.get("audio_file") and os.path.exists(segment["audio_file"]):
                            audio_files.append(segment["audio_file"])

            # Package DOCX + all audio files into one ZIP
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w') as zipf:
                zipf.write(docx_filepath, os.path.basename(docx_filepath))
                for f in audio_files:
                    zipf.write(f, os.path.basename(f))
            zip_buffer.seek(0)

            return send_file(
                zip_buffer,
                as_attachment=True,
                download_name=f"{course_name}_video_package.zip",
                mimetype="application/zip"
            )

        elif file_type == 'ppt':
            if not full_content: 
                return jsonify({"error": "Missing content for PPT."}), 400
            filepath = create_ppt(full_content, course_name)
            filename = os.path.basename(filepath)
            return send_file(filepath, as_attachment=True, download_name=filename)

        elif file_type == 'pdf' or file_type == 'microlessons':
            if not full_content: 
                return jsonify({"error": "Missing content for PDF."}), 400
            filepath = create_pdf(full_content, course_name)
            filename = os.path.basename(filepath)
            return send_file(filepath, as_attachment=True, download_name=filename)

        else:
            return jsonify({"error": f"Invalid file type requested: {file_type}"}), 400

    except Exception as e:
        print(f"An unexpected error occurred in generate-file: {e}")
        return jsonify({"error": str(e)}), 500

from flask import Response, stream_with_context

@app.route('/api/generate-scaffold-stream', methods=['POST'])
def generate_scaffold_stream():
    try:
        data = request.get_json()
        course_name = data.get('course_name')
        language = data.get('language')
        output_formats = data.get('output_formats', [])
        lesson_structure_mode = data.get('lesson_structure', 'simple')
        detailed_scaffold = lesson_structure_mode == 'detailed'

        scaffold = generate_course_scaffold(course_name, language, detailed_scaffold)
        total_lessons = sum(len(module.get('lessons', [])) for module in scaffold.get('modules', []))
        lessons_completed = 0

        def event_stream():
            yield f"data: Scaffold successfully generated on attempt 1.\n\n"

            for module in scaffold.get('modules', []):
                for lesson in module.get('lessons', []):
                    lesson_title = lesson.get('lesson_title', '(no title)')
                    yield f"data: Generating content for lesson: {lesson_title}...\n\n"

                    # Call AI model for lesson content
                    full_content = generate_full_course_content({'modules':[module]}, language, microlessons_mode=False)
                    time.sleep(1)  # simulate processing

                    # Simulate failures for demonstration
                    if lesson_title in ["1.1: What is Blockchain Technology?", "2.3: Introduction to Consensus Mechanisms"]:
                        yield f"data: Gemini API call failed: 503 UNAVAILABLE\n\n"
                        yield f"data: Attempt 1 failed for '{lesson_title}'. Retrying in 5 seconds...\n\n"
                        time.sleep(5)

                    lessons_completed += 1
                    remaining = int((total_lessons - lessons_completed) * 1)  # simple ETA
                    progress_percent = int((lessons_completed / total_lessons) * 100)
                    yield f"data: Completed lesson: {lesson_title} - Remaining ETA: {remaining}s\n\n"
                    yield f"data: PROGRESS:{progress_percent}\n\n"

        return Response(stream_with_context(event_stream()), mimetype='text/event-stream')

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    app.run(debug=True)
