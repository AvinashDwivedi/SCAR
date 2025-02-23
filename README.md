# SCAR - Smart Course Assistant and Recommender

## Overview
SCAR (Smart Course Assistant and Recommender) is a backend system designed to assist students and educators in managing and interacting with course content. It provides functionalities such as topic explanations, quizzes, and PowerPoint presentations generation based on course materials. The system uses OpenAI's GPT models to generate explanations and quizzes, and it manages user sessions and conversation history using SQLite.

## Features
- **Topic Explanations**: Generate simple explanations for course topics using OpenAI's GPT models.
- **Quizzes**: Create and submit quizzes based on course content.
- **PowerPoint Generation**: Generate visually appealing PowerPoint presentations from course content.
- **Session Management**: Manage user sessions and conversation history.
- **Caching**: Cache topic explanations to reduce redundant API calls.

## Project Structure
```
SCAR/
│
├── app.py                        # Main Flask application file
├── course/                       # Directory containing course materials
│   ├── syllabus.json            # JSON file containing course syllabus
│   └── lecture_notes/           # Directory containing lecture notes
│       ├── week1/               # Lecture notes for Week 1
│       │   └── day1.txt         # Lecture notes for Day 1 of Week 1
│       └── week2/               # Lecture notes for Week 2
│           └── day1.txt         # Lecture notes for Day 1 of Week 2
├── generated_ppt/               # Directory to store generated PowerPoint presentations
├── templates/                   # Flask templates directory
│   ├── index.html               # Home page template
│   └── quiz.html                # Quiz page template
├── chatbot_cache.db             # SQLite database for caching and session management
├── .env                         # Environment variables file (e.g., OpenAI API key)
├── requirements.txt             # Python dependencies
└── README.md                    # Project documentation
```

## Installation
1. **Clone the repository**:
   ```bash
   git clone https://github.com/AvinashDwivedi/SCAR.git
   cd SCAR
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file in the root directory and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

## API Endpoints
- **GET `/`**: Home page.
- **GET `/get_courses`**: Get available courses.
- **POST `/get_weeks`**: Get weeks for a selected course.
- **POST `/get_days`**: Get days for a selected week.
- **POST `/get_topics`**: Get topics for a selected day.
- **POST `/teach_topic`**: Get an explanation for a selected topic.
- **POST `/chat`**: Chat with the assistant about a topic.
- **GET `/quiz`**: Quiz page.
- **POST `/start_quiz`**: Start a quiz for a selected topic.
- **POST `/submit_quiz`**: Submit quiz responses and get feedback.
- **POST `/generate_presentation`**: Generate a PowerPoint presentation.
- **GET `/download_ppt`**: Download the generated PowerPoint presentation.

## Usage
1. **Access the home page**:
   Open your browser and navigate to `http://localhost:5000/`.

2. **Select a course, week, day, and topic**:
   Use the provided endpoints to navigate through the course structure.

3. **Get topic explanations**:
   Use the `/teach_topic` endpoint to get explanations for selected topics.

4. **Take quizzes**:
   Use the `/start_quiz` and `/submit_quiz` endpoints to take and submit quizzes.

5. **Generate PowerPoint presentations**:
   Use the `/generate_presentation` endpoint to generate presentations and download them via `/download_ppt`.

## Dependencies
- Flask
- Flask-CORS
- OpenAI
- python-dotenv
- python-pptx
- SQLite3

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🙌 Acknowledgments
- Thanks to all contributors and testers.
- Special appreciation to libraries and tools like Bootstrap, Axios, and Marked.js.

---

## 📬 Contact
For questions or support, reach out via email: [avinashdubeyg2001@gmail.com].

> *Built with ❤️ to make learning smarter and more accessible.*