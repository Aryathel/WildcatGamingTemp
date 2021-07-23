import discord
from discord.ext import commands
import datetime

""" Class | Template

This is a template put in place to be used
when creating a new Cog file.
"""
class New(commands.Cog, name = "New"):
    def __init__(self, bot):
        self.bot = bot
        print(f"{bot.OK} {bot.TIMELOG()} Loaded New Cog.")

    def cog_unload(self):
        print(f"{self.bot.OK} {self.bot.TIMELOG()} Unloaded New Cog.")

    """ Command | Sample

    This is a template for a standard command.
    """
    @commands.guild_only()
    @commands.command(name = "SAMPLE", help = "Just a placeholder.", brief = "If parameters then examples here")
    async def sample(self, ctx):
        pass

    """ Event Listener | On Message

    This is a template for a standard message listener.
    """
    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            pass

""" Function | Setup

The function called by Discord.py when adding another file in a multi-file project.
"""
def setup(bot):
    bot.add_cog(New(bot))
