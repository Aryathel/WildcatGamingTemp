import discord
from discord.ext import commands
import datetime
import uuid
from zipfile import ZipFile
import os
import asyncio

"""Cog | User Tickets

This cog contains commands and functions related to creating
and managing tickets.

NOTE: All commands are restricted to server use only by default,
remove the `@commands.guild_only()` line before any command that
should also be able to be used in a DM.
"""
class Tickets(commands.Cog, name = "Support Tickets"):
    """
    Commands related to creating and managing suport tickets.
    """
    def __init__(self, bot):
        self.bot = bot

        if not 'ticket_backend' in self.bot.data:
            bot.data['ticket_backend'] = {
                "CH_ID": 0,
                "M_ID": 0
            }

        self.bot.data_manager.save_data()

        print(f"{bot.OK} {bot.TIMELOG()} Loaded Ticket Cog.")

    def on_cog_unload(self):
        print(f"{bot.OK} {bot.TIMELOG()} Unloaded Ticket Cog.")

    @commands.guild_only()
    @commands.command(name = "openticket", help = "Create a new support ticket.", brief = "")
    async def open(self, ctx):
        """Command | Ticket Creation

        This command creates a new ticket in the category
        set in the config file.
        """
        await ctx.message.delete()

        if ctx.channel.id == self.bot.ticket_channel_id:
            open_ticket_category = self.bot.get_channel(self.bot.open_ticket_category_id)
            roles = [ctx.guild.get_role(id) for id in self.bot.ticket_roles]
            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            for role in roles:
                overwrites[role] = discord.PermissionOverwrite(read_messages=True)
            if ctx.author.nick:
                name = ctx.author.nick
            else:
                name = ctx.author.name
            channel = await open_ticket_category.create_text_channel(
                name = f"{self.get_alpha(name)}-{uuid.uuid1().fields[0]}",
                reason = f"{ctx.author} Opened a ticket.",
                topic = f"**{self.bot.TIMELOG()}** | {name} Opened a ticket.",
                overwrites = overwrites
            )
            embed = self.bot.embed_util.get_embed(
                title = "Ticket Opened!",
                desc = f"Please see {channel.mention} to continue.",
                author = ctx.author
            )
            m = await ctx.send(embed = embed)
            embed = self.bot.embed_util.get_embed(
                title = "**Welcome to the Support Desk!**",
                desc = f"You're now in direct contact with the {roles[0].mention} team! We're here to help. :smile:\n\n__**Please let us know what the problem we can help you with is in here.**__\n",
                ts = True
            )
            await channel.send(content = f"{ctx.author.mention} {' '.join(r.mention for r in roles)}", embed = embed)
            await asyncio.sleep(30)
            await m.delete()
        else:
            channel = self.bot.get_channel(self.bot.ticket_channel_id)
            embed = self.bot.embed_util.get_embed(
                title = "Wrong Channel",
                desc = f"Please use {channel.mention} to create a ticket.",
                author = ctx.author
            )
            m = await ctx.send(embed = embed)
            await asyncio.sleep(10)
            await m.delete()

    @commands.guild_only()
    @commands.command(name = "closeticket", help = "Close an existing support ticket.", brief = "")
    async def close(self, ctx):
        """Command | Ticket Closing

        This command closes an open ticket and moves it to the
        closed ticket category.
        """
        await ctx.message.delete()

        if ctx.author.nick:
            name = ctx.author.nick
        else:
            name = ctx.author.name

        if ctx.channel.category.id == self.bot.open_ticket_category_id:
            roles = [ctx.guild.get_role(id) for id in self.bot.ticket_roles]
            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=False)
            }
            for role in roles:
                overwrites[role] = discord.PermissionOverwrite(read_messages=True)
            closed_category = self.bot.get_channel(self.bot.closed_ticket_category_id)
            topic = f"{ctx.channel.topic} | **{self.bot.TIMELOG()}** | {name} Closed the ticket."
            await ctx.channel.edit(
                topic = topic,
                reason = f"{ctx.author} Closed a ticket.",
                category = closed_category,
                overwrites = overwrites
            )
            embed = self.bot.embed_util.get_embed(
                title = "Ticket Closed!",
                ts = True,
                author = ctx.author
            )
            await ctx.channel.send(embed = embed)
            embed = self.bot.embed_util.update_embed(
                embed = embed,
                title = "Ticket Closed!",
                desc = f"{ctx.channel.mention}",
                author = ctx.author
            )
            await self.bot.log_channel.send(embed = embed)

    @commands.guild_only()
    @commands.command(name = "ziptickets", aliases = ['archivetickets'], help = "Save all closed ticket channels to a text file, zip the files together and return that zip file, then delete the channels from Discord.", brief = "")
    async def archive(self, ctx):
        """Command | Ticket Cleanup

        This command will read all ticket channels that are closed,
        write their contents to text files, zip those files together,
        send the zip file in Discord, then delete the closed ticket channels.
        """

        closed_ticket_category = self.bot.get_channel(self.bot.closed_ticket_category_id)
        async with ctx.channel.typing():
            print(f"{self.bot.OK} {self.bot.TIMELOG()} Starting closed ticket archive process:")
            files_saved = []
            skip_delete = []
            old_skip = []
            for channel in closed_ticket_category.channels:
                if type(channel) == discord.TextChannel:
                    print(f"{self.bot.OK} {self.bot.TIMELOG()} Saving #{channel} to ./Archive/{channel}.txt.")
                    doc = []
                    doc.append('|'.join(channel.topic.split('|')[3:]))

                    async for message in channel.history(limit = 200):
                        if len(message.attachments) > 0 and not channel in skip_delete:
                            skip_delete.append(channel)
                        if message.content == "Deletion Skipped" and message.author.id == self.bot.user.id:
                            old_skip.append(channel)
                        if not message.author.bot and message.clean_content not in [None, '']:
                            doc.append(f"{(message.created_at + datetime.timedelta(hours=-7)).strftime('[%m/%d/%Y | %I:%M:%S %p]')} {message.author} >>> {message.clean_content}")
                    doc.append('|'.join(channel.topic.split('|')[:3]))
                    doc.reverse()
                    if not channel in old_skip:
                        with open(f"./Archive/{channel}.txt", 'w+', encoding = "utf-8") as file:
                            file.write('\n'.join(doc))
                        files_saved.append(f"./Archive/{channel}.txt")
            print(f"{self.bot.OK} {self.bot.TIMELOG()} Collapsing to Zip file.")
            zip_name = f"./Archive/ticket-archive-{datetime.datetime.now().strftime('%m-%d-%Y_%I-%M-%S-%p')}-{ctx.guild.id}.zip"
            with ZipFile(zip_name, 'w') as zip_file:
                for file in files_saved:
                    zip_file.write(file)
                    os.remove(file)

            fields = []
            fields.append({
                "name": "Archivist",
                "value": ctx.author.mention,
                "inline": True
            })
            fields.append({
                "name": "Channels Archived",
                "value": len(files_saved),
                "inline": False
            })

            embed = self.bot.embed_util.get_embed(
                title = "Archiving Complete!",
                ts = True,
                author = ctx.author,
                fields = fields
            )

            with open(zip_name, 'rb') as file:
                await ctx.send(embed = embed, file = discord.File(file, zip_name.split('/')[-1]))

            if self.bot.delete_archived_tickets:
                for channel in closed_ticket_category.channels:
                    if not channel in old_skip:
                        if not channel in skip_delete:
                            await channel.delete(reason = "Ticket archived.")
                        else:
                            embed = self.bot.embed_util.get_embed(
                                title = "Channel Deletion Skipped",
                                desc = "This channel contains a message with an attachment, so it was not deleted. This channel will need to be manually deleted.",
                                ts = True,
                                author = ctx.author
                            )
                            await channel.send(content = "Deletion Skipped", embed = embed)

        print(f"{self.bot.OK} {self.bot.TIMELOG()} Finished archiving closed tickets.")

    def get_alpha(self, name):
        """Function

        Take in a string and turn it into a valid discord channel name.
        """
        formatted = ""
        for char in name.lower():
            if char.isalpha():
                formatted += char
            elif char in [' ', '_']:
                formatted += '-'
        return formatted

def setup(bot):
    """Setup

    The function called by Discord.py when adding another file in a multi-file project.
    """
    bot.add_cog(Tickets(bot))
