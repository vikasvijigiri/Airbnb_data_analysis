from datetime import datetime
import json, bson
import streamlit as st


# Convert some columns that are not JSON serializable
def json_encoder(obj):
    try:
        if isinstance(obj, datetime):
            # Convert datetime to ISO 8601 format
            return obj.isoformat()
        elif isinstance(obj, bson.decimal128.Decimal128):
            # Convert Decimal128 to float or str
            return str(obj)
    except Exception as e:
        st.error(e) 

# collect from MongoDb and then export
#@st.cache_data
def export_data(data):
    try:
        # Specify the file name
        file_name = "airbnb_mongodb_data.json"
        
        # Open the file for writing
        with open(file_name, "w") as file:
            # Dump the dictionary to the file in JSON format using the custom encoder
            json.dump(data, file, default=json_encoder)
    except Exception as e:
        st.error(e)    

# Imported already stored data. For fast processing and mongoDb connection time and again
#@st.cache_data
def import_data():
    try:
        # Specify the file name
        file_name = "airbnb_mongodb_data.json"
        
        # Open the file for reading
        with open(file_name, "r") as file:
            # Read JSON data from the file into a dictionary
            data_dict = json.load(file)
        return data_dict    
    except Exception as e:
        st.error(e)  
        return None




