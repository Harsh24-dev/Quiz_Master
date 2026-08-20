from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"
    name = db.Column(db.String,  primary_key=True, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    full_name = db.Column(db.String, nullable=False)
    qualification = db.Column(db.String, nullable=False)
    scores = db.relationship("Score",cascade="all,delete",backref="user",lazy=True)

class Admin(db.Model):
    __tablename__ = "admin"
    name = db.Column(db.String, primary_key = True, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

class Subject(db.Model):
    __tablename__ = "subject"
    s_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sname = db.Column(db.String, unique=True, nullable=False)
    s_description = db.Column(db.String, nullable=False)
    chapters = db.relationship("Chapter", cascade="all,delete", backref="subject", lazy=True)

class Chapter(db.Model):
    __tablename__ = "chapter"
    c_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cname = db.Column(db.String, unique=True, nullable=False)
    c_description = db.Column(db.String, nullable=False)
    s_id = db.Column(db.Integer, db.ForeignKey("subject.s_id"), nullable=False)
    quizzes = db.relationship("Quiz", cascade="all,delete", backref="chapter", lazy=True)

class Quiz(db.Model):
    __tablename__ = "quiz"
    q_id = db.Column(db.Integer, primary_key=True,  autoincrement=True)
    c_id = db.Column(db.Integer, db.ForeignKey("chapter.c_id"), nullable=False)
    q_deadline = db.Column(db.DateTime,  nullable=False)
    questions = db.relationship("Question", cascade="all,delete", backref="quiz", lazy=True)
    scores = db.relationship("Score", cascade="all,delete", backref="quiz", lazy=True)


class Question(db.Model):
    __tablename__ = "question"
    ques_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    q_id = db.Column(db.Integer, db.ForeignKey('quiz.q_id'), nullable=False)
    question_statement = db.Column(db.String, nullable=False)
    option1 = db.Column(db.String, nullable=False)
    option2 = db.Column(db.String, nullable=False)
    option3 = db.Column(db.String, nullable=False)
    option4 = db.Column(db.String, nullable=False)
    correct_option = db.Column(db.String, nullable=False)

class Score(db.Model):
    __tablename__ = "score"
    score_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    q_id = db.Column(db.Integer, db.ForeignKey('quiz.q_id'), nullable=False)
    u_id = db.Column(db.String, db.ForeignKey('user.name'), nullable=False)
    total_score = db.Column(db.Float, nullable=False)