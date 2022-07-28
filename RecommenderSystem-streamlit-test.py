#!/usr/bin/env python
# coding: utf-8

import numpy as np 
import pandas as pd 
import plotly.express as px

#basic libraries
import streamlit as st
pd.options.mode.chained_assignment = None
from PIL import Image

# text processing libraries
#import re
#import string
#import nltk
#from nltk.corpus import stopwords

# sklearn 
from sklearn import model_selection
from sklearn.feature_extraction.text import CountVectorizer,TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn import preprocessing, decomposition, model_selection, metrics, pipeline
from sklearn.model_selection import GridSearchCV,StratifiedKFold,RandomizedSearchCV
from sklearn.metrics.pairwise import cosine_similarity

# matplotlib and seaborn for plotting
import matplotlib.pyplot as plt
import seaborn as sns

# Suppress warnings 
import warnings
warnings.filterwarnings('ignore')


#########################
#Page Configuration
########################

st.set_page_config(page_title="Unesco World Heritage Sites", layout='wide')


##############################
# Image
##############################

image = Image.open('world.jpg')
st.image(image, caption='Image by Juliana Kozoski')


#############################
# Introduction
#############################
                   
st.title("UNESCO World Heritage Sites")
"""
A World Heritage Site is a landmark or area with legal protection by an international convention administered by the United Nations Educational, Scientific and Cultural Organization (UNESCO). World Heritage Sites are designated by UNESCO for having cultural, historical, scientific or other form of significance. The sites are judged to contain "cultural and natural heritage around the world considered to be of outstanding value to humanity".
"""

############################
# Load the dataset
############################


# # Load dataset

data = pd.read_csv("whc-sites_recommender.csv", keep_default_na=False, )


############################
# Recommendation System
############################


# # Transforming tokens to a vector: TFIDF

tfidf = TfidfVectorizer(max_features=1500, min_df=2,
                       max_df=0.75, ngram_range=(1, 2))

sparse_matrix = tfidf.fit_transform(data['short_description_en_clean'])



# # Recommender system based on KNN

from sklearn.neighbors import NearestNeighbors
kNN = NearestNeighbors(n_neighbors=10,  metric='cosine')
kNN.fit(sparse_matrix)


def recommended_WHS_new(data, WHS_id, sparse_matrix, k,
                        metric='cosine'):
    
    neighbour_ids = []
    
    name_WHS = data.loc[WHS_id, 'short_description_en_clean']
    WHS_to_assess = sparse_matrix[WHS_id]
    
    # use KNN to find the WHS the are closed to the choosed:    
    kNN = NearestNeighbors(n_neighbors=k, 
                           metric=metric)
    kNN.fit(sparse_matrix)

    neighbour = kNN.kneighbors(WHS_to_assess, return_distance=False)
    
    # map each neighbour id with the right WHS_id:
    for i in range(1,k):
        n = neighbour.item(i) 
        neighbour_ids.append(n)   
    
    #get the name of the recommended whs:
    WHS_titles = dict(zip(data.index, data['name_en']))
    WHS_title = WHS_titles[WHS_id]
    
    #append the titles into a list:
    neighbours_title = []
    for i in neighbour_ids:
        neighbours_title.append(WHS_titles[i])
        
    return neighbours_title


def top_recommend(data,WHS_id,k):
    
    """  
    
    What the fuction is doing:
    
    Run the function to get the top recomendations, add to the title of the games
    other information, such as genre, saved in the first data frame, then concat
    the informations of the 'target' game.
    
    Parameters:
    
    game_id:the steam_appid of the game you're looking
    k:the number of recommendations show
    df:the name of the data frame
    
    Returns:
    
    the top recommendations
    
    """
    
    #select the name of top recommendations:
    top_recommendations = recommended_WHS_new(data, WHS_id, sparse_matrix, k, metric='cosine')
    
    #get the genre informations from the top_recommendations saved on the general dataset:
    top_recommendations = data[data.name_en.isin(top_recommendations)]
    top_recommendations = top_recommendations.drop(['short_description_en','short_description_en_clean'],axis=1)
    
    #add to this results the game we want to compare:
    #top_recommendations = pd.concat([(df[df.steam_appid == game_id]), top_recommendations])
    
    return top_recommendations


########

st.header("**What're the recommended WHS?**")

WHS_list = data['name_en'].unique().tolist().sort_values('name_en',ascending=True)
WHS_name = st.selectbox('', WHS_list)
data_ = data.reset_index()
selected_id = int(data_.loc[data_['name_en']  == WHS_name, 'index'])
print(selected_id)

recommendations = top_recommend(data,selected_id,k=10)
#genre_recommendations = print_description(steam_recommend, recommendations,tfidf).sort_values('Game Rating',ascending=False)
st.table(recommendations)
