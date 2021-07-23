"""Resource | Utility Fcuntions

This file hosts classes/functions which are used regularly throughout
the program. More details provided for each.
"""
import re

import discord
from discord.ext import menus
import datetime

class EmbedUtil:
    def __init__(self, bot):
        self.embed_color = bot.embed_color
        self.footer = bot.footer
        self.footer_image = bot.footer_image
        self.timestamp = bot.embed_ts
        self.show_author = bot.show_command_author

    def get_embed(self, title=None, desc=None, fields=None, ts=False,
                  author=None, thumbnail=None, image=None, footer=None,
                  footer_image=None, url=None, color=None):
        """Function | Create Embedded Message

        This function reads the default embed settings from the bot
        attributes, then creates an embedded message to the specifications
        of the input.
        """
        embed = discord.Embed(
            color=self.embed_color if not color else color
        )
        if title:
            embed.title = title
        if desc:
            embed.description = desc
        if url:
            embed.url = url
        if not footer == False:
            embed.set_footer(
                text=self.footer if not footer else footer,
                icon_url=self.footer_image if not footer_image else footer_image
            )
        if ts:
            embed.timestamp = self.timestamp()
        if author:
            if type(author) == dict:
                if 'icon_url' in author and author['icon_url']:
                    embed.set_author(
                        name=author['name'],
                        icon_url=author['icon_url']
                    )
                else:
                    embed.set_author(
                        name=author['name']
                    )
            else:
                embed.set_author(
                    name=author.name,
                    icon_url=author.avatar_url
                )

        if fields:
            for field in fields:
                embed.add_field(
                    name=field['name'],
                    value=field['value'],
                    inline=field['inline'] if 'inline' in field.keys() else True
                )
        if thumbnail:
            embed.set_thumbnail(
                url=thumbnail
            )
        if image:
            embed.set_image(
                url=image
            )
        return embed

    def update_embed(self, embed, title = None, desc = None, fields = None, ts = False,
                    author = None, thumbnail = None, image = None, footer = None,
                    footer_image = None):
        """Function | Modify Embedded Message

        This function takes in an embedded message and modifies it
        based on inputs.
        """
        if title:
            embed.title = title
        if desc:
            embed.description = desc
        if ts == True:
            embed.timestamp = self.timestamp()
        if author:
            if type(author) == dict:
                if 'icon_url' in author and author['icon_url']:
                    embed.set_author(
                        name = author['name'],
                        icon_url = author['icon_url']
                    )
                else:
                    embed.set_author(
                        name = author['name']
                    )
            else:
                embed.set_author(
                    name = author.name,
                    icon_url = author.avatar_url
                )
        if fields:
            embed.clear_fields()
            for field in fields:
                embed.add_field(
                    name = field['name'],
                    value = field['value'],
                    inline = field['inline'] if 'inline' in field.keys() else True
                )
        if thumbnail:
            embed.set_thumbnail(
                url = thumbnail
            )
        if image:
            embed.set_image(
                url = image
            )
        embed.set_footer(
            text = embed.footer.text if not footer else footer,
            icon_url = embed.footer.icon_url if not footer_image else footer_image
        )
        return embed

class Confirmation(menus.Menu):
    def __init__(self, title = None, msg = None, url = None):
        super().__init__(timeout = 30.0, delete_message_after = True)
        self.msg = msg
        self.title = title
        self.url = None
        self.result = None

    async def send_initial_message(self, ctx, channel):
        embed = ctx.bot.embed_util.get_embed(
            title = self.title,
            desc = self.msg,
            url = self.url
        )
        return await channel.send(embed = embed)

    @menus.button('\N{WHITE HEAVY CHECK MARK}')
    async def do_confirm(self, payload):
        self.result = True
        self.stop()

    @menus.button('\N{CROSS MARK}')
    async def do_deny(self, payload):
        self.result = False
        self.stop()

    async def prompt(self, ctx):
        await self.start(ctx, wait = True)
        return self.result

class TimeLength:
    def __init__(self, string):
        self.time_pattern = re.compile("((?P<days>\d+)+d)?((?P<hours>\d+)+h)?((?P<minutes>\d+)+m)?((?P<seconds>\d+)+s)?", re.IGNORECASE)

        self.days = 0
        self.hours = 0
        self.minutes = 0
        self.seconds = 0

        self.parse_time(string)

    def parse_time(self, string):
        m = self.time_pattern.match(string)

        self.days = int(m.group("days")) if m.group("days") is not None else 0
        self.hours = int(m.group("hours")) if m.group("hours") is not None else 0
        self.minutes = int(m.group("minutes")) if m.group("minutes") is not None else 0
        self.seconds = int(m.group("minutes")) if m.group("minutes") is not None else 0
