import os
import streamlit as st
import pandas as pd
from data_exp_imp_module import *
from EDA_module import *

def open_header():
    # Page header
    st.markdown("<h1 style='text-align:center; font-size:48px; color: red;'>Data Preprocessing</h1>", unsafe_allow_html=True)    
    st.markdown("---")  # Horizontal line for separation

def page_options():
    # Create tabs for Data Extract and Preprocess
    tabs = st.tabs(["Data Extract", "Preprocess"])

    with tabs[0]:
        st.header("Retrieving data from MongoDB Atlas")
        st.write("In this section, you can retrieve data from MongoDB Atlas or a local JSON file.")
        data = mongodb_data()  # Retrieve data
        
        # Display the retrieved data (optional)
        #st.success("Data successfully retrieved from MongoDB Atlas or local file")
        #st.dataframe(data)
        st.session_state['data'] = data  # Store data in session state

    with tabs[1]:
        st.header("Steps of Preprocessing")
        st.write("In this section, you can preprocess the data for analysis. The preprocessing includes:")
        st.write("- Filling missing values using mean or mode based on data type.")
        st.write("- Creating new features from existing data to enhance EDA.")
        st.write("- Adjusting data types for columns.")
        st.write("Click the button below to preprocess the data:")
        
        data = st.session_state.get('data', None)  # Retrieve data from session state
        if data is not None:
            df = preprocessing_data(data)
            st.warning("large data! Cant show data here")  
            #st.dataframe(df.head(3))
            if 'clean_df' not in st.session_state:
                st.session_state['clean_df'] = None
            st.session_state['clean_df'] = df  # Store clean data in session state
            
            # Display the preprocessed data (optional)



#@st.cache_data
def mongodb_data():
    # Retrieve data from MongoDB or local JSON file
    if os.path.exists('airbnb_mongodb_data.json'):
        data = import_data()
        st.success("Successfully imported data from airbnb_mongodb_data.json!") 
    else:
        client = connect_to_mongo_db()
        data = data_base_collectoions(client)
        export_data(data)
        st.success("Successfully imported data from MongoDB database!")
    return data


#@st.cache_data
def preprocessing_data(data):
    # Preprocess data logic
    df = convert_data_pandas(data)
    clean_data(df)
    label_encoding(df)
    return df

def main():
    #open_header()
    page_options()

if __name__ == "__main__":
    main()
