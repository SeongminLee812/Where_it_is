import requests, json
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

origin = "서울특별시 강동구 상암로27길 19 삼화에코빌1차 제101동 (천호동 228-1)"
destination = "매헌로16길 32"
directions = transit_route(origin, destination)

# Print the directions to verify
# print(json.dumps(directions, indent=4, ensure_ascii=False))


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

print(parsing(directions))