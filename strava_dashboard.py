import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import requests
import datetime
import plotly_express as px
import polyline

def get_new_token():
    access_token = requests.post(str(r'https://www.strava.com/oauth/token?client_id=42399&client_secret=750191abe2d99529b503cbfe70b86ad8f3d8ae70&refresh_token=4053c255fe9432ade612c43f4bf83f59f3153316&grant_type=refresh_token'))
    access_token = access_token.json()
    access_token = access_token['access_token']
    return access_token


def convert_to_imperial(activities):
    kph_to_mph = 2.23694
    meters_to_feet = 3.28084
    km_to_miles = 0.621371
    activities['average_speed [mph]'] = activities['average_speed'] * kph_to_mph
    activities['average_temp [F]'] = (activities['average_temp'] * 1.8) + 32
    activities['distance [miles]'] = (activities['distance'] / 1000) * km_to_miles
    activities['elev_high [ft]'] = activities['elev_high'] * meters_to_feet
    activities['elev_low [ft]'] = activities['elev_low'] * meters_to_feet
    activities['max_speed [mph]'] = activities['max_speed'] * kph_to_mph
    activities['total_elevation_gain [ft]'] = activities['total_elevation_gain'] * meters_to_feet
    return activities

# Initialize the activitiesframe
activities = pd.DataFrame()

url = "https://www.strava.com/api/v3/athlete/activities"

access_token = get_new_token()

page = 1

while True:
    # get page of activities from Strava
    r = pd.read_json(str(url + '?access_token=' + access_token + '&per_page=100' + '&page=' + str(page)))

    # if no results then exit loop
    if r.empty:
        break
    else:
        activities = activities.append(r, sort=True)

    # increment page
    page += 1

gear_dict = {'b6284755': 'Canyon Endurace CF SL 7.0',
             'b6004319': 'Giant AnyRoad 2'}

# Clean activities
activities['gear_id'] = activities['gear_id'].replace(gear_dict)

# Convert to imperial units
activities = convert_to_imperial(activities)

# Modify and Seperate time activities
activities['start_date_local'] = activities['start_date_local'].astype('datetime64')
activities['start_date_local_year'] = activities['start_date_local'].dt.year
activities['start_date_local_month'] = activities['start_date_local'].dt.month
activities['start_date_local_time'] = activities['start_date_local'].dt.time
activities.loc[activities['start_date_local_time'] <= datetime.time(12), 'start_date_local_time_of_day'] = 'Morning'
activities.loc[(activities['start_date_local_time'] > datetime.time(12)) &
         (activities['start_date_local_time'] <= datetime.time(18)), 'start_date_local_time_of_day'] = 'Afternoon'
activities.loc[activities['start_date_local_time'] > datetime.time(18), 'start_date_local_time_of_day'] = 'Evening'
activities.loc[activities['distance [miles]'] >= 30, 'distance_description'] = 'Long'
activities.loc[(activities['distance [miles]'] < 30) & (activities['distance [miles]'] >= 20), 'distance_description'] = 'Medium'
activities.loc[activities['distance [miles]'] < 20, 'distance_description'] = 'Short'

activities = activities[activities['type'] == 'Ride']

message = activities["type"] + "<br>"
message += "Distance [Miles]: " + round(activities["distance [miles]"], 1).astype(str) + "<br>"
message += "Average Speed [mph]: " + round(activities["average_speed [mph]"], 1).astype(str) + "<br>"
message += "Power [W]: " + round(activities["average_watts"], 1).astype(str) + "<br>"
message += "Date: " + activities["start_date_local"].astype(str)
activities["text"] = message

rows = []
for values in activities['map']:
    rows.append(values['summary_polyline'])

activities['summary_polyline'] = rows

i = 0

fig = go.Figure()

for summary_polyline in activities['summary_polyline']:
    try:
        coordinates = polyline.decode(summary_polyline)

        ride_longitudes = [coordinate[1] for coordinate in coordinates]
        ride_latitudes = [coordinate[0] for coordinate in coordinates]

        if i == len(activities['summary_polyline']):
            current_fig = px.line_mapbox(
                lon=ride_longitudes,
                lat=ride_latitudes,
            )
        else:
            current_fig = px.line_mapbox(
                lon=ride_longitudes,
                lat=ride_latitudes,
            )
        fig.add_trace(current_fig.data[0])
        i += 1
    except TypeError:
        i += 1
        pass

fig.update_layout(mapbox_style="open-street-map",
                  mapbox=dict(
                      center=dict(
                        lat=45.5051,
                        lon=-122.6750,
                      ),
                      zoom=8
                  ))
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

fig.show()