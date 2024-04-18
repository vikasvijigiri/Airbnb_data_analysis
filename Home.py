import streamlit as st
import os
from EDA_module import *


def main_page_header():
    #st.header("How famous is the Airbnb in the world?")    
    st.markdown("<h1 style='text-align:center; font-size:48px; color: red;'>How Airbnb fares in the world</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; font-size:24px; color: blue;'>- an analytics case study </h2>", unsafe_allow_html=True)

    # Add a horizontal line or an image below the header for visual separation



def main_page_options():    
    # Create a row of tabs with navigation options
    tabs = st.tabs(["Home", "Usage", "About me"])
    st.markdown("---")  # For a horizontal line    
    # Display content in each tab
    with tabs[0]:  # Home tab
        st.header("Welcome to Home!")
        st.write("The aim of this study is to understand the data of Airbnb hotels and how to get the most of it through:")   
        st.markdown("""
            - GeoSpatial Analysis 
            - Pricing dynamics, patterns in property type, seasons, amenities, neighbourhood etc.  
            - Location based insights
            - Season wise availability and price analysis 
            """)

    

    
    with tabs[1]:  # Departments tab
        st.header("How to use this app")
        st.markdown("""
            - Fill in the details of MongoDB ATLAS server details (To establish connection to MongoDB ATLAS).
            - Import Data, here the data is imported from the MongoDB server (If not saved in the earlier runs), or locally saved one. 
            - Data Visualization, where the user is guided systematically. User needs to read the message and click appropriately.
            - Data Analysis, here also the user is guided.
            """)
    
    with tabs[2]:  # About tab
        st.header("Data is like a schrodinger cat!")
        st.write("I am a computational physicist with a PhD in physics. I have ample experience in handling large data sets throughout my research career. My love for data and contemporary challenges in the real-world has landed me here. I am a aspiring Data Scientist with expertise in mathematical and satistical modeling, with modern of the modernest techniques.")


def main():
    main_page_header()
    main_page_options()



if __name__ == "__main__":
    main()    

