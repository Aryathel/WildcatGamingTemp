import asyncio
import json
import os

import discord
from discord.ext import commands
import datetime
import tweepy.asynchronous as tweepy

""" Class | Twitter Stream Listener

This class handles all twitter posts from teh subscribed channels.
"""
class TwitterListener(tweepy.AsyncStream):
    """ Method | Init

    The setup for the stream handler.
    """
    def __init__(self, bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot


    """ Method | On Connect

    This method is called once a successfull response is received from the Twitter server.
    """
    async def on_connect(self):
        print(f"{self.bot.OK} {self.bot.TIMELOG()} Twitter Listener Connected")


    """ Method | On Disconnect

    This method id called when the Stream is disconnected.
    """
    async def on_disconnect(self):
        print(f"{self.bot.WARN} {self.bot.TIMELOG()} Twitter Listener Disconnected")


    """ Method | On New Tweet

    This method is called whenever a followed user on Twitter posts a new tweet.
    """
    async def on_status(self, status):
        # Make sure the bot is online fully before handling a tweet
        await self.bot.wait_until_ready()

        msg = status._json

        # Send the tweet to the registered twitter channel.
        channel = self.bot.get_channel(self.bot.data['logs']['twitter'])
        if msg['user']['id'] == 24967749:
            await channel.send(f"New Tweet from {msg['user']['name']}!\nhttps://twitter.com/{msg['user']['screen_name']}/status/{msg['id_str']}")


    """ Method | On Exception

    This method is called whenever an unhandled exception occurs.
    """
    async def on_exception(self, exception):
        print(f"{self.bot.ERR} {self.bot.TIMELOG()} Twitter Streaming Error:")
        print(f"{' '*35} {exception}")


    """ Method | On Error

    This method handles all error status codes that are received from the stream.
    """
    async def on_http_error(self, status_code):
        if status_code == 420:
            print(f"{self.bot.ERR} {self.bot.TIMELOG()} Twitter Error Code Received:")
            print(f"{' '*35} Code: {status_code}")
            print(f"{' '*35} Handle: Stop Listener")
            return False
        else:
            print(f"{self.bot.WARN} {self.bot.TIMELOG()} Twitter Error Code Received:")
            print(f"{' '*35} Code: {status_code}")
            print(f"{' '*35} Handle: Ignore Status")
            return True

""" Class | Twitter

This cog is used to handle subscribing to twitter users, and post new tweets from those users.
"""
class Twitter(commands.Cog, name = "Twitter"):
    """ Method | Init

    Initializes the Twitter cog, creating the stream listener instance.
    """
    def __init__(self, bot):
        self.bot = bot

        # Using the registered API key to connect to Twitter.
        self.twitter_consumer_key = os.getenv("MSI_TWIT_CUST_KEY")
        self.twitter_consumer_secret = os.getenv("MSI_TWIT_CUST_SECRET")
        self.twitter_access_token = os.getenv("MSI_TWIT_ACS_TOKEN")
        self.twitter_access_token_secret = os.getenv("MSI_TWIT_ACS_TOKEN_SECRET")

        # Creating the instance of the stream listener.
        self.listener = TwitterListener(
            self.bot,
            self.twitter_consumer_key,
            self.twitter_consumer_secret,
            self.twitter_access_token,
            self.twitter_access_token_secret
        )

        self.bot.loop.create_task(self.listener.filter(follow=['24967749']))

        print(f"{bot.OK} {bot.TIMELOG()} Loaded Twitter Cog.")


    """ Method | Cog Unload

    Called when the cog is unloaded from the system.
    """
    def cog_unload(self):
        self.listener.disconnect()
        print(f"{self.bot.OK} {self.bot.TIMELOG()} Unloaded Twitter Cog.")


""" Function | Setup

The function called by Discord.py when adding another file in a multi-file project.
"""
def setup(bot):
    bot.add_cog(Twitter(bot))
