from sklearn import tree
import urllib.request, json

all_station_url = "http://opendata-download-metobs.smhi.se/api/version/1.0/parameter/1/station-set/all/period/latest-hour/data.json"
temperature_url = "http://opendata-download-metobs.smhi.se/api/version/1.0/parameter/1/station/<PLACEHOLDER>/period/latest-months/data.json"
humidity_url = "http://opendata-download-metobs.smhi.se/api/version/1.0/parameter/6/station/<PLACEHOLDER>/period/latest-months/data.json"
air_pressure_url = "http://opendata-download-metobs.smhi.se/api/version/1.0/parameter/9/station/<PLACEHOLDER>/period/latest-months/data.json"

#[temperature, humidity, atmospheric pressure]
X = [[22.5, 59.0, 1013.2],[19.5, 64.0, 1006.0],[17.5, 85.5, 1019.6],
     [21.0, 44.5, 1021.4],[14.5, 75.5, 1015.0],[17.5, 84.0, 1020.4],
     [31.5, 54.5, 1016.0],[14.0, 67.0, 2013.0],[14.5, 68.5, 1010.4]]

Y = ['sunny', 'cloudy', 'rainy',
     'sunny', 'cloudy', 'rainy',
     'sunny', 'cloudy', 'rainy']

def pick_alternative(alternatives):
    index = 1
    for alternative in alternatives:
        print("%s (%d)" % (alternative["name"], index))
        index += 1
    while True:
        pick = input("Please choose alternative from the list above (1-%d): " % (index-1))
        if pick.isdigit() and 1 <= int(pick) < index:
            return alternatives[int(pick)-1]

def get_station_by_name(name):
    stations = []
    with urllib.request.urlopen(all_station_url) as response:
        decoded = response.read().decode(response.headers.get_content_charset())
        data = json.loads(decoded)
        for node in data["station"]:
            if name.lower() in node["name"].lower():
                stations.append(node)
    if len(stations) > 1:
        return pick_alternative(stations)
    elif len(stations) == 0:
        return ""
    else:
        return stations[0]

def guess_weather(temp, humidity, airpressure):
    clf = tree.DecisionTreeClassifier()
    clf = clf.fit(X,Y)
    prediction = clf.predict([[temp, humidity, airpressure]])
    return prediction

def get_data_from_station(station, data_url):
    url = data_url.replace("<PLACEHOLDER>", station["key"])
    try:
        with urllib.request.urlopen(url) as response:
            decoded = response.read().decode(response.headers.get_content_charset())
            data = json.loads(decoded)
            return float(data["value"][-1]["value"])
    except urllib.error.HTTPError:
        return None

def get_temperature_from_station(station):
    return get_data_from_station(station, temperature_url)

def get_humidity_from_station(station):
    return get_data_from_station(station, humidity_url)

def get_airpressure_from_station(station):
    return get_data_from_station(station, air_pressure_url)

station = get_station_by_name(input("Enter name of a SMHI station or your area: "))
if station:
    temp = get_temperature_from_station(station)
    if temp == None:
        print("Could not fetch temperature from station")
        quit()

    humidity = get_humidity_from_station(station)
    if humidity == None:
        print("Could not fetch humidity from station")
        quit()

    airpressure = get_airpressure_from_station(station)
    if airpressure == None:
        print("Could not fetch atmospheric pressure from station")
        quit()

    weather = guess_weather(temp, humidity, airpressure)
    print("Weather in %s is probably %s (%d 'C, %d %%rH, %d hPa)" % (station["name"], weather[0], temp, humidity, airpressure))
else:
    print("No such station found matching given name")
