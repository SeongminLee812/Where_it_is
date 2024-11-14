from fastapi import FastAPI, UploadFile, File, HTTPException
import pandas as pd
import re
from io import BytesIO
import requests
import json
import os
from urllib.parse import quote
from datetime import datetime, timedelta

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

def transit_route(origin, destination):
    origin, destination = quote(origin), quote(destination)
    # Google Maps Directions API endpoint
    endpoint = "https://maps.googleapis.com/maps/api/directions/json?"
    nav_request = 'origin={}&destination={}&mode=transit&key={}'.format(origin, destination, GOOGLE_MAPS_API_KEY)
    request_url = endpoint + nav_request  # Full URL with endpoint and parameters

    # Sends the request and reads the response.
    response = requests.get(request_url)
    
    # Check if response is successful
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to retrieve data", "status_code": response.status_code}


def parsing(directions):
    '''
    Inputs: the api result
    Outputs: total travel time and location of nearby station
    '''
    if directions['status'] == 'OK':
        # unit is seconds
        total_tt = directions['routes'][0]['legs'][0]['duration']['value']
        steps = directions['routes'][0]['legs'][0]['steps']
        mode_list = [i['travel_mode'] for i in steps]
        tt_list = [i['duration']['value'] for i in steps]
        if 'TRANSIT' in mode_list:
            s = mode_list.index('TRANSIT')
            station_loc = steps[s]['transit_details']['departure_stop']['location']
        else:
            station_loc = None
        return total_tt, station_loc, mode_list, tt_list
    else: # if api call is not valid, return None
        return None, None, None, None


app = FastAPI()

def extract_key_data(file):
    # Read the uploaded file into BytesIO for compatibility
    file_bytes = BytesIO(file.read())
    df = pd.read_excel(file_bytes, header=None)

    # Step 1: Locate the row containing '주소' keyword to set as header
    address_column_index = None
    header_row_index = None
    for row_index, row in df.iterrows():
        for col_index, cell_value in row.items():
            if isinstance(cell_value, str) and re.search(r"주소", cell_value):
                address_column_index = col_index
                header_row_index = row_index
                break
        if address_column_index is not None:
            break

    # If no '주소' column is found, return an error
    if address_column_index is None:
        raise ValueError("파일에 '주소'와 관련된 컬럼이 없습니다.")

    # Step 2: Reload data with identified header row
    file_bytes.seek(0)  # Reset the file pointer to the beginning
    df = pd.read_excel(file_bytes, header=header_row_index)

    # Step 3: Select key columns - Address, 임대보증금, 임대료, etc.
    key_columns = [col for col in df.columns if re.search(r"(주소|임대보증금|임대료)", str(col))]

    # Filter the DataFrame to keep only relevant columns
    filtered_df = df[key_columns].dropna(how="all")

    return filtered_df.to_dict(orient="records")

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        key_data = extract_key_data(file.file)
        return {"data": key_data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/get_route/"):
async def get_route(origin, destination):
    try:
        directions = transit_route(origin, destination)
        parsed = parsing(directions)
        return {"data": parsed}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

