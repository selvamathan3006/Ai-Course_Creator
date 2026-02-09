const form = document.getElementById('course-form');
const generateBtn = document.getElementById('generate-btn');
const loadingDiv = document.getElementById('loading');
const resultsDiv = document.getElementById('results');

const FILE_MAP = {
    'pdf': 'Course PDF Document',
    'ppt': 'PowerPoint Presentation',
    'video': 'Video Links/Scripts',
    'quiz': 'Quiz Data'
};

form.addEventListener('submit', async function(event) {
    event.preventDefault();
    resultsDiv.innerHTML = '';
    loadingDiv.classList.remove('hidden');
    generateBtn.disabled = true;
    generateBtn.textContent = 'Generating...';

    const courseName = form.elements['course_name'].value;
    const language = form.elements['language'].value;
    const lessonStructureMode = form.elements['lesson_structure_mode'].value;
    const outputFormatCheckboxes = form.querySelectorAll('input[name="output_format"]:checked');
    const outputFormats = Array.from(outputFormatCheckboxes).map(cb => cb.value);

    if (outputFormats.length === 0) {
        resultsDiv.innerHTML = '<p style="color:red;">Please select at least one output format.</p>';
        cleanupUI();
        return;
    }

    try {
        // Generate scaffold + full content
        const scaffoldResponse = await fetch('/api/generate-scaffold', {
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify({
                course_name: courseName,
                language: language,
                output_formats: outputFormats,
                lesson_structure: lessonStructureMode
            })
        });

        if (!scaffoldResponse.ok) throw new Error('Failed to generate scaffold.');
        const data = await scaffoldResponse.json();
        const persistentData = {
            course_name: data.course_name,
            language: data.language,
            full_content: data.full_content,
            scaffold: data.scaffold
        };

        // Sequentially generate files
        for (let i = 0; i < outputFormats.length; i++) {
            const fileType = outputFormats[i];
            generateBtn.textContent = `Generating ${FILE_MAP[fileType]} (${i+1}/${outputFormats.length})`;

            const fileResponse = await fetch('/api/generate-file', {
                method:'POST',
                headers:{'Content-Type':'application/json'},
                body: JSON.stringify({file_type:fileType, ...persistentData})
            });

            if (!fileResponse.ok) {
                const error = await fileResponse.json();
                resultsDiv.innerHTML += `<p style="color:red;"><strong>${FILE_MAP[fileType]}:</strong> ${error.error}</p>`;
                continue;
            }

            // Download file if applicable
            const blob = await fileResponse.blob();
            const disposition = fileResponse.headers.get('content-disposition');
            const filename = disposition ? disposition.split('filename=')[1].replace(/"/g,'') : `${fileType}_output.file`;
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);

            resultsDiv.innerHTML += `<p style="color:green;"><strong>${FILE_MAP[fileType]}:</strong> File downloaded: ${filename}</p>`;
        }

    } catch(err) {
        resultsDiv.innerHTML = `<p style="color:red;">System Error: ${err.message}</p>`;
    } finally {
        cleanupUI();
    }
});

function cleanupUI() {
    loadingDiv.classList.add('hidden');
    generateBtn.disabled = false;
    generateBtn.textContent = 'Generate Course';
}
