import pandas as pd
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from geopy.geocoders import Nominatim
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException

geolocator = Nominatim(user_agent="aNewHope", timeout=10)
countries = pd.read_csv('countries.csv', index_col='name')

def addGeoData(df):
    try:
        df['location'], df['lat'], df['long'] = zip(*df['raw_location'].map(getLocation))
    except GeocoderTimedOut as e:
        print("Error: GeocoderTimedOut")
    except GeocoderUnavailable as e:
        print("Error: GeocoderUnavailable")
    df = df.dropna(subset=['location'])
    try:
        df['country'] = df['location'].apply(getCountry)
        df['code'] = df['country'].apply(getCode)
    except KeyError:
        pass
    try:
        df['language'] = df.text.apply(detect)
    except LangDetectException:
        pass
    return df

def getLocation(raw_location):
    location = geolocator.geocode(raw_location, language='en')
    if location != None:
        lat = location.latitude
        longitude = location.longitude
    else:
        lat = None
        longitude = None
    return location, lat, longitude

def getCountry(location):
    candidate = str(location).split(', ')[-1]
    # A veces el último item es el país, a veces las coordenadas. Usar atributos de location?
    if candidate[0] in '(-0123456789':
        candidate = str(location).split(', ')[-3]
    return candidate

def getCode(country):
    return countries.loc[country]['alpha-3']