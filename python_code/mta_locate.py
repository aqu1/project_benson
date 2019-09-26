import pandas as pd
import requests


def geoGoogle(search, key, infolist):
    """Function to receive and address' geocode data from Google Maps."""
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
    return [output[info] for info in infolist]


def df_locate(addresses, key):
    """Function to iterate over a set of addresses using geoGoogle function."""
    stations = []
    coord = []
    bors = []
    for address in addresses:
        stations.append(address)
        coord.append(geoGoogle(address, key, ['latitude', 'longitude']))
        # bors.append(geoGoogle(entry, key, info='formatted_address').split(',')[1])
        """use the 'formatted_address' attribute of geoGoogle output for search for borough substrings
        maybe use regex, wasn't sure here"""
    d = {'stationline': stations, 'Latitude': list(zip(*coord))[0], 'Longitude': list(zip(*coord))[1]}
    locate_df = pd.DataFrame(d)
    return locate_df


def process_mta(csv, key):
    """Function to process MTA turnstile dataset using the df_locate function.  Creates a location dataframe that is
    then merged with the original input dataframe."""
    turnstile_df = pd.read_csv(csv, low_memory=False)
    print('CSV imported')
    turnstile_df.LINENAME = turnstile_df.LINENAME.str \
        .strip('W') \
        .replace('LNQR456', '456LNQR') \
        .replace('ABCD1', '1ABCD') \
        .replace('FLM123', '123FLM') \
        .replace('BDNQR2345', '2345BDNQR') \
        .replace('R2345', '2345R') \
        .replace('ACJZ2345', '2345ACJZ') \
        .replace('ACENQRS1237', '1237ACENQRS')
    turnstile_df = turnstile_df \
        .assign(stationline=turnstile_df.STATION.astype(str) + ' ' + turnstile_df.LINENAME.astype(str) + ' station NYC')
    print('DF strings prepped')
    stations = sorted(list(set(turnstile_df.stationline)))
    print('Start location calculations')
    location_df = df_locate(stations, key)
    print('Location calculations successful')
    location_df = location_df.assign(LINENAME=location_df.stationline.apply(lambda x: ''.join(x.split()[2])))
    location_df.stationline = location_df.stationline.apply(lambda x: ' '.join(x.split()[:-3]))
    location_df.rename(columns={'stationline': 'STATION'}, inplace=True)
    final_df = pd.merge(turnstile_df, location_df, left_on=['STATION', 'LINENAME'], right_on=['STATION', 'LINENAME'])
    final_df.drop(['Unnamed: 0'], axis=1, inplace=True)
    print('DF processed and merged')
    return final_df


def main():
    """essential variables here"""
    key = 'AIzaSyCxLwaGqiRunNaJ0Uvt93GH_RVd-S-2hIw'
    csv = '../data/turnstiles_daily_filtered.csv'
    outcsv = 'brooklyn_turnstiles.csv'

    """execute functions"""
    final_df = process_mta(csv, key)
    final_df.to_csv(outcsv)


if __name__ == '__main__':
    main()
