# Quiz Master

A multi-user quiz and exam-preparation web application. An administrator organizes content into a subject, chapter, quiz, and question hierarchy, and students take timed multiple-choice quizzes and track their performance over time.

This is a server-rendered Flask application: the backend builds HTML pages with Jinja2 templates, stores data in SQLite through SQLAlchemy, and renders performance charts with Matplotlib. It also exposes a small REST API for subject data.

The application code lives in the `quiz_master_21f3001662/` directory. A copy of the original project report is included there as `Project Report Quiz Master - V1.pdf`.

## Roles

The application has two roles, each with its own dashboard and workflow.

**Administrator**
- Create, edit, and delete subjects, chapters, quizzes, and questions.
- Quizzes belong to a chapter and carry a deadline. Questions are multiple choice with four options and one correct answer.
- Search across users, subjects, chapters, and quizzes.
- View a summary chart of the number of quizzes per subject.
- View the list of registered users.

**Student**
- Browse subjects, drill into chapters, and see the quizzes available in each.
- Take a quiz: answer the multiple-choice questions and get scored automatically.
- Review the correct answers after submitting.
- See a score dashboard of past attempts and a personal performance chart of best scores per chapter.

## Data model

The schema is a straightforward content hierarchy plus scoring.

| Entity | Key fields | Relationships |
|--------|-----------|---------------|
| User | name (primary key), password, full_name, qualification | Score (one-to-many) |
| Admin | name (primary key), password | — |
| Subject | s_id, sname, s_description | Chapter (one-to-many, cascade) |
| Chapter | c_id, cname, c_description, s_id | Quiz (one-to-many, cascade) |
| Quiz | q_id, c_id, q_deadline | Question, Score (one-to-many, cascade) |
| Question | ques_id, q_id, question_statement, option1-4, correct_option | belongs to Quiz |
| Score | score_id, q_id, u_id, total_score | belongs to User and Quiz |

Cascade deletes keep the hierarchy consistent: removing a subject removes its chapters, their quizzes, and all related questions and scores.

## How it works

- `app.py` builds the Flask app, configures SQLite, initializes the database and the REST API, and creates the tables on startup.
- `backend/models.py` defines the SQLAlchemy models.
- `backend/controllers.py` holds the page routes: authentication, the admin and student dashboards, all create/edit/delete flows, quiz taking and scoring, search, and the two summary charts.
- `backend/api_controllers.py` exposes a Flask-RESTful endpoint for subjects (list, create, update, delete).
- Quizzes are scored by comparing each submitted option against the stored correct option and counting the matches.
- Summary charts are generated with Matplotlib (using the non-interactive Agg backend) and saved as images that the templates display: quizzes per subject for the admin, and best score per chapter for each student.

## Tech stack

| Layer | Technologies |
|-------|-------------|
| Backend | Python, Flask, Flask-RESTful, Flask-SQLAlchemy |
| Templating | Jinja2, HTML, CSS (Bootstrap-based layout) |
| Database | SQLite via SQLAlchemy ORM |
| Charts | Matplotlib |

## Getting started

### Prerequisites
- Python 3.10 or newer

### Run
```bash
cd quiz_master_21f3001662

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install flask flask-restful flask-sqlalchemy matplotlib

python app.py                   # runs on http://localhost:5000
```
The database and tables are created automatically on first run.

## REST API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/subjects` | List all subjects |
| POST | `/api/subject` | Create a subject |
| PUT | `/api/edit_subject/<s_id>` | Update a subject |
| DELETE | `/api/delete_subject/<s_id>` | Delete a subject |

## Project structure
```
quiz_master_21f3001662/
├── app.py                     # App setup, config, DB init, API registration
├── backend/
│   ├── models.py              # SQLAlchemy models
│   ├── controllers.py         # Page routes: auth, dashboards, CRUD, quiz taking, charts
│   └── api_controllers.py     # REST API for subjects
├── templates/                 # Jinja2 templates for admin and student views
├── static/
│   ├── styles/                # CSS
│   └── images/                # Generated summary charts
└── Project Report Quiz Master - V1.pdf
```

## What this project covers
- Modeling a real content hierarchy with SQLAlchemy relationships and cascade deletes.
- Building a full server-rendered CRUD application with Flask and Jinja2.
- Implementing quiz-taking logic and automatic scoring.
- Generating server-side charts from live data with Matplotlib.
- Adding a REST API alongside a server-rendered app.

## Known limitations and what I would improve
This was an early project, and a few things are deliberately simple. If I were extending it:
- Hash passwords instead of storing them in plain text, and add proper session-based login rather than passing the user name in the URL.
- Add server-side validation and CSRF protection on forms.
- Enforce quiz deadlines and prevent re-attempts where appropriate.
- Add pagination and automated tests.

This is a personal academic project (Modern Application Development I).
