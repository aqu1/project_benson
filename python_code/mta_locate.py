import numpy as np
from geopy.geocoders import GoogleV3, Nominatim
import re
import pandas as pd
import googlemaps
import requests
import gmaps
import gmaps.datasets
from random import sample


def geolocate(s, api_key):
    geolocator = GoogleV3(api_key=api_key)
    location = geolocator.geocode(s)
    return [location.latitude, location.longitude]
    # heatmaps


def revlocate(search, api_key):
    geolocator = GoogleV3(api_key=api_key)
    location = geolocator.reverse(search)
    print(location.raw)


def zipcode(search, api_key):
    geolocater = Nominatim(user_agent="metis")
    location = geolocater.geocode(search)
    zipcode = re.search(r'\d{5}(?:-\d{4})?(?=\D*$)', location.address).group()
    return zipcode


def geoGoogle(search, key, info='postcode'):
    # Set up your Geocoding url
    geocode_url = "https://maps.googleapis.com/maps/api/geocode/json?address={}".format(search)
    if key is not None:
        geocode_url = geocode_url + "&key={}".format(key)

    # Ping google for the results:
    results = requests.get(geocode_url)
    # Results will be in JSON format - convert to dict using requests functionality
    results = results.json()
    answer = results['results'][0]
    output = {
        "formatted_address": answer.get('formatted_address'),
        "latitude": answer.get('geometry').get('location').get('lat'),
        "longitude": answer.get('geometry').get('location').get('lng'),
        "accuracy": answer.get('geometry').get('location_type'),
        "google_place_id": answer.get("place_id"),
        "type": ",".join(answer.get('types')),
        "postcode": ",".join([x['long_name'] for x in answer.get('address_components')
                              if 'postal_code' in x.get('types')])
    }
    return output[info]


def heatmap(df, key):
    location = []
    for index in df.STATION.sample(n=50, random_state=76).index:
        location.append(tuple([df.STATION[index], df.ENTRIES[index]]))  # replace with lat and long
    # Use google maps api
    gmaps.configure(api_key=key)  # Fill in with your API key
    # Get the dataset
    earthquake_df = gmaps.datasets.load_dataset_as_df('earthquakes')
    # Get the locations from the data set
    locations = earthquake_df[['latitude', 'longitude']]
    # Get the magnitude from the data
    weights = earthquake_df['magnitude']
    # Set up your map
    fig = gmaps.figure()
    fig.add_layer(gmaps.heatmap_layer(locations, weights=weights))
    return fig, locations, weights


def df_locate(df, key):
    stations = []
    lats = []
    longs = []
    for entry in df:
        print(entry)
        stations.append(entry)
        lats.append(geoGoogle(entry, key, info='latitude'))
        longs.append(geoGoogle(entry, key, info='longitude'))
    d = {'stationline': stations, 'latitude': lats, 'longitude': longs}
    locate_df = pd.DataFrame(d)
    return locate_df


def main():
    key = 'AIzaSyCxLwaGqiRunNaJ0Uvt93GH_RVd-S-2hIw'
    turnstile_df = pd.read_csv('mta-3months.txt', low_memory=False)
    turnstile_df = turnstile_df\
        .assign(stationline=turnstile_df.STATION.astype(str) + ' ' + turnstile_df.LINENAME.astype(str) + ' station NYC')

    subways = ['14 ST-UNION SQ LNQR456W station NYC']
    for subway in subways:
        print(geoGoogle(subway, key, info='latitude'))
    stations = sorted(list(set(turnstile_df.stationline)))
    # station_locate = df_locate(stations, key)
    # station_locate.to_csv('station_locations.csv')
    # faster to do each unique value and map?  faster to do per unique station then merge.


if __name__ == '__main__':
    main()
