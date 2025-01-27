import os
import uuid
from pptx import Presentation
from pptx.util import Pt, Inches
import textwrap
from flask import Flask, render_template, request, jsonify, send_file
import json
from flask_cors import CORS
from openai import OpenAI

app = Flask(__name__)
CORS(app)  # Enables CORS for all routes by default

# Initialize OpenAI client
client = OpenAI(api_key="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")

# Helper function to interact with GPT
def chat_with_gpt(prompt, type=None):
    try:
        if type:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                response_format={"type": "json_object"},
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content
        else:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"
    
def save_string_to_file(text, filename="output.txt"):
    """
    Save a string to a text file.
    
    Parameters:
    - text (str): The string to save.
    - filename (str): The name of the file (default: "output.txt").
    
    Returns:
    - str: Confirmation message with the file path.
    """
    try:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(text)
        return f"String saved to {filename}"
    except Exception as e:
        return f"An error occurred: {e}"


# Load syllabus
def load_syllabus():
    with open("course/syllabus.json", "r") as file:
        return json.load(file)

def get_available_courses(syllabus):
    return list(syllabus.keys())

syllabus_json = load_syllabus()

@app.route('/')
def home():
    return render_template("index.html")  # Ensure the frontend HTML file is named "index.html"

@app.route('/get_courses', methods=['GET'])
def get_courses():
    courses = get_available_courses(syllabus_json)
    return jsonify(courses=courses)

@app.route('/get_weeks', methods=['POST'])
def get_weeks():
    course = request.json.get("course")
    if course in syllabus_json:  # Check if the course exists in the syllabus JSON
        weeks = list(syllabus_json[course].keys())
        return jsonify(weeks=weeks)
    return jsonify(error="Invalid course selected."), 400

@app.route('/get_days', methods=['POST'])
def get_days():
    course = request.json.get("course")
    week = request.json.get("week")

    if not course or course not in syllabus_json:
        return jsonify(error="Invalid or missing course."), 400

    if not week or week not in syllabus_json[course]:
        return jsonify(error="Invalid or missing week."), 400

    days = list(syllabus_json[course][week].keys())
    return jsonify(days=days)

@app.route('/get_topics', methods=['POST'])
def get_topics():
    course = request.json.get("course")
    week = request.json.get("week")
    day = request.json.get("day")

    if not course or course not in syllabus_json:
        return jsonify(error="Invalid or missing course."), 400

    if not week or week not in syllabus_json[course]:
        return jsonify(error="Invalid or missing week."), 400

    if not day or day not in syllabus_json[course][week]:
        return jsonify(error="Invalid or missing day."), 400

    topics = syllabus_json[course][week][day].get("Topics", [])
    return jsonify(topics=topics)

@app.route('/teach_topic', methods=['POST'])
def teach_topic():
    course = request.json.get("course")
    week = request.json.get("week")
    day = request.json.get("day")
    topic = request.json.get("topic")

    topic_content = open(f"course/lecture_notes/{week}/{day}.txt", 'r', encoding='utf-8').read()

    prompt = f"By going through '''{topic_content}'''. Explain the '{topic}' in simple terms suitable for a beginner."
    explanation = chat_with_gpt(prompt)
    print(save_string_to_file(explanation, "example_output.txt"))
    return jsonify(explanation=explanation)

@app.route('/chat', methods=['POST'])
def chat():
    message = request.json.get("message")
    course = request.json.get("course")
    week = request.json.get("week")
    day = request.json.get("day")
    topic = request.json.get("topic")

    if not message:
        return jsonify(error="Message is required."), 400

    topic_content = open(f"course/lecture_notes/{week}/{day}.txt", 'r', encoding='utf-8').read()
    prompt = f"By going through '''{topic_content}'''. Clear the students doubt only if it's related to it else tell them to ask relevant questions. The doubt is: {message}"
    reply = chat_with_gpt(prompt)
    return jsonify(reply=reply)

@app.route('/quiz')
def quiz_page():
    return render_template('quiz.html')  # Ensure 'quiz.html' is in the templates folder

@app.route('/start_quiz', methods=['POST'])
def start_quiz():
    course = request.json.get("course")
    week = request.json.get("week")
    day = request.json.get("day")
    topic = request.json.get("topic")

    if not course or not week or not day or not topic:
        return jsonify(error="All selections (course, week, day, topic) are required to start the quiz."), 400

    topic_content = open(f"course/lecture_notes/{week}/{day}.txt", 'r', encoding='utf-8').read()

    prompt = f'''
    Create a short quiz with 3 multiple-choice questions and their answers
    on the topic "{topic_content}". Present the quiz in JSON format as given here:
    {json.load(open("quiz_template.json"))}
    '''
    quiz_content = chat_with_gpt(prompt, type="json_object")
    try:
        quiz_data = json.loads(quiz_content)
    except json.JSONDecodeError:
        return jsonify(error="Failed to generate valid quiz data."), 500

    return jsonify(quiz=quiz_data)


@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    responses = request.json.get("responses")
    quiz = request.json.get("quiz")

    if not responses or not quiz:
        return jsonify(error="Responses and quiz data are required."), 400

    score = 0
    total = len(quiz['questions'])
    feedback = []

    for i, response in enumerate(responses):
        correct_option_id = quiz['questions'][i]["correct_option_id"]
        if response == correct_option_id:
            score += 1
            feedback.append({"question": quiz['questions'][i]["question"], "correct": True})
        else:
            correct_answer_text = next(option["text"] for option in quiz['questions'][i]["options"] if option["id"] == correct_option_id)
            feedback.append({
                "question": quiz['questions'][i]["question"],
                "correct": False,
                "correct_answer": correct_answer_text
            })

    return jsonify(score=score, total=total, feedback=feedback)

# PowerPoint Generation Function
def create_visually_appealing_presentation(topic, slides_data, filename, max_chars_per_slide=1000):
    """
    Generate a visually appealing PowerPoint presentation with markdown content, 
    handling long text by splitting it across multiple slides and ensuring proper layout.
    """
    def add_content_slide(prs, title, content, layout):
        """
        Helper function to add a content slide to the presentation.
        Dynamically adjusts content to fit the slide.
        """
        slide = prs.slides.add_slide(layout)
        slide.shapes.title.text = title

        content_placeholder = slide.placeholders[1]

        # Dynamically adjust font size to fit the content
        font_size = 18  # Start with a standard font size
        max_lines = 12  # Max lines to fit in the placeholder
        content_lines = content.split("\n")

        # If content exceeds max lines, reduce font size iteratively
        while len(content_lines) > max_lines and font_size > 10:
            font_size -= 1
            max_lines += 2  # Slightly increase lines allowed as font size decreases

        # Add content to placeholder with adjusted font size
        text_frame = content_placeholder.text_frame
        text_frame.clear()  # Clear default content
        for line in content_lines:
            p = text_frame.add_paragraph()
            p.text = line
            p.font.size = Pt(font_size)
            p.line_spacing = Pt(font_size + 6)  # Line spacing based on font size

    # Initialize the presentation
    prs = Presentation()
    title_slide_layout = prs.slide_layouts[0]
    content_slide_layout = prs.slide_layouts[1]

    # Add title slide
    title_slide = prs.slides.add_slide(title_slide_layout)
    title_slide.shapes.title.text = topic
    subtitle = title_slide.placeholders[1]
    subtitle.text = f"An in-depth presentation on {topic}"

    # Customize title slide fonts
    title_slide.shapes.title.text_frame.paragraphs[0].font.size = Pt(36)
    subtitle.text_frame.paragraphs[0].font.size = Pt(20)
    subtitle.text_frame.paragraphs[0].font.italic = True

    # Add content slides
    for slide_data in slides_data:
        title = slide_data["title"]
        content = slide_data["content"]

        # Split content into chunks based on max_chars_per_slide
        content_chunks = textwrap.wrap(content, max_chars_per_slide, break_long_words=False, replace_whitespace=False)

        for i, chunk in enumerate(content_chunks):
            slide_title = title if i == 0 else f"{title} (Cont.)"
            add_content_slide(prs, slide_title, chunk, content_slide_layout)

    # Save the presentation
    try:
        prs.save(filename)
    except Exception as e:
        raise IOError(f"Failed to save the presentation: {e}")


@app.route('/generate_presentation', methods=['POST'])
def generate_presentation():
    data = request.json
    informational_text = data.get("informational_text")
    topic = data.get("topic", "Presentation")

    if not informational_text or len(informational_text.strip()) < 10:
        return jsonify(error="Informational text is required and must be meaningful."), 400

    try:
        # Generate slide titles
        titles_prompt = f"Don't add preamble and Based on the following informational text, generate list of slide titles for a presentation separated by '\\n':\n\n{informational_text}"
        titles_response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": titles_prompt}]
        )
        titles_content = titles_response.choices[0].message.content if titles_response.choices and titles_response.choices[0].message.content else None

        if not titles_content:
            return jsonify(error="Failed to generate slide titles. OpenAI response was empty or invalid."), 500

        slide_titles = [line.strip() for line in titles_content.split("\n") if line.strip()]

        if not slide_titles:
            return jsonify(error="No slide titles generated. Please review the informational text."), 400

        # Generate slide content
        slides_data = []
        for title in slide_titles:
            content_prompt = f"Don't add preamble. Generate short content for the presentation slide titled '{title}' based on the following text:\n\n{informational_text}"
            content_response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": content_prompt}]
            )
            content = content_response.choices[0].message.content if content_response.choices and content_response.choices[0].message.content else None

            if not content:
                return jsonify(error=f"Content for slide '{title}' is empty or invalid."), 500

            slides_data.append({
                "title": title,
                "content": content.strip()
            })

        # Generate the presentation
        output_dir = "generated_ppt"
        os.makedirs(output_dir, exist_ok=True)
        unique_id = uuid.uuid4().hex
        ppt_filename = os.path.join(output_dir, f"presentation_{unique_id}.pptx")
        create_visually_appealing_presentation(topic, slides_data, ppt_filename)

        return jsonify(message="Presentation generated successfully!", download_url=f"/download_ppt?filename=presentation_{unique_id}.pptx")
    except Exception as e:
        return jsonify(error=f"Failed to generate presentation: {str(e)}"), 500


@app.route('/download_ppt', methods=['GET'])
def download_ppt():
    """
    Download the generated PowerPoint presentation.
    """
    filename = request.args.get("filename")
    if not filename:
        return jsonify(error="Filename is required."), 400

    filepath = os.path.join("generated_ppt", filename)
    if not os.path.exists(filepath):
        return jsonify(error="File not found."), 404

    return send_file(filepath, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)