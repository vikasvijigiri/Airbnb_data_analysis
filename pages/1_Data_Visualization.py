import streamlit as st
import folium
from streamlit_folium import st_folium
from matplotlib import cm
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import numpy as np
import extract_data_module as ed 
import pandas as pd
import calendar



# Constants
MONTH_ORDER = [
    'January', 'February', 'March', 'April', 'May', 'June', 'July',
    'August', 'September', 'October', 'November', 'December'
]
Y_COLS = ['30 days', '60 days', '90 days', '1 year']
Y_COLS_VARS = ['availability.availability_30', 'availability.availability_60', 'availability.availability_90', 'availability.availability_365']

DEMAND_BINS = [
    0,
    13.33,
    33.33,
    50.0,
    66.66,
    83.33,
    100
]


@st.cache_data
def open_header():
    # Page header
    st.markdown("<h1 style='text-align:center; font-size:48px; color: red;'>Exploratory Data Analysis</h1>", unsafe_allow_html=True)
    st.markdown("---")
    ed.main()
  

def geo_spatial_viz():
    st.title("Search for best Airbnb hotels")


    if 'clean_df' not in st.session_state:
        st.warning("No data available. Please clear the cache or run the data processing step again.")
        return
    
    df = st.session_state['clean_df']

    # Perform calculations and filtering only once and cache the results
    # Allow user to select a country
    label = "Country"
    options = df['address.country'].unique()
    country = st.sidebar.selectbox(label, options, index=0, key='country')
    
    # Filter data based on selected country
    dg = df[df['address.country'] == country].copy()

    # Allow user to select ratings range
    ratings = st.sidebar.slider(
        "Ratings range:",
        min_value=0.0,
        max_value=10.0,
        value=(0.0, 10.0),
        step=1.0
    )
    
    # Allow user to select property type
    label = "Property Type"
    options = dg['property_type'].unique()
    property_type = st.sidebar.selectbox(label, options, index=0, key='property_type')
    
    # Allow user to select cancellation policy
    label = "Cancellation Policy"
    options = ['Moderate', 'Flexible', 'Strict (14 days grace period)', 'Super Strict (60 days)', 'Super Strict (30 days)']
    vars = ['moderate', 'flexible', 'strict_14_with_grace_period', 'super_strict_60', 'super_strict_30']
    cancel_options = dict(zip(options, vars))
    cancel_policy = st.sidebar.selectbox(label, options, index=0, key='cancellation_policy')
    cancel_var = cancel_options[cancel_policy]

    # Allow user to select price range
    min_value = dg['price'].min()
    max_value = dg['price'].max()
    price = st.sidebar.slider(
        "Price range:",
        min_value=min_value,
        max_value=max_value,
        value=(min_value, max_value),
        step=1.0
    )

    # Allow user to select coloring variable
    label = "Color Variable"
    options = ['Avg Reviews', 'No of reviews', 'Cancellation Policy', 'Price']
    vars = ['avg_review_scores', 'number_of_reviews', 'cancellation_policy_encoded', 'price']
    color_options = dict(zip(options, vars))
    coloring_var_label = st.sidebar.selectbox(label, options, index=0, key='color_variable')
    coloring_var = color_options[coloring_var_label]

    # Filter data based on user input
    filtered_df = dg[
        (dg['price'] >= price[0]) & (dg['price'] <= price[1]) &
        (dg['avg_review_scores'] >= ratings[0]) & (dg['avg_review_scores'] <= ratings[1]) &
        (dg['cancellation_policy'] == cancel_var) &
        (dg['property_type'] == property_type)
    ]

    # Cache the filtered DataFrame and coloring variable in session state
    st.session_state['geo_spatial_viz_result'] = {
        'filtered_df': filtered_df,
        'coloring_var': coloring_var
    }

    # Retrieve the cached results from session state
    cached_data = st.session_state['geo_spatial_viz_result']
    filtered_df = cached_data['filtered_df']
    coloring_var = cached_data['coloring_var']

    # Call visualize_map with the cached data
    if not filtered_df.empty:
        visualize_map(filtered_df, coloring_var)
    else:
        st.warning("No data available for the selected filters.")








def visualize_map(filtered_df, coloring_var):
    # Define a key for caching the folium map in session state
    #@st.cache_data
    def variables():
        # Extract necessary data for the map
        coordinates = list(filtered_df['address.location.coordinates'])
        values = filtered_df[coloring_var].values
        names = filtered_df['name'].values
        reviews = filtered_df['number_of_reviews'].values
        ratings = filtered_df['avg_review_scores'].values
        price = filtered_df['price'].values
        bedrooms = filtered_df['bedrooms'].values
        room_type = filtered_df['room_type'].values
        accommodates = filtered_df['accommodates'].values
        security_deposit = filtered_df['security_deposit'].values   


        # Choose a colormap and normalize the values
        cmap = cm.RdYlGn
        norm = Normalize(vmin=min(values), vmax=max(values))
    
        # Set initial location and zoom level
        initial_location = coordinates[0][::-1]  # Initial location based on the first set of coordinates
        zoom_level = 10
        
        # Create the Folium map
        folium_map = folium.Map(
            location=initial_location,
            zoom_start=zoom_level,
            tiles='CartoDB Voyager',
            attr='Map tiles by CartoDB, CC BY 3.0 — Map data © OpenStreetMap contributors',
            control_scale=False
        )
        
        # Add markers with color based on values
        for i, (lat, lon) in enumerate(coordinates):
            normalized_value = norm(values[i])
            color = cm.colors.to_hex(cmap(normalized_value))
            html = f"""
                <h3><span style='color: red;'>{names[i]}</span></h3><br>
                <p style='font-size: 16px; line-height: 0.5;'>Rating: <span style='color: blue;'>{ratings[i]}</span></p>
                <p style='font-size: 16px; line-height: 0.5;'>Reviews: <span style='color: blue;'>{reviews[i]}</span></p>
                <p style='font-size: 16px; line-height: 0.5;'>Price: <span style='color: green;'>{price[i]}</span></p>
                <p style='font-size: 16px; line-height: 0.5;'>Bedrooms: <span style='color: green;'>{bedrooms[i]}</span></p>
                <p style='font-size: 16px; line-height: 0.5;'>Room type: <span style='color: green;'>{room_type[i]}</span></p>
                <p style='font-size: 16px; line-height: 0.5;'>Accommodates: <span style='color: green;'>{accommodates[i]}</span></p>
                <p style='font-size: 16px; line-height: 0.5;'>Security Deposit: <span style='color: green;'>{security_deposit[i]}</span></p>
            """
            folium.CircleMarker(
                location=[lon, lat],
                radius=5,
                color=color,
                fill=True,
                popup=folium.Popup(html, max_width=400),
                fill_color=color,
                fill_opacity=1
            ).add_to(folium_map)
        return folium_map
    folium_map = variables()
    # Use the map from session state if it was previously calculated
    st_folium(folium_map, width=720, height=360)

def price_analysis_with_country():

    
    if 'clean_df' not in st.session_state:
        st.warning("No data available. Please clear the cache or run the data processing step again.")
        return
    
    df = st.session_state['clean_df']
    
    @st.cache_data
    def get_mean_prices():
        mean_prices_country = df.groupby('address.country')['price'].mean().sort_values().reset_index()
        mean_prices_property = df.groupby('property_type')['price'].mean().sort_values().reset_index()
        mean_prices_seasons = df.groupby('season')['price'].mean().sort_values().reset_index()

        #mean_prices_seasons['price'] = mean_prices_seasons['price']/mean_prices_seasons['price'].max()
        occupancy_season = df.groupby('season')['availability.availability_30'].mean().sort_values().reset_index()
        occupancy_season['availability.availability_30'] = occupancy_season['availability.availability_30'] * 10
        # Reshape the data from wide format to long format
        price = pd.melt(mean_prices_seasons, id_vars='season', value_vars=['price'], var_name='variable', value_name='y')
        occ_r = pd.melt(occupancy_season, id_vars='season', value_vars=['availability.availability_30'], var_name='variable', value_name='y')
        
        # Combine the two long format DataFrames
        price_oc_r = pd.concat([price, occ_r], ignore_index=True)
        

        
        # Group by 'property_type' and count
        count_room_type = df.groupby('property_type').size()
        count_room_type = count_room_type.sort_values(ascending=False)
        count_rnum = count_room_type.reset_index(name='count')

        
        country_number_rooms = df.groupby('address.country')['property_type'].count().sort_values().reset_index()
        # Convert the grouped data to a DataFrame using reset_index()

        
        occupancy_country = df.groupby('address.country')['availability.availability_30'].mean().sort_values().reset_index()
        occupancy_country['availability.availability_30'] = occupancy_country['availability.availability_30']/30


        
        # Merge df1 and df2 on the common column
        revenue_country = pd.merge(mean_prices_country, country_number_rooms, on='address.country')
        
        # Merge the merged DataFrame with df3 on the common column
        revenue_country = pd.merge(revenue_country, occupancy_country, on='address.country')
        
        # Multiply the columns
        # Multiply col1, col2, and col3 and store the result in a new column 'result'
        revenue_country['revenue'] = revenue_country['price'] * revenue_country['availability.availability_30'] * revenue_country['property_type']


        revenue_country = revenue_country[['address.country', 'revenue']]
        revenue_country = revenue_country.sort_values(by='revenue')
        

        return mean_prices_country, mean_prices_property, occupancy_country, count_rnum, country_number_rooms, revenue_country, price_oc_r

    @st.cache_data
    def other_variables():
        # Group the DataFrame by 'address.country' and find the index of the maximum 'Count' in each group
        acc_df = df.groupby(['address.country', 'accommodates']).size().reset_index(name='Count')
        ind = acc_df.groupby(['address.country'])['Count'].idxmax()
        # Use the indices to select rows with the maximum 'Count' in each group of 'address.country'
        acc_country = acc_df.loc[ind]

        acc_country['num_hotels'] = df.groupby(['address.country'])['property_type'].size().values

        

        #acc_country = acc_country#.reset_index(drop=True)

        acc_country['acc_type_percentage'] = acc_df['Count'] / acc_country['num_hotels'] * 100
        
        dg = df.groupby(['address.country', 'accommodates'])['price'].sum().reset_index(name='acc_price')
        
        acc_country['acc_price'] = dg['acc_price'].loc[ind]
        
        acc_country['total_price'] = df.groupby('address.country')['price'].sum().values
        
        acc_country['acc_price_share'] = acc_country['acc_price'] / acc_country['total_price'] * 100

        
        return acc_country


    
    mean_prices_country, mean_prices_property, occupancy_country, count_rtype, country_room_type, revenue_country, price_oc_r = get_mean_prices()
    acc_country = other_variables()

    
    st.markdown("----------")
    st.header("Price Variation Across Countries")
    # Display price variation across countries
    if 'fig1' not in st.session_state:
        fig1, ax1 = plt.subplots(figsize=(12, 8))
        ax1p = sns.barplot(
            x='address.country',
            y='price',
            data=mean_prices_country,
            palette='deep',
            ax=ax1,
            errorbar=None,
            capsize=0.2
        )
        for container in ax1p.containers:
            ax1p.bar_label(container, fmt='%.2f', padding=3)        
        ax1.set_title('Airbnb Hotels Average Price by Country', fontsize=20)
        ax1.set_ylabel('Average Price ($)', fontsize=20)
        ax1.set_xlabel('', fontsize=12)
        ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45, ha='right')
        ax1.tick_params(axis='both', labelsize=18)
        st.session_state['fig1'] = fig1
    st.pyplot(st.session_state['fig1'])



    st.markdown("-----")
    st.header("Number of Hotels by Country")
    
    # Display price variation across countries
    if 'fig1.5' not in st.session_state:
        fig1_5, ax1_5 = plt.subplots(figsize=(12, 8))
        ax1_5p = sns.barplot(
            x='address.country',
            y='property_type',
            data=country_room_type,
            palette='deep',
            ax=ax1_5,
            errorbar=None,
            capsize=0.2
        )
        for container in ax1_5p.containers:
            ax1_5p.bar_label(container, fmt='%.2d', padding=3)        
        ax1_5.set_title('Airbnb Hotels Numbers by Country', fontsize=20)
        ax1_5.set_ylabel('Number of Hotels', fontsize=20)
        ax1_5.set_xlabel('', fontsize=12)
        ax1_5.set_xticklabels(ax1_5.get_xticklabels(), rotation=45, ha='right')
        ax1_5.tick_params(axis='both', labelsize=18)
        st.session_state['fig1.5'] = fig1_5
    st.pyplot(st.session_state['fig1.5'])


    st.markdown("----------")
    st.header("Occupancy Variation across Countries")
    # Display price variation across countries
    if 'fig1.1' not in st.session_state:
        fig1_1, ax1_1 = plt.subplots(figsize=(12, 8))
        ax1_1p = sns.barplot(
            x='address.country',
            y='availability.availability_30',
            data=occupancy_country,
            palette='deep',
            ax=ax1_1,
            errorbar=None,
            capsize=0.2
        )
        for container in ax1_1p.containers:
            ax1_1p.bar_label(container, fmt='%.2f', padding=3)        
        ax1_1.set_title('Airbnb Hotels Occupancy Rate by Country', fontsize=20)
        ax1_1.set_ylabel('Occupancy Rate', fontsize=20)
        ax1_1.set_xlabel('', fontsize=12)
        ax1_1.set_xticklabels(ax1_1.get_xticklabels(), rotation=45, ha='right')
        ax1_1.tick_params(axis='both', labelsize=18)
        st.session_state['fig1.1'] = fig1_1
    st.pyplot(st.session_state['fig1.1'])
    
    
    st.markdown("-----")
    st.header("Price Variation by Room Type (aggregate)")

    # Display price variation with room type
    if 'fig2' not in st.session_state:
        fig2, ax2 = plt.subplots(figsize=(16, 12))
        ax2p = sns.barplot(
            y='property_type',
            x='price',
            data=mean_prices_property,
            palette='deep',
            ax=ax2,
            errorbar=None,
            capsize=0.2
        )
        for container in ax2p.containers:
            ax2p.bar_label(container, fmt='%.2f', padding=3)           
        ax2.set_title('Airbnb Hotels Average Price by Room Type', fontsize=21)
        ax2.set_xlabel('Average Price ($)', fontsize=21)
        ax2.set_ylabel('', fontsize=21)
        ax2.tick_params(axis='both', labelsize=21)
        st.session_state['fig2'] = fig2
    st.pyplot(st.session_state['fig2'])

    st.markdown("-----")
    st.header("Number of Hotels by Property Type (aggregate)")

    # Display price variation across seasons
    if 'fig2.5' not in st.session_state:
        fig2_5, ax2_5 = plt.subplots(figsize=(16, 12))
        ax2_5p = sns.barplot(
            y='property_type',
            x='count',
            data=count_rtype,
            palette='deep',
            ax=ax2_5,
            errorbar=None,
            capsize=0.2
        )
        for container in ax2_5p.containers:
            ax2_5p.bar_label(container, fmt='%.2d', padding=3)           
        ax2_5.set_title('Number of Airbnb Hotels by Room Type', fontsize=21)
        ax2_5.set_xlabel('Number of hotels', fontsize=21)
        ax2_5.set_ylabel('', fontsize=21)
        ax2_5.tick_params(axis='both', labelsize=21)
        st.session_state['fig2.5'] = fig2_5
    st.pyplot(st.session_state['fig2.5'])


    st.markdown("---------")
    st.header("Price variation by seasons (aggregate)")
    # Display price variation across seasons
    if 'fig3' not in st.session_state:
        fig3, ax3 = plt.subplots(figsize=(16, 12))
        ax3p = sns.barplot(
            y='y',
            x='season',
            data=price_oc_r,
            hue='variable',
            ax=ax3,
            errorbar=None,
            capsize=0.2
        )
        #sns.barplot(x='Category', y='Variable1', data=df, color='blue', label='Variable1')
        #sns.barplot(x='season', y='availability.availability_30', data=price_oc_r, color='orange', label='Occupancy Rate', alpha=0.7)
        #sns.barplot(x='season', y='Variable3', data=df, color='green', label='Variable3', alpha=0.5)
        legend = plt.gca().legend()
        legend_labels = {'price': 'Price', 'availability.availability_30': 'Occupancy Rate'}
        # Set custom labels for the legend
        for text, label in zip(legend.get_texts(), legend_labels.values()):
            text.set_text(label)
        for container in ax3p.containers:
            ax3p.bar_label(container, fmt='%.2f', padding=3)
                    
        ax3.set_title('Airbnb Hotels Price versus Occupancy Rate by Seasons', fontsize=21)
        ax3.set_ylabel('Price ($) & Occupancy Rate (scaled)', fontsize=21)
        ax3.set_xlabel('', fontsize=21)
        ax3.tick_params(axis='both', labelsize=21)
        st.session_state['fig3'] = fig3
    st.pyplot(st.session_state['fig3'])


    st.markdown("-----")
    st.header("Average Revenue by Country")
    
    # Display price variation across countries
    if 'fig1.2' not in st.session_state:
        fig1_2, ax1_2 = plt.subplots(figsize=(12, 8))
        ax1_2p = sns.barplot(
            x='address.country',
            y='revenue',
            data=revenue_country,
            palette='deep',
            ax=ax1_2,
            errorbar=None,
            capsize=0.2
        )
        for container in ax1_2p.containers:
            ax1_2p.bar_label(container, fmt='%.2f', padding=3)           
        ax1_2.set_title('Airbnb Revenue by Country', fontsize=20)
        ax1_2.set_ylabel('Average Revenue ($)', fontsize=20)
        ax1_2.set_xlabel('', fontsize=12)
        ax1_2.set_xticklabels(ax1_2.get_xticklabels(), rotation=45, ha='right')
        ax1_2.tick_params(axis='both', labelsize=18)
        st.session_state['fig1.2'] = fig1_2
    st.pyplot(st.session_state['fig1.2'])


    st.markdown("-----")
    st.header("Preferred Accomodation by Country")
    
    # Display price variation across countries
    if 'fig4' not in st.session_state:
        fig4, ax4 = plt.subplots(figsize=(12, 8))
        ax4p = sns.barplot(
            x='address.country',
            y='accommodates',
            data=acc_country,
            palette='deep',
            ax=ax4,
            errorbar=None,
            capsize=0.2
        )
        for container in ax4p.containers:
            ax4p.bar_label(container, fmt='%.2d', padding=3)           
        ax4.set_title('Accommodation type preferred by Country', fontsize=20)
        ax4.set_ylabel('Accommodates', fontsize=20)
        ax4.set_xlabel('', fontsize=12)
        ax4.set_xticklabels(ax4.get_xticklabels(), rotation=45, ha='right')
        ax4.tick_params(axis='both', labelsize=18)
        st.session_state['fig4'] = fig4
    st.pyplot(st.session_state['fig4'])


    st.markdown("-----")
    st.header("Fraction of Preferred Accommodate by Country")
    
    # Display price variation across countries
    if 'fig5' not in st.session_state:
        fig5, ax5 = plt.subplots(figsize=(12, 8))
        ax5p = sns.barplot(
            x='address.country',
            y='acc_type_percentage',
            data=acc_country,
            palette='deep',
            ax=ax5,
            errorbar=None,
            capsize=0.2
        )
        for container in ax5p.containers:
            ax5p.bar_label(container, fmt='%.2f', padding=3)           
        ax5.set_title('Fraction of Accommodates type', fontsize=20)
        ax5.set_ylabel('Accommodates (Fraction)', fontsize=20)
        ax5.set_xlabel('', fontsize=12)
        ax5.set_xticklabels(ax5.get_xticklabels(), rotation=45, ha='right')
        ax5.tick_params(axis='both', labelsize=18)
        st.session_state['fig5'] = fig5
    st.pyplot(st.session_state['fig5'])


    st.markdown("-----")
    st.header("Preferred Accommodate's Price Share by Country")
    
    # Display price variation across countries
    if 'fig6' not in st.session_state:
        fig6, ax6 = plt.subplots(figsize=(12, 8))
        ax6p = sns.barplot(
            x='address.country',
            y='acc_price_share',
            data=acc_country,
            palette='deep',
            ax=ax6,
            errorbar=None,
            capsize=0.2
        )
        for container in ax6p.containers:
            ax6p.bar_label(container, fmt='%.2f', padding=3)           
        ax6.set_title('Fraction of price share for preferred accommodate type', fontsize=20)
        ax6.set_ylabel('Price share % (Preferred Accommodation)', fontsize=20)
        ax6.set_xlabel('', fontsize=12)
        ax6.set_xticklabels(ax6.get_xticklabels(), rotation=45, ha='right')
        ax6.tick_params(axis='both', labelsize=18)
        st.session_state['fig6'] = fig6
    st.pyplot(st.session_state['fig6'])


def prices_dynamic_plot():

    
    if 'clean_df' not in st.session_state:
        st.warning("No data available. Please clear the cache or run the data processing step again.")
        return
    
    df = st.session_state['clean_df']
    df['month'] = df['first_review'].dt.month_name()
    df['year'] = df['first_review'].dt.year
    # Define the order of months
    month_order = [
        'January', 'February', 'March', 'April', 'May', 'June', 'July',
        'August', 'September', 'October', 'November', 'December'
    ]
    
    @st.cache_data
    def get_country_year():
        country = df['address.country'].unique()
        year = df['year'].unique()
        month = df['month'].unique()
        
        correlation = df.select_dtypes(exclude='object').corrwith(df['price'])

            
        return country, year, month, correlation
    
    #############################################################################################
    # Create the heatmap

    country, year, month, correlation = get_country_year()

    ##################################################

    st.markdown("-------")   
    st.header("Price correlations with other variables")

    col_hmp = st.columns(3)

    button_hmp = col_hmp[1].selectbox("Number of features", [2, 4, 6, 8, 10, 12, 16, 20, 24, 32], index=0, key='featuer_heatmap')

    columns = correlation.sort_values(ascending=False)[:button_hmp].index.to_list()
    correlation_matrix = df[columns].corr()  
    plt.rcParams.update({'font.size': 14})
    fig1, ax1 = plt.subplots(figsize=(14, 10))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f', cbar=True)
    ax1.set_title('Price Correlation with other Factors', fontsize=21)
    ax1.tick_params(axis='both', labelsize=16) 
    ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45, ha='right')
    st.pyplot(fig1)




    #########################################################
    #                    Seasons
    ########################################################


    
    st.markdown("-------")

    st.header("Price trend by Seasons")


    col0 = st.columns(3)
    country_option = col0[0].multiselect("Select country(s)", country, default = 'Turkey', key='price_by_country0')
    year_option = col0[1].multiselect("Select year(s)", year, default = 2018, key='price_by_year0')
    #month_option = col[2].multiselect("select month(s)", month, default = 1, key='price_by_month')

    fig1_5, ax1_5 = plt.subplots(figsize=(12, 10))    


    if len(country_option) == 1:
        dg = df[df['address.country'].isin(country_option)]
        #dg['month'] = pd.Categorical(dg['month'], categories=month_order, ordered=True)
        for yr in year_option:
            sns.lineplot(
                data=dg[dg['year'] == yr],
                x='season',  # Replace 'date_column' with your date column name
                y='price',  # Replace 'price' with the column you want to plot
                marker='o',  # Optional: add markers to the line plot
                label=yr,  # Optional: add a label for the legend
                markersize=10
            )

    elif len(year_option) == 1:
        dg = df[df['year'].isin(year_option)]
        #dg['month'] = pd.Categorical(dg['month'], categories=month_order, ordered=True)
        for country_ in country_option:
            sns.lineplot(
                data=dg[dg['address.country'] == country_],
                x='season',  # Replace 'date_column' with your date column name
                y='price',  # Replace 'price' with the column you want to plot
                marker='o',  # Optional: add markers to the line plot
                label=country_,  # Optional: add a label for the legend
                markersize=10
            )
    #ax3.set_title('Airbnb Hotels Average Price by Seasons', fontsize=21)
    ax1_5.set_xlabel('', fontsize=21)
    ax1_5.set_ylabel('Price ($)', fontsize=21)
    ax1_5.tick_params(axis='both', labelsize=21) 
    ax1_5.set_xticklabels(ax1_5.get_xticklabels(), rotation=45, ha='right')
    st.pyplot(fig1_5) 






    
    #########################################################
    #                    Months
    #########################################################
    st.markdown("-------")

    st.header("Price trend by months")


    col = st.columns(3)
    country_option = col[0].multiselect("Select country(s)", country, default = 'Turkey', key='price_by_country')
    year_option = col[1].multiselect("Select year(s)", year, default = 2018, key='price_by_year')
    #month_option = col[2].multiselect("select month(s)", month, default = 1, key='price_by_month')

    fig2, ax2 = plt.subplots(figsize=(12, 10))    


    if len(country_option) == 1:
        dg = df[df['address.country'].isin(country_option)]
        dg['month'] = pd.Categorical(dg['month'], categories=month_order, ordered=True)
        for yr in year_option:
            sns.lineplot(
                data=dg[dg['year'] == yr],
                x='month',  # Replace 'date_column' with your date column name
                y='price',  # Replace 'price' with the column you want to plot
                marker='o',  # Optional: add markers to the line plot
                label=yr,  # Optional: add a label for the legend
                markersize=10
            )

    elif len(year_option) == 1:
        dg = df[df['year'].isin(year_option)]
        dg['month'] = pd.Categorical(dg['month'], categories=month_order, ordered=True)
        for country_ in country_option:
            sns.lineplot(
                data=dg[dg['address.country'] == country_],
                x='month',  # Replace 'date_column' with your date column name
                y='price',  # Replace 'price' with the column you want to plot
                marker='o',  # Optional: add markers to the line plot
                label=country_,  # Optional: add a label for the legend
                markersize=10
            )
    #ax3.set_title('Airbnb Hotels Average Price by Seasons', fontsize=21)
    ax2.set_xlabel('', fontsize=21)
    ax2.set_ylabel('Price ($)', fontsize=21)
    ax2.tick_params(axis='both', labelsize=21) 
    ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45, ha='right')
    st.pyplot(fig2) 


    #########################################################
    #                    Years
    #########################################################
    st.markdown("-------")
    st.header("Price trend by years")


    col1 = st.columns(3)
    country_option1 = col1[1].multiselect("Select country(s)", country, default = 'Turkey', key='price_by_country1')
    #year_option1 = col1[1].multiselect("Select year(s)", year, default = 2018, key='price_by_year1')
    
    fig3, ax3 = plt.subplots(figsize=(12, 10)) 

    for country_ in country_option1:
        dg = df[df['address.country'].isin([country_])]
        dg = dg.groupby('year')['price'].mean().reset_index()

        sns.lineplot(
            data=dg,
            x='year',  # Replace 'date_column' with your date column name
            y='price',  # Replace 'price' with the column you want to plot
            marker='o',  # Optional: add markers to the line plot
            label=country_,  # Optional: add a label for the legend
            markersize=10
        )
    
    ax3.set_ylabel('Price ($)', fontsize=20)
    ax3.set_xlabel('', fontsize=12)
    ax3.set_xticklabels(ax3.get_xticklabels(), rotation=45, ha='right')
    ax3.tick_params(axis='both', labelsize=18)
    ax3.legend(loc='best')
    st.pyplot(fig3)

    
    st.markdown("-------")




def occupancy_rate_analysis():
    # Load data from session state
    if 'clean_df' not in st.session_state:
        st.warning("No data available. Please clear the cache or run the data processing step again.")
        return

    # Load the data and preprocess
    df = st.session_state['clean_df'][['first_review', 'price', 'season', 'address.country'] + Y_COLS_VARS]
    df['year'] = df['first_review'].dt.year
    df['month'] = df['first_review'].dt.month_name()
    
    # Get unique country and year
    country = df['address.country'].unique()
    year = df['year'].unique()



    st.markdown("-------------")
    # Occupancy Rate by Season
    st.header("Occupancy Rate by Season")
    # Create selection widgets
    col1, col2, col3 = st.columns(3)
    country_option = col1.multiselect("Select country(s)", country, default=['Turkey'], key='country_option')
    year_option = col2.multiselect("Select year(s)", year, default=[2018], key='year_option')
    availability_option = col3.selectbox("Select availability type", Y_COLS, key='availibility_type')
    availability_var = Y_COLS_VARS[Y_COLS.index(availability_option)]
    
    # Calculate occupancy rate and group data
    df['occupancy_rate'] = (df[availability_var] / df[availability_var].max()) * 100
    
    fig, ax = plt.subplots(figsize=(12, 8))
    if len(country_option) == 1:
        selected_country = country_option[0]
        dg = df[df['address.country'] == selected_country]        
        for selected_year in year_option:
            dg1 = dg[dg['year'] == selected_year]
            grouped_dg = dg1.groupby('season')['occupancy_rate'].mean().reset_index()
        
            # Plot occupancy rate by season
            plot_data(fig,
                ax,      
                grouped_dg,
                grouped_dg,
                'season',
                'occupancy_rate',
                f"{selected_country} in {selected_year}",
                f"Occupancy Rate (%)",
                False,
                None
            )

    elif len(year_option) == 1:
        selected_year = year_option[0]
        dg = df[df['year'] == selected_year]
        for selected_country in country_option:
            dg1 = dg[dg['address.country'] == selected_country]
            grouped_dg = dg1.groupby('season')['occupancy_rate'].mean().reset_index()
        
            
            # Plot occupancy rate by month
            plot_data(fig,
                ax,      
                grouped_dg,
                grouped_dg,
                'season',
                'occupancy_rate',
                f"{selected_country} in {selected_year}",
                "Occupancy Rate",
                False,
                None
            )
    st.pyplot(fig)




    

    # Occupancy Rate by Month
    st.markdown("-------------")
    st.header("Occupancy Rate by Month")
    col4, col5, col6 = st.columns(3)
    country_option1 = col4.multiselect("Select country(s)", country, default=['Turkey'], key='country_option1')
    year_option1 = col5.multiselect("Select year(s)", year, default=[2018], key='year_option1')
    availability_option1 = col6.selectbox("Select availability type", Y_COLS, key='availibility_type1')
    availability_var1 = Y_COLS_VARS[Y_COLS.index(availability_option1)]
    fig, ax = plt.subplots(figsize=(12, 8))
    if len(country_option1) == 1:
        selected_country = country_option1[0]
        dg = df[df['address.country'] == selected_country]
        dg['month'] = pd.Categorical(dg['month'], categories=MONTH_ORDER, ordered=True)
        for selected_year in year_option1:
            filtered_dg = dg[dg['year'] == selected_year]
            grouped_dg = filtered_dg.groupby('month')[availability_var1].mean().reset_index()
            grouped_dg[availability_var1] = grouped_dg[availability_var1]/30 * 100
            # Plot occupancy rate by month
            plot_data(fig,
                ax,      
                grouped_dg,
                grouped_dg,
                'month',
                availability_var1,
                f"{selected_country} in {selected_year}",
                "Occupancy Rate",
                False,
                None
            )
    
    elif len(year_option1) == 1:
        selected_year = year_option1[0]
        dg = df[df['year'] == selected_year]
        dg['month'] = pd.Categorical(dg['month'], categories=MONTH_ORDER, ordered=True)
        for selected_country in country_option1:
            filtered_dg = dg[dg['address.country'] == selected_country]
            grouped_dg = filtered_dg.groupby('month')[availability_var1].mean().reset_index()
            grouped_dg[availability_var1] = grouped_dg[availability_var1]/30 * 100
            
            # Plot occupancy rate by month
            plot_data(fig,
                ax,      
                grouped_dg,
                grouped_dg,
                'month',
                availability_var1,
                f"{selected_country} in {selected_year}",
                "Occupancy Rate",
                False,
                None
            )
    st.pyplot(fig)





    # Demand Fluctuations
    st.markdown("-------------")    
    st.header("Demand Fluctuations")
    col7, col8, col9 = st.columns(3)
    country_option2 = col7.multiselect("Select country(s)", country, default=['Turkey'], key='country_option2')
    price_option2 = col8.checkbox("Include Price?", value = False)
    availability_option2 = col9.selectbox("Select availability type", Y_COLS, key='availability_option2')
    availability_var2 = Y_COLS_VARS[Y_COLS.index(availability_option2)]


    fig, ax = plt.subplots(figsize=(12, 8))
    # Calculate demand percentage
    df['demand_percentage'] = (df[availability_var2] / df[availability_var2].max()) * 100
    for selected_country in country_option2:
        filtered_df = df[df['address.country'] == selected_country]
        grouped_df = filtered_df.groupby('year')['demand_percentage'].mean().reset_index()
        grouped_df_price = filtered_df.groupby('year')['price'].mean().reset_index() 
        grouped_df_price['price'] = grouped_df_price['price']/grouped_df_price['price'].max() * 100 
        #grouped_df['demand_category'] = pd.cut(grouped_df['demand_percentage'], bins=DEMAND_BINS, labels=DEMAND_LABELS, right=False)


        #st.write(grouped_df_price['price'])
        # Plot demand fluctuations
        plot_data(fig,
            ax,
            grouped_df,
            grouped_df_price,
            'year',
            'demand_percentage',
            f"{selected_country} in {selected_year}",
            "Demand (Percentage)",
            price_option2,
            f"P-{selected_country}"
        )
    st.pyplot(fig)
    if price_option2:
        st.warning("Note: By setting price option to display too, you cannot select multiple countries at a time. ")
        st.warning("Note: Price option is for comparing the demand vs price for a particular country at once. ")
    
        # sns.lineplot(data=grouped_df, x='year', y='demand_percemtage', marker='o', label=f"{selected_country}")
        # if price_option2:
        #     sns.lineplot(
        #         data=grouped_df_price,
        #         x='year',  # Replace 'date_column' with your date column name
        #         y='price',  # Replace 'price' with the column you want to plot
        #         marker='s',  # Optional: add markers to the line plot
        #         label=selected_country  # Optional: add a label for the legend
        #     )     
        # ax.set_title(f"Demand Fluctuations for {selected_country}", fontsize=20)
        # ax.set_ylabel(Demand (Percentage), fontsize=18)
        # ax.set_xlabel('')
        # ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
        # ax.tick_params(axis='both', labelsize=14)
        # ax.legend(loc='best')
        # st.pyplot(fig)   


def plot_data(fig, ax, grouped_df, grouped_df_price, x_col, y_col, title, ylabel, price_, price_title_):
    sns.lineplot(data=grouped_df, x=x_col, y=y_col, marker='o', label=title, markersize=10)
    if price_:
        sns.lineplot(
            data=grouped_df_price,
            x='year',  # Replace 'date_column' with your date column name
            y='price',  # Replace 'price' with the column you want to plot
            marker='s',  # Optional: add markers to the line plot
            label=price_title_,  # Optional: add a label for the legend
            markersize=10   # Adjust the marker size here.
        )         
    #ax.set_title(title, fontsize=20)
    ax.set_ylabel(ylabel, fontsize=18)
    ax.set_xlabel('')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    ax.tick_params(axis='both', labelsize=14)
    ax.legend(loc='best')




def pages():

    # Add navigation options to the sidebar
    st.sidebar.title("Vizualization Features")
    pages = {
        "Home": open_header,
        "Geo Spatial Visualization": geo_spatial_viz,
        "Price Analysis (Aggregate & Country wise)": price_analysis_with_country,
        "Price analysis (Year & Month wise)": prices_dynamic_plot,
        "Availability Analysis (Year & Month wise)": occupancy_rate_analysis,
        # Add more pages as needed
    }

    # User selects which page to navigate to
    selected_page = st.sidebar.radio("Go to:", list(pages.keys()))

    # Execute the selected function (subpage) if any is selected
    if pages[selected_page]:
        pages[selected_page]()
    else:
        # Display the home page or a welcome message
        st.write("Welcome to the app! Please select a page from the sidebar.")


def main():
    pages()



if __name__ == "__main__":
    main()










