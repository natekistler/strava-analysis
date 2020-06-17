import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import ppscore as pps
import datetime

filepath = '/Users/natekistler/PycharmProjects/strava-analysis/Data Files/strava_data_raw.csv'

data = pd.read_csv(filepath)

def convert_to_imperial(data):
    kph_to_mph = 2.23694
    meters_to_feet = 3.28084
    km_to_miles = 0.621371
    data['average_speed [mph]'] = data['average_speed'] * kph_to_mph
    data['average_temp [F]'] = (data['average_temp'] * 1.8) + 32
    data['distance [miles]'] = (data['distance'] / 1000) * km_to_miles
    data['elev_high [ft]'] = data['elev_high'] * meters_to_feet
    data['elev_low [ft]'] = data['elev_low'] * meters_to_feet
    data['max_speed [mph]'] = data['max_speed'] * kph_to_mph
    data['total_elevation_gain [ft]'] = data['total_elevation_gain'] * meters_to_feet
    return data
    

gear_dict = {'b6284755': 'Canyon Endurace CF SL 7.0',
             'b6004319': 'Giant AnyRoad 2'}

#Clean Data
data['gear_id'] = data['gear_id'].replace(gear_dict)

#Convert to imperial units
data = convert_to_imperial(data)


#Modify and Seperate time data
data['start_date_local'] = data['start_date_local'].astype('datetime64')
data['start_date_local_year'] = data['start_date_local'].dt.year
data['start_date_local_month'] = data['start_date_local'].dt.month
data['start_date_local_time'] = data['start_date_local'].dt.time
data.loc[data['start_date_local_time'] <= datetime.time(12), 'start_date_local_time_of_day'] = 'Morning'
data.loc[(data['start_date_local_time'] > datetime.time(12)) &
         (data['start_date_local_time'] <= datetime.time(18)), 'start_date_local_time_of_day'] = 'Afternoon'
data.loc[data['start_date_local_time'] > datetime.time(18), 'start_date_local_time_of_day'] = 'Evening'
data.loc[data['distance [miles]'] >= 30, 'distance_description'] = 'Long'
data.loc[(data['distance [miles]'] < 30) & (data['distance [miles]'] >= 20), 'distance_description'] = 'Medium'
data.loc[data['distance [miles]'] < 20, 'distance_description'] = 'Short'

#upload to database
