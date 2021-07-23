import json
import os

import tweepy

class TwitterListener(tweepy.StreamListener):
    def on_status(self, status):
        print(status._json)

if __name__ == "__main__":
    twitter_consumer_key = os.getenv("MSI_TWITTER_KEY")
    twitter_consumer_secret = os.getenv("MSI_TWITTER_SECRET")
    twitter_auth = tweepy.AppAuthHandler(twitter_consumer_key, twitter_consumer_secret)
    twitter_api = tweepy.API(twitter_auth)

    print(json.dumps(twitter_api.get_user('1344439285718470656')._json, indent = 2))

    # Creating the instance of the stream listener.
    stream_listener = tweepy.Stream(
        auth = twitter_api.auth,
        listener = TwitterListener()
    )
    # Starting the stream listener to follow specified channels.
    stream_listener.filter(follow=['1344439285718470656'])
