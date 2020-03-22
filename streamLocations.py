import sys
import tweepy
import urllib3
import http
import requests
import logging
import string
import time
import pandas as pd
from geo import *
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('query', help='Escribí los términos de búsqueda sin espacios')
args = parser.parse_args()
query = args.query.split(',')
print(query)

#Twitter API credentials
consumerKey = ""
consumerSecret = ""
accessToken = ""
accessTokenSecret = ""

auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
auth.set_access_token(accessToken, accessTokenSecret)
api = tweepy.API(auth,
                 retry_count = 5, # retry 5 times
                 retry_delay = 5, # seconds to wait for retry
                 wait_on_rate_limit=True,
                 wait_on_rate_limit_notify=True)

count = 1
df = pd.read_csv('myLocations.csv')

class MyStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        global count, df
        try:
            if status.user.location:
                count+=1
                row = pd.DataFrame({'text': [status.text],
                               'raw_location': [status.user.location],
                })
                df = df.append(row, ignore_index = True)
                    
            if count%10==0:
                dfWithLocations = df[-df['location'].isnull()]
                dfToGeocode = df[df['location'].isnull()]
                if len(dfToGeocode)>0:
                    dfToGeocode = addGeoData(dfToGeocode)
                    df = pd.concat([dfWithLocations, dfToGeocode])
                df.to_csv('myLocations.csv', index=False)

        except (http.client.IncompleteRead) as e:
            logging.warning('http.client.IncompleteRead')
        except urllib3.exceptions.ProtocolError as error:
            logging.warning('urllib3.exceptions.ProtocolError')
        except urllib3.exceptions.ReadTimeoutError as error:
            logging.warning('urllib3.exceptions.ReadTimeoutError')
        except ConnectionResetError as error:
            logging.warning('ConnectionResetError')
        except ConnectionError as error:
            logging.warning('ConnectionError')
        except requests.exceptions.ConnectionError as error:
            logging.warning('requests.exceptions.ConnectionError')

    def on_error(self, status_code):
        print >> sys.stderr, 'Encountered error with status code:', status_code
        return True # Don't kill the stream

    def on_timeout(self):
        print >> sys.stderr, 'Timeout...'
        return True # Don't kill the stream

    def on_exception(self, exception):
        print(exception)
        return True

myStreamListener = MyStreamListener()
myStream = tweepy.Stream(auth = api.auth, listener=myStreamListener)
while True:
    try:
        myStream.filter(track=query, stall_warnings=True)
    except (urllib3.exceptions.ProtocolError, AttributeError):
        continue
