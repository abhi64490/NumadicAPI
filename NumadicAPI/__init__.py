"""
The flask application package.
"""

import pandas as pd
import glob
from flask import Flask
import math

csv_files = glob.glob(f'EOLdump/*.csv')
all_data = []

#To create response data
dfResponse=pd.DataFrame(columns=["License_plate", "distance", "NumberOfTrips", "AverageSpeed","TransporterName","SpeedVoilationCount"])

for file in csv_files:

    df = pd.read_csv(file)
    all_data.append(df)
    df = pd.concat(all_data, ignore_index=True)

df_trip=pd.read_csv(r'C:\Users\abhi_\source\repos\NumadicAPI\NumadicAPI\TripInfo.csv')


app = Flask(__name__)

@app.route('/call_report', methods=['GET'])
def call_report():
    # Get start time and end time from query parameters
    start_time_epoch = request.json['start_time']
    end_time_epoch = request.json['end_time']
    if start_time_epoch in df_trip['date_time']:
        data=generate_report(start_time_epoch,end_time_epoch)
        dfResponsedata = dfResponse.append(data, ignore_index=True)
        #Save to xlsx file
        file_path = 'asset_report.xlsx'
        dfResponsedata.to_excel(file_path, index=False)
        return dfResponsedata
    else:
        return 'invalid request'

    




def generate_report(start_time_epochs,end_time_epochs):

    # Retrieve start and end time from the request
    start_time_epoch = start_time_epochs
    end_time_epoch = end_time_epochs

    # Convert epoch timestamps to datetime objects
    start_datetime = datetime.fromtimestamp(start_time_epoch)
    end_datetime = datetime.fromtimestamp(end_time_epoch)
    
    # Filter the data based on the specified time range

    #License_plate
    License_plate=df_trip[df_trip['date_time'] == start_time_epoch]['vehicle_number']

    lat1=df[df['tis'] == start_time_epoch]['lat']
    lon1=df[df['tis'] == start_time_epoch]['lon']

    lat2=df[df['tis'] == end_time_epoch]['lat']
    lon2=df[df['tis'] == end_time_epoch]['lon']
    

    #distance
    distance=haversine(lat1, lon1, lat2, lon2)

    #NumberOfTrips
    NumberOfTrips=df_trip[df_trip['vehicle_number'] == License_plate]['trip_id'].value_counts()

    #AverageSpeed
    hours_difference = (end_datetime - start_datetime).total_seconds() / 3600
    Speed=distance/hours_difference

    #Transportername
    TransporterName=df_trip[df_trip['vehicle_number'] == License_plate]['transporter_name']

    #NumberOfVoilation
    SpeedVoilationCount=len(df[(df['vehicle_number'] == License_plate) & (df['osf'] == True)])

    #creating dataframe
    data = {
    "License_plate":  License_plate,
    "distance": distance,
    "NumberOfTrips": NumberOfTrips,
    "AverageSpeed": Speed,
    "TransporterName": TransporterName,
    "SpeedVoilationCount": SpeedVoilationCount
    }

    return data



#Calculate distance from lat and lon
def haversine(lat1, lon1, lat2, lon2):
   
    # Convert latitude and longitude to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = math.sin(dlat/2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = 6371 * c  # Earth's radius in kilometers
    
    return distance

if __name__ == '__main__':
    app.run()