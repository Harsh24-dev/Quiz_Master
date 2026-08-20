#app route
from flask import Flask, render_template,request, session,url_for,redirect
from .models import *
from flask import current_app as app
from datetime import datetime, timezone
import matplotlib
matplotlib.use("Agg") 
import matplotlib.pyplot as plt

#login/Signup route

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods = ["GET","POST"])
def signin():
    if request.method == "POST":
        name = request.form.get("name")
        pwd = request.form.get("password")

        usr = User.query.filter_by(name=name,password=pwd).first()
        admin = Admin.query.filter_by(name=name,password=pwd).first()

        if usr:
            return redirect(url_for("student_dashboard",name=name))
        elif admin:
            return redirect(url_for("admin_dashboard",name=name)) 
        else:
            return render_template("login.html",msg="Invalid user credentials, try again.")
    
    return render_template("login.html")

@app.route("/register",methods = ["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name")
        pwd = request.form.get("password") 
        full_name = request.form.get("full_name")
        edu = request.form.get("qualification")
        usr = User.query.filter_by(name=name).first()
        
        if usr:
            return render_template("signup.html",msg="Sorry, this mail already registered!!!")
        
        new_usr = User(name=name,password=pwd,full_name=full_name,qualification = edu)
        db.session.add(new_usr)
        db.session.commit()
        return render_template("login.html",msg="Registration successfull, try login now")
    return render_template("signup.html")

# Admin route

@app.route("/admin/<name>")
def admin_dashboard(name):
    subjects = get_subjects()
    chapters = get_chapters()
    return render_template("admin_dashboard.html",name = name, subjects = subjects, chapters = chapters)

@app.route("/quiz/<name>")
def quiz_dashboard(name):
    chapters = get_chapters()
    quizzes = get_quizzes()
    return render_template("quiz_dashboard.html",name = name, chapters = chapters, quizzes = quizzes)

@app.route("/admin/search/<name>", methods=["GET", "POST"])
def admin_search(name):

    if request.method == "POST":
        query = request.form.get("search_txt", "").strip()
        users = User.query.filter(User.name.ilike(f"%{query}%")).all()
        subjects = Subject.query.filter(Subject.sname.ilike(f"%{query}%")).distinct().all()
        chapters = Chapter.query.filter(Chapter.cname.ilike(f"%{query}%")).all()
        quizzes = Quiz.query.filter(Quiz.q_id.ilike(f"%{query}%")).all()

        return render_template('admin_dashboard.html', name=name, query=query, users=users, subjects=subjects, chapters = chapters, quizzes=quizzes)

    return redirect(url_for('admin_dashboard', name=name))

@app.route("/admin/summary/<name>")
def summary(name):
    plot=get_subjects_summary()
    plot.savefig("./static/images/subject_summary.jpeg", format="jpeg", dpi=100, bbox_inches="tight")
    plot.close()
    return render_template("admin_summary.html",name = name)

def get_subjects_summary():
    subjects=get_subjects()
    subject_names = [sub.sname for sub in subjects]
    quiz_counts = [sum(len(chap.quizzes) for chap in sub.chapters) for sub in subjects]
    plt.bar(subject_names,quiz_counts,color="skyblue", width=0.2)
    plt.title("Quizzes per Subject")
    plt.xlabel("Subjects")
    plt.ylabel("Number of Quizzes")
    return plt

@app.route('/subject/<name>',methods = ["POST","GET"])
def add_subject(name):
    if request.method == "POST":
        sname = request.form.get("sname")
        s_description = request.form.get("s_description")
        
        new_sub = Subject(sname = sname, s_description = s_description)
        db.session.add(new_sub)
        db.session.commit()
        return redirect(url_for("admin_dashboard",name = name))
    
    return render_template("add_subject.html", name = name)

@app.route('/chapter/<s_id>/<name>',methods = ["POST","GET"])
def add_chapter(s_id,name):
    if request.method == "POST":
        cname = request.form.get("cname")
        c_description = request.form.get("c_description")
        
        new_chap = Chapter(cname = cname, c_description = c_description, s_id = s_id)
        db.session.add(new_chap)
        db.session.commit()
        return redirect(url_for("admin_dashboard",name = name))
    
    return render_template("add_chapter.html", s_id = s_id, name = name)

@app.route('/add_quiz/<c_id>/<name>',methods = ["POST","GET"])
def add_quiz(c_id,name):
    if request.method == "POST":
        q_deadline = request.form.get("q_deadline")
        q_deadline=datetime.strptime(q_deadline,"%Y-%m-%dT%H:%M")
        new_quiz = Quiz( q_deadline = q_deadline, c_id = c_id)
        db.session.add(new_quiz)
        db.session.commit()
        return redirect(url_for("quiz_dashboard",name = name))
    
    return render_template("add_quiz.html", c_id = c_id, name = name)

@app.route('/add_question/<q_id>/<name>',methods = ["POST","GET"])
def add_question(q_id,name):
    if request.method == "POST":
        question_statement = request.form.get("question_statement")
        option1 = request.form.get("option1")
        option2 = request.form.get("option2")
        option3 = request.form.get("option3")
        option4 = request.form.get("option4")
        correct_option = request.form.get("correct_option")
        
        new_ques = Question( question_statement = question_statement, option1 = option1, option2 = option2, option3 = option3, option4 = option4, correct_option = correct_option, q_id = q_id)
        db.session.add(new_ques)
        db.session.commit()
        return redirect(url_for("view_quiz", q_id = q_id, name = name))
    
    return render_template("add_question.html", q_id = q_id, name = name)

@app.route('/edit_quiz/<q_id>/<name>',methods = ["POST","GET"])
def edit_quiz(q_id,name):
    q = get_quiz(q_id)
    if request.method == "POST":
        q_deadline= request.form.get("q_deadline")
        q_deadline=datetime.strptime(q_deadline,"%Y-%m-%dT%H:%M")
        q.q_deadline = q_deadline
        db.session.commit()
        return redirect(url_for("quiz_dashboard",name = name))
    return render_template("edit_quiz.html", quiz = q, name = name)

@app.route('/edit_chapter/<c_id>/<name>',methods = ["POST","GET"])
def edit_chapter(c_id,name):
    c = get_chapter(c_id)
    if request.method == "POST":
        cname = request.form.get("cname")
        c_description = request.form.get("c_description")
        c.cname = cname
        c.c_description = c_description
        db.session.commit()
        return redirect(url_for("admin_dashboard",name = name))
    return render_template("edit_chapter.html", chapter = c, name = name)

@app.route('/edit_subject/<s_id>/<name>',methods = ["POST","GET"])
def edit_subject(s_id,name):
    s = get_subject(s_id)
    if request.method == "POST":
        sname = request.form.get("sname")
        s_description = request.form.get("s_description")
        s.sname = sname
        s.s_description = s_description
        db.session.commit()
        return redirect(url_for("admin_dashboard",name = name))
    return render_template("edit_subject.html", subject = s, name = name)

@app.route("/delete_subject/<s_id>/<name>",methods=["GET","POST"])
def delete_subject(s_id,name):
    s=get_subject(s_id) 
    db.session.delete(s)
    db.session.commit()
    return redirect(url_for("admin_dashboard",name=name))

@app.route("/delete_chapter/<c_id>/<name>",methods=["GET","POST"])
def delete_chapter(c_id,name):
    c=get_chapter(c_id) 
    db.session.delete(c)
    db.session.commit()
    return redirect(url_for("admin_dashboard",name=name))

@app.route("/delete_quiz/<q_id>/<name>",methods=["GET","POST"])
def delete_quiz(q_id,name):
    q=get_quiz(q_id) 
    db.session.delete(q)
    db.session.commit()
    return redirect(url_for("quiz_dashboard",name=name))

@app.route("/view_quiz/<q_id>/<name>",methods=["GET","POST"])
def view_quiz(q_id, name):
    q=get_quiz(q_id)
    return render_template("view_quiz.html",q_id = q_id, name = name, quiz = q)

@app.route('/edit_question/<ques_id>/<name>', methods=["GET", "POST"])
def edit_question(ques_id, name):
    question = Question.query.get(ques_id)
    quiz = Quiz.query.get(question.q_id)

    if request.method == "POST":
        question.question_statement = request.form.get("question_statement")
        question.option1 = request.form.get("option1")
        question.option2 = request.form.get("option2")
        question.option3 = request.form.get("option3")
        question.option4 = request.form.get("option4")
        question.correct_option = request.form.get("correct_option")

        db.session.commit()
        return redirect(url_for("view_quiz", q_id = quiz.q_id, name=name))

    return render_template("edit_question.html", question = question, quiz = quiz, name=name)

@app.route('/delete_question/<q_id>/<ques_id>/<name>', methods=["GET", "POST"])
def delete_question(ques_id, q_id, name):
    question = Question.query.filter_by(ques_id=ques_id).first()

    if question:
        db.session.delete(question)
        db.session.commit()

    return redirect(url_for("view_quiz", q_id = q_id, name=name))

@app.route("/user_list/<name>")
def user_list(name):
    users = User.query.all()
    return render_template("user_list.html",name = name,users = users)

#User Route
@app.route("/user/<name>")
def student_dashboard(name):
    quizzes = get_quizzes()
    chapters = get_chapters()
    subjects = Subject.query.options(db.joinedload(Subject.chapters).joinedload(Chapter.quizzes)).all()
    dt_time_now = datetime.today().strftime('%Y-%m-%dT%H:%M')
    dt_time_now = datetime.strptime(dt_time_now,"%Y-%m-%dT%H:%M")
    return render_template("student_dashboard.html",name = name, quizzes = quizzes, chapters = chapters, subjects = subjects, dt_time_now = dt_time_now)

@app.route("/user/summary/<name>")
def user_summary(name):
    plot = get_user_summary(name)
    plot.savefig("./static/images/user_performance.jpeg", format="jpeg", dpi=100, bbox_inches="tight")
    plot.close()
    
    return render_template("user_summary.html", name=name)

def get_user_summary(name):
    user = User.query.filter_by(name=name).first()
    
    quiz_attempts = (db.session.query(Quiz.q_id, Score.total_score).join(Score, Quiz.q_id == Score.q_id).filter(Score.u_id == user.name).all())

    if not quiz_attempts:
        return plt

    quiz_ids = [quiz[0] for quiz in quiz_attempts]
    scores = [quiz[1] for quiz in quiz_attempts]

    quiz_labels = []
    for q_id in quiz_ids:
        quiz = Quiz.query.filter_by(q_id=q_id).first()
        if quiz:
            chapter = Chapter.query.filter_by(c_id=quiz.c_id).first()
            if chapter:
                quiz_labels.append(chapter.cname)
            else:
                quiz_labels.append(f"Quiz {q_id}")
        else:
            quiz_labels.append(f"Quiz {q_id}")

    plt.figure(figsize=(8, 5))
    plt.bar(quiz_labels, scores, color="lightcoral", width=0.4)
    plt.title(f"Quiz Performance - {name}")
    plt.xlabel("Chapters")
    plt.ylabel("best Scores")
    plt.ylim(0, 10)
    plt.xticks(rotation=45, ha="right")

    return plt

@app.route("/user/search/<name>", methods=["GET", "POST"])
def user_search(name):

    if request.method == "POST":
        query = request.form.get("search_txt", "").strip()
        subjects = Subject.query.filter(Subject.sname.ilike(f"%{query}%")).distinct().all()
        chapters = Chapter.query.filter(Chapter.cname.ilike(f"%{query}%")).all()
        quizzes = Quiz.query.filter(Quiz.q_id.ilike(f"%{query}%")).all()
        dt_time_now = datetime.today().strftime('%Y-%m-%dT%H:%M')
        dt_time_now = datetime.strptime(dt_time_now,"%Y-%m-%dT%H:%M")

        return render_template('student_dashboard.html', name=name, query=query, subjects=subjects, chapters = chapters, quizzes=quizzes,dt_time_now=dt_time_now)

    return redirect(url_for('student_dashboard', name=name))

@app.route('/take_quiz/<q_id>/<name>',methods = ["POST","GET"])
def take_quiz(q_id,name):
    quiz = Quiz.query.filter_by(q_id=q_id).first()
    if request.method == "POST":
        total_score = 0
        for question in quiz.questions:
            selected_option = request.form.get(f"question_{question.ques_id}")
            if selected_option == question.correct_option:
                total_score += 1

        new_score = Score(q_id=q_id, u_id=name, total_score=total_score)
        db.session.add(new_score)
        db.session.commit()
        return redirect(url_for("quiz_answer", q_id=q_id, name=name))
    
    return render_template("take_quiz.html",q_id=q_id,quiz=quiz,name=name,sname=quiz.chapter.subject.sname,cname=quiz.chapter.cname)

@app.route("/quiz_answer/<q_id>/<name>",methods=["GET","POST"])
def quiz_answer(q_id, name):
    q=get_quiz(q_id)
    return render_template("quiz_answer.html",q_id = q_id, name = name, quiz = q)

@app.route('/score_dashboard/<name>')
def score_dashboard(name):
    user = User.query.filter_by(name=name).first()
    scores = Score.query.filter_by(u_id = user.name).all()
    quizzes = get_quizzes()

    return render_template("score_dashboard.html", name=name, scores=scores, quizzes=quizzes)


# Other Route

def get_quiz(id):
    quiz = Quiz.query.filter_by(q_id = id).first()
    return quiz

def get_chapter(id):
    chapter = Chapter.query.filter_by(c_id = id).first()
    return chapter

def get_subject(id):
    subject = Subject.query.filter_by(s_id = id).first()
    return subject

def get_quizzes():
    quizzes = Quiz.query.all()
    return quizzes

def get_chapters():
    chapters = Chapter.query.all()
    return chapters

def get_scores():
    scores = Score.query.all()
    return scores

def get_subjects():
    subjects = Subject.query.all()
    return subjects

def get_questions():
    questions = Question.query.all()
    return questions



# to edit
