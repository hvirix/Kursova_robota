from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length
from dotenv import load_dotenv
import os
load_dotenv()

import pymysql
pymysql.install_as_MySQLdb()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Виключаємо зайву вартість відстеження змін
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')


db = SQLAlchemy(app)


# Модель для студентів
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    course = db.Column(db.Integer, nullable=False)
    faculty = db.Column(db.String(50), nullable=False)
    floor = db.Column(db.Integer, nullable=False)
    room_number = db.Column(db.Integer, nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)


# Модель для новин
class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    
class Requests(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    group = db.Column(db.String(100), nullable=False)
    faculty = db.Column(db.String(100), nullable=False)
    course = db.Column(db.Integer, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)


# Форма для пошуку студента
class SearchForm(FlaskForm):
    query = StringField('Пошук студента за ПІБ', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Знайти')

# Форма для запитань
class QuestionForm(FlaskForm):
    name = StringField('Ваше ім’я', validators=[DataRequired(), Length(max=100)])
    email = StringField('Ваш Email', validators=[DataRequired(), Length(max=100)])
    message = TextAreaField('Ваше запитання', validators=[DataRequired()])
    submit = SubmitField('Надіслати')


@app.route('/')
def index():
    # Отримуємо новини з бази даних
    news = News.query.all()
    return render_template('index.html', news=news)


@app.route('/students', methods=['GET', 'POST'])
def students():
    search_form = SearchForm()
    students = []
    if search_form.validate_on_submit() and search_form.query.data:
        query = search_form.query.data.strip()
        print(query)
        students = Student.query.filter(Student.full_name.like(f"%{query}%")).all()
        print(students)
    return render_template('students.html', search_form=search_form, students=students)

@app.route('/news/<int:news_id>')
def news_detail(news_id):
    # Отримуємо новину за ID
    news_item = News.query.get_or_404(news_id)
    return render_template('news_detail.html', news_item=news_item)

@app.route('/questions', methods=['GET', 'POST'])
def questions():
    question_form = QuestionForm()

    if question_form.validate_on_submit():
        new_question = Question(
            name=question_form.name.data,
            email=question_form.email.data,
            message=question_form.message.data
        )
        db.session.add(new_question)
        db.session.commit()
        flash('Ваше запитання успішно надіслано!', 'success')
        return redirect(url_for('questions'))

    return render_template('questions.html', question_form=question_form)

@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        # Отримуємо дані з форми
        name = request.form['name']
        group = request.form['group']
        faculty = request.form['faculty']
        course = request.form['course']
        phone = request.form['phone']
        email = request.form['email']
        print(f"name = {name}, group = {group}, faculty = {faculty}, course = {course}, phone = {phone}, email = {email}")

        # Перевірка на наявність усіх полів
        if not all([name, group, faculty, course, phone, email]):
            return jsonify({"error": "Всі поля повинні бути заповнені!"}), 400

        # Створення нового запису в базі даних
        new_request = Requests(name=name, group=group, faculty=faculty,
                               course=course, phone=phone, email=email)

        # Додавання до БД
        db.session.add(new_request)
        db.session.commit()

        return jsonify({"success": "Реєстрація успішна!"}), 200  # Успішна реєстрація

    return render_template('registration.html')  # Повертаємо HTML форму для реєстрації


@app.route('/management')
def management():
    return render_template('management.html')

@app.route('/chat')
def chat():
    return redirect('https://t.me/your_dormitory_chat')  # Посилання на чат (Telegram, наприклад)

# Створення бази даних (якщо її ще не існує)
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)