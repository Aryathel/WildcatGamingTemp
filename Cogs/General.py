import discord
from discord.ext import commands, menus
import datetime
from math import trunc
import unicodedata

"""General Commands

This Cog contains a list of commands that almost every program
utilizes.

NOTE: All commands are restricted to server use only by default,
remove the `@commands.guild_only()` line before any command that
should also be able to be used in a DM.
"""
class General(commands.Cog, name = "General"):
    """A general set of commands."""
    def __init__(self, bot):
        self.bot = bot
        print(f"{bot.OK} {bot.TIMELOG()} Loaded General Cog.")

    """ Method | Cog Unload

    Called when the cog is unloaded from the system.
    """
    def cog_unload(self):
        print(f"{self.bot.OK} {self.bot.TIMELOG()} Unloaded General Cog.")

    @commands.guild_only()
    @commands.command(name='uptime', help = 'Returns the amount of time the bot has been online.')
    async def uptime(self, ctx):
        """Get Bot Uptime

        As the name implies... this returns the amount of time the
        bot has been online, given that the `bot.start_time` value
        was set in `main.py` in the `on_ready` function.
        """
        if self.bot.delete_commands:
            await ctx.message.delete()

        # Some basic calculations to determine individual time amounts
        seconds = trunc((self.bot.embed_ts() - self.bot.start_time).total_seconds())
        hours = trunc(seconds / 3600)
        seconds = trunc(seconds - (hours * 3600))
        minutes = trunc(seconds / 60)
        seconds = trunc(seconds - (minutes * 60))

        embed = self.bot.embed_util.get_embed(
            title = f":alarm_clock: {self.bot.user.name} Uptime",
            desc = f"{hours} Hours\n{minutes} Minutes\n{seconds} Seconds",
            ts = True,
            author = ctx.author
        )
        await ctx.send(embed = embed)

    @commands.guild_only()
    @commands.command(name='ping', aliases=['pong'], help = 'Gets the current latency of the bot.')
    async def ping(self, ctx):
        """Get Bot Ping

        Returns two values, the ping of the Discord bot to the API,
        and the ping time it takes from when the original message is sent
        to when the bot successfully posts its response.
        """
        if self.bot.delete_commands:
            await ctx.message.delete()

        embed = self.bot.embed_util.get_embed(
            title = ":ping_pong: Pong!",
            desc = "Calculating ping time...",
            author = ctx.author
        )
        m = await ctx.send(embed = embed)

        embed = self.bot.embed_util.update_embed(
            embed = embed,
            desc = "Message latency is {} ms\nDiscord API Latency is {} ms".format(
                trunc((m.created_at - ctx.message.created_at).total_seconds() * 1000),
                trunc(self.bot.latency * 1000)
            )
        )
        await m.edit(embed = embed)

    @commands.command(name = 'charinfo', aliases = ['char'], help = 'Gets information on a provided character, best used with a default emoji.', brief = ":regional_indicator_a:")
    async def charinfo(self, ctx, *, characters: str):
        def to_string(c):
            digit = f'{ord(c):x}'
            name = unicodedata.name(c, 'Name not found.')
            return f'`\\U{digit:>08}`: {name} - {c} \N{EM DASH} <http://www.fileformat.info/info/unicode/char/{digit}>'
        msg = '\n'.join(map(to_string, characters))
        if len(msg) > 2000:
            return await ctx.send(embed = self.bot.embed_util.get_embed(desc = 'Output too long to display.'))
        embed = self.bot.embed_util.get_embed(
            title = "Character Info",
            desc = msg
        )
        await ctx.send(embed = embed)

    @commands.command(name = "hexconvert", help = "Converts a hexadecimal color code to decimal numer format.", brief = "#EB1D24")
    async def hexconvert(self, ctx, hex):
        hex = hex.strip().replace('#', '')
        embed = self.bot.embed_util.get_embed(
            title = "Hex Color Converted",
            desc = f"Hex: `{hex}`\nDec: `{int(hex, 16)}`",
            color = int(hex, 16)
        )
        await ctx.send(embed = embed)

    """DISABLED - this command really didn't see much use or value, so I am just leaving it out for now.
    @commands.guild_only()
    @commands.command(name='invite', help = 'Returns the server invite link.', brief = "")
    async def invite(self, ctx):
        ""Command | Get Server Invite

        Returns an invite to the server. Disabled by default,
        this is enabled if the server the bot is used in is meant to be public.
        ""
        if self.bot.delete_commands:
            await ctx.message.delete()

        print(ctx.guild.features)
        if 'VANITY_URL' in ctx.guild.features:
            invite = await ctx.guild.vanity_invite()
        else:
            invite = await ctx.guild.create_invite(unique = False)


        embed = self.bot.embed_util.get_embed(
            title = "Invite Link",
            desc = invite.url,
            author = ctx.author
        )
        await ctx.send(embed = embed)
    """

def setup(bot):
    """Setup

    The function called by Discord.py when adding another file in a multi-file project.
    """
    bot.add_cog(General(bot))
