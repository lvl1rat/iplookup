import requests
import os
from terminaltables import SingleTable
from datetime import datetime
import pytz
import sys


def getLocalCurrency(country_code):
    # A simple mapping of country codes to currencies
    country_currency_map = {
        "US": "USD",
        "GB": "GBP",
        "CA": "CAD",
        "JP": "JPY",
        "IN": "INR",
        "DE": "EUR",
        "FR": "EUR",
        # Add more mappings as needed...
    }
    return country_currency_map.get(country_code, "Unknown Currency")

def getLocalTime(data):
    timezone = data['timezone']
    utc_time = datetime.now().replace(tzinfo=pytz.utc)
    local_timezone = pytz.timezone(timezone)
    local_time = utc_time.astimezone(local_timezone)

    formatted_time = local_time.strftime('%H:%M:%S')
    return formatted_time

def dataTable(data):
    table_data = [[f"City: {data['city']}", f"Region: {data['regionName']} ({data['region']})", f"Country: {data['country']} ({data['countryCode']})"],
        [f"Zip Code: {data['zip']}", f"Latitude: {data['lat']}", f"Longitude: {data['lon']}"],
        [f"Time Zone: {data['timezone']}", f"Time: {getLocalTime(data)}", f"Currency: {getLocalCurrency(data['countryCode'])}"]
        ]
    table_instance = SingleTable(table_data, " Status: Success ")
    table_instance.inner_heading_row_border = False
    table_instance.inner_row_border = True
    table_instance.justify_columns = {0: 'center', 1: 'center', 2: 'center'}
    return ("\n"+table_instance.table)

def lowerDataTabel(data):
    table_data = [
        [f"Organization: {data['org']} as {data['as']}"]
    ]    
    table_instance = SingleTable(table_data, f" ISP: {data['isp']} ")
    table_instance.inner_heading_row_border = False
    table_instance.inner_row_border = True
    table_instance.justify_columns = {0: 'center', 1: 'center', 2: 'center'}
    return (""+table_instance.table)

def checkApiFiles():
    if not os.path.exists('auth'):
        os.makedirs('auth')

    file_path = "auth/hash.txt"

    with open(file_path, "a+") as file:
        # Move the file pointer to the beginning to read the content
        file.seek(0)
        api_key = file.readline().strip()

        if api_key == "":
            user_input = input("Enter NASA API key for LandSat Imagery [ENTER to skip]\n(https://api.nasa.gov/)\n\n─────| ")

            if user_input:
                file.write(user_input + "\n")
                api_key = user_input
    return api_key

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():

    clear()
    print(f"\n───────IP LookUp───────")
    
    api_key = checkApiFiles()
    if len(sys.argv) < 2:
        query = input("\nIP Query (IPv4/IPv6):\n\n─────| ")
    else:
        query = sys.argv[1]
        print("\nIP Query (IPv4/IPv6):\n\n─────| " + query)
    url = f"http://ip-api.com/json/{query}"

    try:
        response = requests.get(url) 
        data = response.json()
        if data['status'] == 'success':

            print(dataTable(data) + "\n")
            print(lowerDataTabel(data) + "\n")
            print(f"┌ Open Street Map ──────┐")
            osm_url = f"https://www.openstreetmap.org/?mlat={data['lat']}&mlon={data['lon']}#map=16/{data['lat']}/{data['lon']}"
            print(osm_url)
            print(f"└───────────────────────┘\n")

            if api_key:
                #24.48.0.1
                print(f"┌ LandSat Image ────────┐")
                geo_url = f" https://api.nasa.gov/planetary/earth/assets?lon={data['lon']}&lat={data['lat']}&&dim=0.050&api_key={api_key}"
                geo_response = requests.get(geo_url)
                geo_data = geo_response.json()
                print(geo_data['url'])
            print(f"└───────────────────────┘\n")
        else:
            print(f"\n┌ Status: Fail ─────────┐\n",
                f"Message: {data['message']} \"{data['query']}\"")
            print(f"└───────────────────────┘\n")
    except requests.ConnectionError as e:
        print(e)

if __name__ == '__main__':
    main()