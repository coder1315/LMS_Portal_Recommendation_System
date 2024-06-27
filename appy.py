import streamlit as st
import pickle
import joblib
import pandas as pd
import numpy as np
import requests
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics.pairwise import cosine_similarity


def fetch_poster_from_pickle(book_name, books):
    try:

        poster_url = books.loc[books['Book-Title'] == book_name, 'Image-URL-M'].values[0]
        return poster_url
    except IndexError:
        return None


def recommend_collab(book_name):
    if book_name in pivots.index:
        index = np.where(pivots.index == book_name)[0][0]
        similar_items = sorted(list(enumerate(similarity_collab[index])), key=lambda x: x[1], reverse=True)[1:11]

        data = []
        for i in similar_items:
            item = {}
            temp_df = books[books['Book-Title'] == pivots.index[i[0]]]
            item['Book-Title'] = list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values)[0]
            item['Book-Author'] = list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values)[0]
            item['Image-URL-M'] = list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values)[0]

            data.append(item)
        return data

    else:
        return False


def recommend_content(book_title):

    book_index = content_dataset[content_dataset['Book-Title'].str.lower() == book_title.lower()].index[0]
    book_cluster = recommendation_cont_dataset.iloc[book_index]['Clusters']
    cluster_books = recommendation_cont_dataset[recommendation_cont_dataset['Clusters'] == book_cluster]
    similarity_scores = cosine_similarity(recommendation_cont_dataset.iloc[book_index].values.reshape(1, -1),
                                          cluster_books.iloc[:, :])
    top_indices = similarity_scores.argsort()[0][-10:][::-1]
    recommended_books = cluster_books.iloc[top_indices]

    recommendations = []
    for index in top_indices:
        book_data = content_dataset.iloc[index]
        recommendation = {
            "Book-Title": book_data["Book-Title"],
            "Book-Author": book_data["Book-Author"],
            "Image-URL-M": book_data["Image-URL-M"]
        }
        recommendations.append(recommendation)

    return recommendations


def recommend_knn_content(book_title):

    book_index = content_dataset[content_dataset['Book-Title'].str.lower() == book_title.lower()].index[0]
    book_cluster = recommendation_cont_dataset.iloc[book_index]['Clusters']
    knn_dataset = recommendation_cont_dataset[recommendation_cont_dataset['Clusters'] == book_cluster].reset_index()
    knn = NearestNeighbors()
    knn.fit(knn_dataset.iloc[:, 1:-1])
    neighbors = knn.kneighbors(pd.DataFrame(recommendation_cont_dataset.iloc[book_index, :-1]).T, 10, return_distance=False)[0]

    recommendations = []
    for neighbor in neighbors:
        neighbor_index = neighbor
        book_data = content_dataset.iloc[neighbor_index]
        recommendation = {
            "Book-Title": book_data["Book-Title"],
            "Book-Author": book_data["Book-Author"],
            "Image-URL-M": book_data["Image-URL-M"]
        }
        recommendations.append(recommendation)

    return recommendations


def ensemble_hybrid_recommend(book_title):
    collab_recs = recommend_collab(book_title)
    content_recs = recommend_content(book_title)
    knn_content_recs = recommend_knn_content(book_title)

    combined_recs = []
    for recs in [collab_recs, content_recs, knn_content_recs]:
        if recs:
            for rec in recs:
                combined_recs.append(rec)

    for rec in combined_recs:
        if 'count' in rec:
            rec['count'] += 1
        else:
            rec['count'] = 1

    sorted_recs = sorted(combined_recs, key=lambda item: item['count'], reverse=True)

    book_info = books[books['Book-Title'].str.lower() == book_title.lower()].drop_duplicates('Book-Title')
    if not book_info.empty:
        book_data = {
            'Book-Title': book_info['Book-Title'].iloc[0],
            'Book-Author': book_info['Book-Author'].iloc[0],
            'Image-URL-M': book_info['Image-URL-M'].iloc[0]
        }
        sorted_recs.insert(0, book_data)

    for i in range(len(sorted_recs)):
        if 'count' in sorted_recs[i]:
            del sorted_recs[i]['count']

    return sorted_recs[:10]


def get_top_books_by_country(content_demo_dataset, country):

    country_data = content_demo_dataset[content_demo_dataset['Country'].str.lower() == country.lower()]
    sorted_data = country_data.sort_values(by=['Book-Rating'], ascending=False)
    top_books = sorted_data.head(20)
    book_list = []
    for index, row in top_books.iterrows():
        book_dict = {
          'Book-Title': row['Book-Title'],
          'Book-Author': row['Book-Author'],
          'Image-URL-M': row['Image-URL-M'],
          'Age': row['Age']
        }
        book_list.append(book_dict)
    return book_list


book_dict = joblib.load('final_rating.pkl')
content_demo_dataset = joblib.load('content_demo_dataset.pkl')
books = pd.DataFrame(book_dict)
content_dataset =joblib.load('content_book.pkl')
recommendation_cont_dataset = joblib.load('recommendation_cont_book.pkl')
similarity_collab= joblib.load('similarity_score.pkl')
pivots = joblib.load('pivots.pkl')


st.title('_Top Books Recommendations_')

selected_book_name = st.selectbox(
    'How would you like to be contacted?',
    books['Book-Title'].values)

if st.button('Recommend'):
    recommendations = ensemble_hybrid_recommend(selected_book_name)

    col1, col2, col3, col4, col5 = st.columns(5)

    for i, recommendation in enumerate(recommendations):
        if i < 5:
            # Access the appropriate column using the index 'i'
            with col1 if i == 0 else col2 if i == 1 else col3 if i == 2 else col4 if i == 3 else col5:
                st.text(recommendation['Book-Title'])
                st.image(recommendation['Image-URL-M'], caption=recommendation['Book-Title'])

st.title("Top Books by Country")


available_countries = content_demo_dataset['Country'].unique()

selected_country = st.selectbox(
    "Select a Country:",
    available_countries
)

if st.button("Get Recommendations"):
    if selected_country:
        recommendations = get_top_books_by_country(content_demo_dataset, selected_country)

        st.write(f"## Top 20 Books in {selected_country}:")
        for book in recommendations:
            col1, col2 = st.columns([1, 3])
            with col1:
                st.image(book['Image-URL-M'], width=100)
            with col2:
                st.write(f"**{book['Book-Title']}**")
                st.write(f"By: {book['Book-Author']}")

    else:
        st.warning("Please select a country.")