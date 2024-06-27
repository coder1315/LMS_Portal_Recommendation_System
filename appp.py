from flask import Flask,render_template,request, session, redirect
import mysql.connector
import subprocess
import streamlit as st


app = Flask(__name__)
app.secret_key = 'ntym1234'

import pickle
import numpy as np
import joblib


popular_df = joblib.load('popular.pkl')
pt = joblib.load('pt.pkl')
similarity_scores = joblib.load('similarity_scores.pkl')
course_pop_df = joblib.load('course.pkl')


@app.route('/')
def mainpage():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/home')
def home():
        if 'user_id' in session:
            return render_template('home.html',book_name=list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_rating'].values),)
        else:
             return redirect('login.html')


@app.route('/login_validation', methods=['POST'])
def login_validation():
    email=request.form.get('email')
    password=request.form.get('password')

    cursor.execute("""SELECT * FROM `users` WHERE `email` LIKE '{}' AND `password` LIKE '{}' """
                   .format(email,password))
    users=cursor.fetchall()
    if len(users)>0:
         session['user_id']=users[0][0]
         return redirect('/home')
    else:
         return redirect('/')

@app.route('/logout')
def logout():
    session.pop('user_id')
    return redirect('/')

db_config = {
    'user': 'root',
    'password': 'nit@mysql123',
    'host': 'localhost',
    'database': 'my_database_flask'
}

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

@app.route('/add_user', methods=['POST'])
def add_user():
    name = request.form.get('aname')
    email = request.form.get('aemail')
    password = request.form.get('apassword')

    insert_query = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
    cursor.execute(insert_query, (name, email, password))
    conn.commit()

    fetch_query = "SELECT user_id FROM users WHERE email = %s"
    cursor.execute(fetch_query, (email,))
    myuser = cursor.fetchone()

    session['user_id'] = myuser[0]

    return redirect('/home')


@app.route('/recommend')
def streamlit():
    streamlit_process = subprocess.Popen(['streamlit', 'run', 'appy.py'])
    return redirect("http://localhost:8501")

@app.route('/courses')
def streamlit_one():
    streamlit_process = subprocess.Popen(['streamlit', 'run', 'appyone.py'])
    return redirect("http://localhost:8501")

if __name__ == '__main__':
    app.run(debug=True)

