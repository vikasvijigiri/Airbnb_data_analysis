from pymongo.mongo_client import MongoClient
import pandas as pd
import datetime
import numpy as np
import json, bson
from sklearn.preprocessing import LabelEncoder
import streamlit as st






# If the connection doesnt work now, then only problem is not giving proper access to this ip address
#@st.cache_data
def connect_to_mongo_db():
    try:
        # Replace the placeholder with your Atlas connection string
        uri = "mongodb+srv://vikki4me:Vikas@cluster0.vn9ijam.mongodb.net/"
        
        # Create a new client and connect to the server
        client = MongoClient(uri)
        
        # Send a ping to confirm a successful connection        
        client.admin.command('ping')
        st.success("Pinged your deployment. You successfully connected to MongoDB!")
        return client
    except Exception as e:
        st.error(f"Error in connecting to mongoDB: {e}")
        return None

#@st.cache_data       
def data_base_collectoions(client):
    try:
        db = client.get_database('sample_airbnb')
        collection_list = db.list_collection_names()       
        return list(db.get_collection(collection_list[0]).find())        
    except Exception as e:
        st.error(f"Error in data base collection: {e}")
        return None  

#@st.cache_data
def key_and_type(data_one):
    try:
        key_type = []
        for key, value in data_one.items():
            key_type.append(type(value))    
        return pd.DataFrame({'key': list(data_one.keys()), 'type': key_type})
    except Exception as e:
        st.error(f"Error in key and type to pandas: {e}")
        return None

#@st.cache_data
def convert_data_pandas(data):
    try:
        data_accumulated = []
        # Define allowed types
        allowed_types = (str, int, datetime.datetime, bson.decimal128.Decimal128)
        
        # # Iterate over each dictionary in data
        # for d in data:
        #     # Filter keys and values by allowed types
        #     column_types = {key: value for key, value in d.items() if isinstance(value, allowed_types)}
            
        #     data_accumulated.append(column_types)
        
        # return pd.DataFrame(data_accumulated)
        #st.success("Successfully Converted data into pandas dataframe!")          
        return pd.json_normalize(data)
    except Exception as e:
        st.error(f"Error in converting data to pandas: {e}")
        return None            

#@st.cache_data
def clean_data(df):
    try:
        df['maximum_nights'] = df['maximum_nights'].astype(int)
        df['minimum_nights'] = df['minimum_nights'].astype(int)
        df['bathrooms'] = df['bathrooms'].astype(str)
        df['bathrooms'] = df['bathrooms'].astype(float)
        df['security_deposit'] = df['security_deposit'].astype(str)
        df['security_deposit'] = df['security_deposit'].astype(float)
        df['price'] = df['price'].astype(str)
        df['price'] = df['price'].astype(float)

        df['cleaning_fee'] = df['cleaning_fee'].astype(str)
        df['cleaning_fee'] = df['cleaning_fee'].astype(float)
        
        df['first_review'] = pd.to_datetime(df['first_review'], errors='coerce')
        df['last_review'] = pd.to_datetime(df['last_review'], errors='coerce')

        
        df['extra_people'] = df['extra_people'].astype(str)
        df['extra_people'] = df['extra_people'].astype(float)
        df['extra_people'] = df['extra_people'].astype(int)
        df['guests_included'] = df['guests_included'].astype(str)
        df['guests_included'] = df['guests_included'].astype(float)
        df['guests_included'] = df['guests_included'].astype(int)
        df['reviews_per_month'] = df['reviews_per_month'].astype(str)
        df['reviews_per_month'] = df['reviews_per_month'].astype(float)
        df['monthly_price'] = df['monthly_price'].astype(str)
        df['monthly_price'] = df['monthly_price'].astype(float)
        df['weekly_price'] = df['weekly_price'].astype(str)
        df['weekly_price'] = df['weekly_price'].astype(float)        

        ######################################################################################################
        df['maximum_nights'] = df['maximum_nights'].where(df['maximum_nights'] <= df['maximum_nights'].quantile(0.99), df['maximum_nights'].value_counts().idxmax())        
        df['bathrooms'] = df['bathrooms'].fillna(df['bathrooms'].value_counts().idxmax())
        df['beds'] = df['beds'].fillna(df['beds'].value_counts().idxmax())
        df['bedrooms']= df['bedrooms'].fillna(df['bedrooms'].value_counts().idxmax())
        df['security_deposit'] = df['security_deposit'].fillna(int(df['security_deposit'].mean()))
        df['cleaning_fee'] = df['cleaning_fee'].fillna(df['cleaning_fee'].mean())
        df['reviews_per_month'] = df['reviews_per_month'].fillna(int(df['reviews_per_month'].mean()))
        df['monthly_price'] = df['monthly_price'].fillna(int(df['monthly_price'].mean()))
        df['weekly_price'] = df['weekly_price'].fillna(int(df['weekly_price'].mean()))        

        df['first_review'] = df['first_review'].interpolate(method='linear')
        df['last_review'] = df['last_review'].interpolate(method='linear')
                

        df['host.host_response_rate'] = df['host.host_response_rate'].fillna(df['host.host_response_rate'].mean())
        df['host.host_response_time'] = df['host.host_response_time'].fillna(df['host.host_response_time'].value_counts().idxmax())

        # df['review_scores.review_scores_accuracy'] = df['review_scores.review_scores_accuracy'].fillna(df['review_scores.review_scores_accuracy'].value_counts().idxmax())
        # df['review_scores.review_scores_cleanliness'] = df['review_scores.review_scores_cleanliness'].fillna(df['review_scores.review_scores_cleanliness'].value_counts().idxmax())
        
        # df['review_scores.review_scores_checkin'] = df['review_scores.review_scores_checkin'].fillna(df['review_scores.review_scores_checkin'].value_counts().idxmax())
        # df['review_scores.review_scores_communication'] = df['review_scores.review_scores_communication'].fillna(df['review_scores.review_scores_communication'].value_counts().idxmax())
        # df['review_scores.review_scores_value'] = df['review_scores.review_scores_value'].fillna(df['review_scores.review_scores_value'].mean())       
        
        # df['review_scores.review_scores_location'] = df['review_scores.review_scores_location'].fillna(df['review_scores.review_scores_location'].value_counts().idxmax())
        # df['review_scores.review_scores_rating'] = df['review_scores.review_scores_rating'].fillna(df['review_scores.review_scores_rating'].mean())         


        
        ##################################################################################################################################

        #return df
        st.success("Successfully cleaned and preprocessed!")      
    except Exception as e:
        st.error(f"Error in cleaning data: {e}")
        #return None 

#@st.cache_data 
def label_encoding(df):
    try:
        le = LabelEncoder()
        
        
        df['host.host_response_time_encoded'] = le.fit_transform(df['host.host_response_time'])
        df['property_type_encoded'] = le.fit_transform(df['property_type'])
        df['room_type_encoded'] = le.fit_transform(df['room_type'])
        df['bed_type_encoded'] = le.fit_transform(df['bed_type'])
        df['cancellation_policy_encoded'] = le.fit_transform(df['cancellation_policy'])
    

        # Define a dictionary mapping month numbers to seasons
        month_to_season = {
            1: 'Winter',
            2: 'Winter',
            3: 'Spring',
            4: 'Spring',
            5: 'Spring',
            6: 'Summer',
            7: 'Summer',
            8: 'Summer',
            9: 'Fall',
            10: 'Fall',
            11: 'Fall',
            12: 'Winter'
        }
        # Use the map() method to convert month numbers to seasons
        df['season'] = df['first_review'].dt.month.map(month_to_season)
        
        df['no_of_amenities'] = df['amenities'].apply(lambda x: len(x))
        df['no_of_host_verifications'] = df['host.host_verifications'].apply(lambda x: len(x))
        df['avg_review_scores'] = df.iloc[:,67:73].mean(axis=1).round(1)
        
        #df['no_of_reviews'] = df['reviews'].apply(lambda x: len(x))
        
        #return df
        st.spinner("Encoding Categorical Label")  
    except Exception as e:
        st.error(f"Error in label encoding: {e}")
        #return None 