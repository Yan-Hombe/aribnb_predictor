# this file contains all the functions that are needed to scrape the airbnb data an make some predictions
# the data is from the website: http://insideairbnb.com/get-the-data.html
# you may want to only make use of certain parts of the function file
# make sure you have a connection to the function file in the same directory as this file


# import the needed packages
# import libraries
import os
import requests
from bs4 import BeautifulSoup
import re
import gzip
import shutil
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV

import geopandas as gpd
from shapely.geometry import Point, MultiPolygon

# Find all links on the page 
def get_links():
    """Get all links on the page 
    this function interact with the website of insideairbnb.com
    and returns all links on the page
    
    output: list of links which can later be used to download the data
    """
    # Set the URL to the official website of Inside Airbnb
    url = 'http://insideairbnb.com/get-the-data/'

    # Send an HTTP request and fetch the content of the website
    response = requests.get(url)
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
    # Find all links on the page
    csv_links = soup.find_all('a', href=re.compile('listings.csv.gz'))
    return csv_links

def get_geojson_links():
    """Get all links on the page 
    this function interact with the website of insideairbnb.com
    and returns all links on the page
    
    output: list of links which can later be used to download the data
    """
    # Set the URL to the official website of Inside Airbnb
    url = 'http://insideairbnb.com/get-the-data.html'

    # Send an HTTP request and fetch the content of the website
    response = requests.get(url)
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
    # Find all links on the page
    geojson_links = soup.find_all('a', href=re.compile('geojson'))
    return geojson_links


def get_links_certain_city(csv_links, cities):
    """
    Used to specify links that only certain cities are downloaded
    
    Parameters:
    csv_link (list): list of all the links on the webpage tipically from function get_links()
    value (string, list): defines which cities to scrape

    Returns:
    list of cities that should be scraped
    """
    links = []
    if isinstance(cities, list):
        for val in cities: 
            for link in csv_links:
                if val in link['href']:
                    links.append(link)
    else:
        for link in csv_links:
            if cities in link['href']:
                links.append(link)
    return links

def get_geojson_links_certain_city(geojson_links, cities):
    """
    Used to specify links that only certain cities are downloaded
    
    Parameters:
    csv_link (list): list of all the links on the webpage tipically from function get_links()
    value (string, list): defines which cities to scrape

    Returns:
    list of cities that should be scraped
    """
    links = []
    if isinstance(cities, list):
        for val in cities: 
            for link in geojson_links:
                if val in link['href']:
                    links.append(link)
    else:
        for link in geojson_links:
            if cities in link['href']:
                links.append(link)
    return links

def download_csv_save_in_folder(csv_links, save_folder):
    """
    scrapes the city files from the website and put them into csv.gz on your directory

    Parameters: 
    csv_links (list): links with cities to download
    save_folder (string): folder name in which files should be stored

    Returns: nothing 
    """
    # Iterate through each CSV.gz link and download the file
    for link in csv_links:
        file_url = link['href']

        region_name = str(link['href'])
        # remove the characters up to the third /
        region_name = region_name.split('/', 3)[3]
        # return element 0 to 2 in the list
        region_name = region_name.split('/', 3)[0:3]
        # combine the list in a string with _ as separator
        region_name = '_'.join(region_name)

        file_name = f'{region_name}.csv.gz'

        
        file_path = os.path.join(str(save_folder), file_name)
        
        # Download the CSV file and save it
        with requests.get(file_url, stream=True) as r:
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
        print(f'Downloaded: {file_name}')

def download_geojson_save_in_folder(geojson_links, save_folder):
    # iterate through each geojson link and download the file
    for link in geojson_links:
        file_url = link['href']

        region_name = str(link['href'])
        # remove the characters up to the fithd /
        region_name = region_name.split('/', 5)[5]
        # remove the characters after the first /
        region_name = region_name.split('/', 1)[0]
        # name for the file
        file_name = f'{region_name}.geojson'

        # define the path where the file should be saved
        file_path = os.path.join(str(save_folder), file_name)

        # Download the geojson file and save it
        with requests.get(file_url, stream=True) as r:
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
        print(f'Downloaded: {file_name}')

def extract_gz_from_to(from_file_path, to_file_path):
    """
    extract all the csv.gz and safe them in the directory

    Parameters: 
    from_file_path (string): name of folder with .csv.gz files
    to_file_path (string): name of folder where to sotre the .csv files

    Returns: nothing
    """
    # iteraate through the files in the folder
    for file in os.listdir(str(from_file_path)):
        # check if the file is a .gz file
        if file.endswith('.gz'):
            # create the path to the file
            file_path = os.path.join(str(from_file_path), file)
            # create the path to the extracted file
            file_path_extracted = os.path.join(str(to_file_path), file[:-3])
            # extract the file
            with gzip.open(file_path, 'rb') as f_in:
                with open(file_path_extracted, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            print(f'Extracted: {file_path_extracted}')

def convert_csv_to_dataframe_merge(from_file_path):
    """
    takes all csv files out of the folder in current path and reads it as pandas data frame 
    then adds country, region and city as variable and merges dataframes into one.

    Parameters: 
    from_file_path (string): folder name in which csv files are stored.

    Returns:
    merged pandas data frame with all variables
    """
    # create an empty list to store the dataframes
    # list is needed to merge the dataframes later
    df_list = []

    # define list names for later use
    name_lst = ['country', 'region', 'city']

    # iteraate through the files in the folder
    for file in os.listdir(str(from_file_path)):
        # check if the file is a .csv file
        if file.endswith('.csv'):
            # create the path to the file
            file_path = os.path.join(str(from_file_path), file)
            # read the csv file into a dataframe
            df = pd.read_csv(file_path)

            # change path direction into list to include in df
            location_str = file[:-4]
            location_lst = location_str.split('_')

            # include country, region, city in df
            for i in range(len(name_lst)):
                df[name_lst[i]] = location_lst[i]

            # append the dataframe to the list
            df_list.append(df)
    # merge the dataframes in the list by rows
    df_merged = pd.concat(df_list, axis=0)
    # create new index for df_merged
    df_merged = df_merged.reset_index(drop=True)
    return df_merged


def data_clean(df, round_long_lat = False):
    """
    apply some data cleaning and preparations

    Parameters:
    df (pandas dataframe): dataframe to be cleaned

    Returns:
    cleaned pandas dataframe
    """

    # create a copy so it does not change original dataframe globaly
    df = df.copy()
    # delete first character in string of data frame in the price column
    def man_price(x):
        x = x.replace(',', '')
        return float(x[1:])
    df['price'] = df['price'].apply(man_price)

    # round the long and lat to 2 digits for the prediction model
    if round_long_lat == True:
        def long_lat_round(x):
            return round(x, 2)
        df['latitude'] = df['latitude'].apply(long_lat_round)
        df['longitude'] = df['longitude'].apply(long_lat_round)
    
    # convert the host_has_profile_pic to 0 and 1
    def convert_t_f_to_bool(x):
        if x == 't':
            return 1
        else:
            return 0
    # all booelean strings in the dataframe
    list_all_bool = ['host_has_profile_pic', 'host_identity_verified', 'instant_bookable', 'has_availability']

    # apply the function to all boolean string variables
    for var in list_all_bool:
        df[var] = df[var].apply(convert_t_f_to_bool)

    return df

def predict_random_forest(features, outcome, hyperparamopt=False, n_estimators = 100):
    """
    This model is used to fit a random forest model. bear in mind that it can be very compuational expensive
    to train a random forest prediction model
    
    Parameters:
    feature (pandas dataframe): only floats or int allowed. No Nan allowed
    outcome (pandas series): only floats or int allowed. No Nan allowed
    hyperparamopt (bool): does some parameter optimization. default is false
    n_estimator (int): gives number of estimators to the model. Default is 100

    Returns: 
    Fitted random forest model
    """

    if hyperparamopt == True:
        # Define the hyperparameters to search over
        param_grid = {
        'max_depth': [10, 20, 30],
        'n_estimators': [100, 200, 300]
    }
        # intitialize the model
        rf = RandomForestRegressor(random_state=42)

        # Use grid search to find the best hyperparameters
        grid_search = GridSearchCV(rf, param_grid=param_grid, cv=10, scoring='neg_mean_squared_error')
        # fit the model
        fitmodel = grid_search.fit(features, outcome)
        
    else:
        # intitialize the model
        rf = RandomForestRegressor(random_state=42, n_estimators=n_estimators)
        # fit the model
        fitmodel = rf.fit(features, outcome)

    return fitmodel

def get_geocode(address, api_key):
    """
    This function takes an address and returns the latitude and longitude of the address
    Parameters:
    address (string): address of the location
    api_key (string): api key for google cloud project
    
    Returns:
    latitude (float): latitude of the address
    longitude (float):  longitude of the address
    """
    
    # Define the API URL
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}"
    
    # Send a request to the API and get the response
    response = requests.get(url)
    
    # Convert the response to JSON
    data = response.json()

    # If the geocoding was successful, print the latitude and longitude
    if data['status'] == 'OK':
        latitude = data['results'][0]['geometry']['location']['lat']
        longitude = data['results'][0]['geometry']['location']['lng']
        return latitude, longitude
    else:
        return None, None
    
def get_neighbourhood(input_longitude, input_latitude, file_path):
    """
    This function gives the neighbourhood of a given longitude and latitude
    Parameters:
    input_longitude (float): longitude of the location
    input_latitude (float): latitude of the location
    file_path (str): path to the geojson file
    
    Returns:
    neighbourhood (str): name of the neighbourhood"""
    # Read the .geojson file
    geo_data = gpd.read_file(file_path)

    # Create a Point object from the input coordinates
    input_point = Point(input_longitude, input_latitude)
    # check whether the point is in the polygon
    inputpoint_contained = geo_data['geometry'].contains(input_point) == True
    # Find the index of the polygon that contains the point (if any)
    polygon_index = inputpoint_contained.idxmax() if inputpoint_contained.any() else None

    if polygon_index is not None:
    # get neighbourhood of the polygon (long lat input)
        return str(geo_data['neighbourhood'][polygon_index])
    else:
        print('no neighbourhood found. Please check your longitude and latitude input')
