# aribnb_predictor
Project Summary: Airbnb Data Scraping, Processing, and Price Prediction

This project involves developing a comprehensive data pipeline that extracts, processes, and uses Airbnb listing data for predictive modeling. The overall goal of the project is to predict the prices of Airbnb listings.

The primary source of data for this project is Inside Airbnb (http://insideairbnb.com/get-the-data), a website that provides publicly available information about Airbnb's listings in many cities around the world. The developed program automatically downloads the required data from this site, saving it locally for further processing.

Once downloaded, the data files, which are initially compressed, are extracted and stored in a local directory. This step ensures that all relevant data is readily accessible for the subsequent stages of the project.

The data then undergoes a cleaning process, where any inconsistencies or missing values are addressed, and the data is structured in a form suitable for analysis. This clean, processed data serves as the foundation for the predictive modeling aspect of the project. The program is capable of predicting Airbnb listing prices based on the processed data. 

An additional feature of the program is its integration with the Google Maps API to fetch geolocation data (latitude and longitude) for each Airbnb listing. This allows the program to also determine the neighborhood in which each Airbnb listing is located. By combining this geolocation data with the listing data from Inside Airbnb, the program can provide more granular and location-specific insights into Airbnb pricing.

In order to explore the project you can run through the jupyter notebook demo_scrape and predict airbnb.ipynb. Make sure you have stored the python function file scrape_and_predict_functions.py in the same working directory.
