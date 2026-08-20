# Technical Report - Quiz Master

Author: Harsh
Type: Server-rendered web application
Stack: Flask, Jinja2, SQLAlchemy, SQLite, Matplotlib, Flask-RESTful

## 1. Problem statement

Build a quiz platform where an administrator organizes study material into a structured hierarchy and creates multiple-choice quizzes, while students take those quizzes and track their performance. The system needs a clean content model, straightforward CRUD for the admin, reliable scoring, and simple analytics for both roles.

## 2. Approach and architecture

The application is a classic server-rendered Flask app rather than a single-page application. Every page is produced on the server with Jinja2 templates, which keeps the stack small and the request flow easy to follow: a browser request hits a route in `controllers.py`, the route queries the database through SQLAlchemy, and it returns a rendered template.

The main components are:
- `app.py`, which constructs the Flask application, configures SQLite, initializes the database and the REST API, pushes an application context so the app is reachable globally, and creates all tables on startup.
- `backend/models.py`, which defines the data model.
- `backend/controllers.py`, which contains all the page routes and business logic.
- `backend/api_controllers.py`, which adds a small REST API for subjects using Flask-RESTful.

## 3. Data model and design decisions

The schema mirrors how study material is actually structured: a subject contains chapters, a chapter contains quizzes, and a quiz contains questions. Scores link a user to a quiz.

Design decisions worth calling out:
- Cascade deletes are set on every parent-to-child relationship, so deleting a subject cleanly removes its chapters, their quizzes, and the associated questions and scores. This avoids orphaned rows without manual cleanup.
- Questions store four options and a `correct_option` field. Scoring then reduces to comparing each submitted answer against that field, which keeps the grading logic trivial and deterministic.
- Users are keyed by name and separated from admins in their own table, which makes the login branch simple: check the submitted credentials against both tables and route to the matching dashboard.

## 4. Core flows

**Authentication.** The login route looks up the submitted name and password in the `User` and `Admin` tables and redirects to the appropriate dashboard. Registration creates a new `User` row after checking that the name is not already taken.

**Content management.** The admin dashboard exposes create, edit, and delete routes for subjects, chapters, quizzes, and questions. Quizzes are created against a chapter with a deadline, and questions are created against a quiz.

**Quiz taking and scoring.** When a student submits a quiz, the route iterates over the quiz's questions, reads the selected option for each from the form, and increments the score by one for every match with the stored correct option. The resulting `Score` row records the quiz, the user, and the total.

**Analytics.** Two summary views are generated on demand with Matplotlib using the non-interactive Agg backend so the code runs on a headless server. The admin summary plots the number of quizzes per subject. The student summary plots best scores per chapter for the logged-in user. Each chart is saved as an image that the template then displays.

## 5. Search

A single search box on each dashboard performs case-insensitive matching. The admin search spans users, subjects, chapters, and quizzes; the student search spans subjects, chapters, and quizzes. Matching uses SQL `ILIKE` so partial queries work as expected.

## 6. REST API

Alongside the server-rendered pages, the app exposes a Flask-RESTful resource for subjects supporting list, create, update, and delete. This demonstrates serving both HTML and JSON from the same application and keeps a clean path for a future API-driven client.

## 7. Challenges and solutions

| Challenge | Solution |
|-----------|----------|
| Keeping the content hierarchy consistent on delete | Cascade delete rules on every relationship |
| Rendering charts on a server without a display | Matplotlib Agg backend, saving images to `static/` |
| Deterministic, simple grading | Store the correct option per question and count matches on submit |
| Serving both pages and structured data | Server-rendered Jinja2 routes plus a Flask-RESTful API |

## 8. Known limitations

This is an early project and some parts are intentionally simple. Passwords are stored in plain text and user identity is carried in the URL rather than in a server session. Forms lack server-side validation and CSRF protection, and quiz deadlines are stored but not strictly enforced. These are the first things I would address in a follow-up, along with hashed passwords, session-based authentication, pagination, and automated tests.

## 9. Results

A complete two-role quiz platform: administrators build and manage the full subject-to-question hierarchy and see quiz distribution at a glance, while students take quizzes, get graded instantly, review answers, and track their best scores per chapter over time.
