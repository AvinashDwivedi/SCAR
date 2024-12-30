from flask import Flask, render_template, request, jsonify
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

if __name__ == "__main__":
    app.run(debug=True)