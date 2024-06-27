import streamlit as st
import pickle
import joblib
import pandas as pd
import numpy as np
import requests
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics.pairwise import cosine_similarity


new_df = joblib.load('new_df.pkl')
course_df =pd.DataFrame(new_df)
course_pop_df = joblib.load('course_pop_df.pkl')
similarity_course = joblib.load('similarity_course.pkl')

def recommend(course):
    if course in course_df['Title'].values:
        index = course_df[course_df['Title'] == course].index[0]
        similar_items = sorted(list(enumerate(similarity_course[index])), key=lambda x: x[1], reverse=True)[0:5]

        data = []
        for i in similar_items:
            item = []
            temp_df = course_df[course_df['Title'] == course_df['Title'].iloc[i[0]]]
            item.append(temp_df['Title'].iloc[0])
            item.append(temp_df['URL'].iloc[0])
            data.append(item)
        return data
    else:
        return 'Course not found'


st.title('_Top Courses Recommendations_')

selected_course_name = st.selectbox(
    'How would you like to be contacted?',
    course_df['Title'].values)

if st.button('Recommend'):
    recommendations = recommend(selected_course_name)

    if recommendations == 'Course not found':
        st.error("Course not found in the database.")
    else:
        st.write("## Similar Courses:")
        for recommendation in recommendations:
            st.write(f"**{recommendation[0]}**")
            st.write(f"  {recommendation[1]}")
            st.write("---")

