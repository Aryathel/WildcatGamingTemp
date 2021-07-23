import asyncio

import discord
from discord.ext import commands
import datetime

from Resources.Menus import MenuListSource, MenuListSelector

""" Class | Message

This cog is used for creating embedded messages to be sent anywhere in the server.
"""
class Message(commands.Cog, name = "Message"):
    """Commands for creating and managing custom embedded messages."""

    """ Method | On Cog Load

    This method is called when the Cog is added.
    """
    def __init__(self, bot):
        self.bot = bot

        if not 'custom_messages' in self.bot.data:
            self.bot.data['custom_messages'] = []
            self.bot.data_manager.save_data()

        print(f"{bot.OK} {bot.TIMELOG()} Loaded Message Cog.")


    """ Method | On Cog Unload

    This method is called when the Cog is unloaded.
    """
    def cog_unload(self):
        print(f"{self.bot.OK} {self.bot.TIMELOG()} Unloaded Message Cog.")


    """ Command | Message

    This is the command parent for all custom embed message sending. On its own, this only returns the help message
    for itself.
    """
    @commands.guild_only()
    @commands.group(name = "message", aliases = ['msg', 'messages'], help = "Shows commands related to creating and managing custom embedded messages.", invoke_without_command = True)
    async def message(self, ctx):
        await ctx.send_help("message")


    """ Command | Message Create

    Shows a prompt to the user to create a new custom message.
    """
    @commands.guild_only()
    @message.command(name = "create", aliases = ['add'], help = "Starts a prompt for creating a custom embedded message.")
    async def create_message(self, ctx):
        embed = self.bot.embed_util.get_embed(
            title = "Custom Embed Creation",
            desc = "Alright, let's get started creating a custom embed! I recommend checking [this link](https://leovoel.github.io/embed-visualizer/) to see what some of the elements I will guide you through creating will look like. First, please __**enter a title for the message**__.\n\nPay attention to the text at the bottom of my prompts, because I will give important information on how to skip or stop certain actions there.",
            footer = "Keep an eye on this text down here | You have 3m to enter a title."
        )
        prompt = await ctx.send(embed = embed)

        data = {}

        def check(m):
            return ctx.author.id == m.author.id and ctx.channel.id == m.channel.id

        try:
            msg = await self.bot.wait_for('message', check = check, timeout = 180)
            await msg.delete()
        except asyncio.TimeoutError:
            await prompt.delete()
            try:
                await ctx.message.add_reaction("\N{CROSS MARK}")
            except:
                pass
            return

        data['title'] = msg.content

        embed = self.bot.embed_util.update_embed(
            embed = embed,
            desc = "Great, now __**send a description for the message**__. This is the body of your message, where the main content should go.\n\n See this [Markdown Guide](https://support.discord.com/hc/en-us/articles/210298617-Markdown-Text-101-Chat-Formatting-Bold-Italic-Underline-) for formatting information.",
            fields = [{"name": "Title", "value": data['title']}],
            footer = "Enter \"skip\" to skip | You have 3m"
        )
        await prompt.edit(embed = embed)

        try:
            msg = await self.bot.wait_for('message', check = check, timeout = 180)
            await msg.delete()
        except asyncio.TimeoutError:
            await prompt.delete()
            try:
                await ctx.message.add_reaction("\N{CROSS MARK}")
            except:
                pass
            return

        if msg.content.lower() == 'skip':
            data['description'] = None
        else:
            data['description'] = msg.content

        embed = self.bot.embed_util.update_embed(
            embed = embed,
            desc = "Great, now __**send a url for the message**__. This turns the `Title` into a blue-highlighted url.",
            fields = [{"name": "Title", "value": data['title']}],
            footer = "Enter \"skip\" to skip | You have 3m"
        )
        await prompt.edit(embed = embed)

        try:
            msg = await self.bot.wait_for('message', check = check, timeout = 180)
            await msg.delete()
        except asyncio.TimeoutError:
            await prompt.delete()
            try:
                await ctx.message.add_reaction("\N{CROSS MARK}")
            except:
                pass
            return

        if msg.content.lower() == 'skip':
            data['url'] = None
        else:
            data['url'] = msg.content

        embed = self.bot.embed_util.update_embed(
            embed = embed,
            desc = "Perfect, now __**send a thumbnail url for the message**__. This adds a small image in the top-right of your message.",
            fields = [
                {"name": "Title", "value": data['title']},
                {"name": "Url", "value": data['url']}
            ],
            footer = "Enter \"skip\" to skip | You have 3m"
        )
        await prompt.edit(embed = embed)

        while True:
            try:
                msg = await self.bot.wait_for('message', check = check, timeout = 180)
                await msg.delete()
            except asyncio.TimeoutError:
                await prompt.delete()
                try:
                    await ctx.message.add_reaction("\N{CROSS MARK}")
                except:
                    pass
                return

            if msg.content.lower() == 'skip':
                data['thumbnail'] = None
            else:
                data['thumbnail'] = msg.content

            try:
                embed = self.bot.embed_util.update_embed(
                    embed = embed,
                    desc = "Got it, now __**send an image url for the message**__. This adds a large image at the bottom of your message.",
                    footer = "Enter \"skip\" to skip | You have 3m",
                    thumbnail = data['thumbnail']
                )
                await prompt.edit(embed = embed)
            except Exception as e:
                print(e)
                embed = self.bot.embed_util.update_embed(
                    embed = embed,
                    desc = "Your image url was an invlaid image! Please __**send a valid image url for the message**__. This adds a small image in the top-right of your message."
                )
                await prompt.edit(embed = embed)
                continue
            break

        while True:
            try:
                msg = await self.bot.wait_for('message', check = check, timeout = 180)
                await msg.delete()
            except asyncio.TimeoutError:
                await prompt.delete()
                try:
                    await ctx.message.add_reaction("\N{CROSS MARK}")
                except:
                    pass
                return

            if msg.content.lower() == 'skip':
                data['image'] = None
            else:
                data['image'] = msg.content

            try:
                embed = self.bot.embed_util.update_embed(
                    embed = embed,
                    desc = "Understood, now __**send the name of an \"author\" for your message**__. This adds a name to the very top of your message.",
                    footer = "Enter \"skip\" to skip | You have 3m",
                    thumbnail = data['thumbnail'],
                    image = data['image']
                )
                await prompt.edit(embed = embed)
            except:
                embed = self.bot.embed_util.update_embed(
                    embed = embed,
                    desc = "Your image url was an invlaid image! Please __**send a valid image url for the message**__. This adds a large image at the bottom of your message."
                )
                continue
            break

        try:
            msg = await self.bot.wait_for('message', check = check, timeout = 180)
            await msg.delete()
        except asyncio.TimeoutError:
            await prompt.delete()
            try:
                await ctx.message.add_reaction("\N{CROSS MARK}")
            except:
                pass
            return

        if msg.content.lower() == 'skip':
            data['author'] = None
        else:
            data['author'] = {}
            data['author']['name'] = msg.content

        if data['author']:
            embed = self.bot.embed_util.update_embed(
                embed = embed,
                desc = "Got it, now __**send an icon_url for the \"author\" for your message**__. This adds a small image before the author name.",
                footer = "Enter \"skip\" to skip | You have 3m",
                thumbnail = data['thumbnail'],
                image = data['image'],
                author = data['author']
            )
            await prompt.edit(embed = embed)

            while True:
                try:
                    msg = await self.bot.wait_for('message', check = check, timeout = 180)
                    await msg.delete()
                except asyncio.TimeoutError:
                    await prompt.delete()
                    try:
                        await ctx.message.add_reaction("\N{CROSS MARK}")
                    except:
                        pass
                    return

                if msg.content.lower() == 'skip':
                    data['author']['icon_url'] = None
                else:
                    data['author']['icon_url'] = msg.content

                try:
                    embed = self.bot.embed_util.update_embed(
                        embed = embed,
                        desc = "Understood, now __**send the title of the first `field` in your message**__. Fields add subsets of information with their own titles to the message. See [this link](https://leovoel.github.io/embed-visualizer/) for an example",
                        footer = "Enter \"done\" to skip this step and finish | You have 3m",
                        thumbnail = data['thumbnail'],
                        image = data['image'],
                        author = data['author']
                    )
                    await prompt.edit(embed = embed)
                except:
                    embed = self.bot.embed_util.update_embed(
                        embed = embed,
                        desc = "Your author icon url was an invlaid image! Please __**send a valid image url for the author icon**__. This adds a small image before the author name."
                    )
                    continue
                break

        embed = self.bot.embed_util.update_embed(
            embed = embed,
            desc = "Understood, now __**send the title of the first `field` in your message**__. Fields add subsets of information with their own titles to the message. See [this link](https://leovoel.github.io/embed-visualizer/) for an example.",
            footer = "Enter \"skip\" to skip this step | You have 3m",
            thumbnail = data['thumbnail'],
            image = data['image'],
            author = data['author']
        )
        await prompt.edit(embed = embed)

        data['fields'] = []
        while True:
            try:
                msg = await self.bot.wait_for('message', check = check, timeout = 180)
                await msg.delete()
            except asyncio.TimeoutError:
                await prompt.delete()
                try:
                    await ctx.message.add_reaction("\N{CROSS MARK}")
                except:
                    pass
                return

            if msg.content.lower() in ['done', 'skip']:
                break
            else:
                data['fields'].append({"name": msg.content, "value": None})

            embed = self.bot.embed_util.update_embed(
                embed = embed,
                desc = "Perfect, now __**send the value of that `field`**__. The value of a field is like the description of the entire embed, but for the specific section. See [this link](https://leovoel.github.io/embed-visualizer/) for an example.",
                footer = "You have 3m",
                thumbnail = data['thumbnail'],
                image = data['image'],
                author = data['author'],
                fields = [
                    {"name": "Title", "value": data['title']},
                    {"name": "Url", "value": data['url']}
                ] + data['fields']
            )
            await prompt.edit(embed = embed)

            try:
                msg = await self.bot.wait_for('message', check = check, timeout = 180)
                await msg.delete()
            except asyncio.TimeoutError:
                await prompt.delete()
                try:
                    await ctx.message.add_reaction("\N{CROSS MARK}")
                except:
                    pass
                return

            data['fields'][-1]['value'] = msg.content

            embed = self.bot.embed_util.update_embed(
                embed = embed,
                desc = "Got it, now __**whether you would like the field to appear in a row with other fields, or on its own line (y/n)**__. See [this link](https://leovoel.github.io/embed-visualizer/) for an example.",
                footer = "You have 3m",
                thumbnail = data['thumbnail'],
                image = data['image'],
                author = data['author'],
                fields = [
                    {"name": "Title", "value": data['title']},
                    {"name": "Url", "value": data['url']}
                ] + data['fields']
            )
            await prompt.edit(embed = embed)

            try:
                msg = await self.bot.wait_for('message', check = check, timeout = 180)
                await msg.delete()
            except asyncio.TimeoutError:
                await prompt.delete()
                try:
                    await ctx.message.add_reaction("\N{CROSS MARK}")
                except:
                    pass
                return

            if msg.content.lower() in ['y', 'ye', 'yes', 'true', 't']:
                data['fields'][-1]['inline'] = True
            else:
                data['fields'][-1]['inline'] = False

            embed = self.bot.embed_util.update_embed(
                embed = embed,
                desc = "Understood, now __**send the title of the next `field` in your message**__. Fields add subsets of information with their own titles to the message. See [this link](https://leovoel.github.io/embed-visualizer/) for an example.",
                footer = "Enter \"done\" to skip this step and finish | You have 3m",
                thumbnail = data['thumbnail'],
                image = data['image'],
                author = data['author'],
                fields = [
                    {"name": "Title", "value": data['title']},
                    {"name": "Url", "value": data['url']}
                ] + data['fields']
            )
            await prompt.edit(embed = embed)

        embed = self.bot.embed_util.update_embed(
            embed = embed,
            desc = "Alright, last but not least, __**respond with a channel mention of all the channels you want to have this message sent to**__ when it is sent later.\n\nFor example: `#channel-1 #chnnel-2 #channel-3`.",
            footer = "You have 3m",
            thumbnail = data['thumbnail'],
            image = data['image'],
            author = data['author'],
            fields = [
                {"name": "Title", "value": data['title']},
                {"name": "Url", "value": data['url']}
            ] + data['fields']
        )
        await prompt.edit(embed = embed)

        while True:
            try:
                msg = await self.bot.wait_for('message', check = check, timeout = 180)
                await msg.delete()
            except asyncio.TimeoutError:
                await prompt.delete()
                try:
                    await ctx.message.add_reaction("\N{CROSS MARK}")
                except:
                    pass
                return

            if len(msg.channel_mentions) > 0:
                data['channels'] = [ch.id for ch in msg.channel_mentions]
                break
            else:
                embed = self.bot.embed_util.update_embed(
                    embed = embed,
                    desc = "You must include at least one channel mention. Please __**respond with a channel mention of all the channels you want to have this message sent to**__.\n\nFor example: `#channel-1 #channel-2 #channel-3`.",
                    footer = "You have 3m",
                    thumbnail = data['thumbnail'],
                    image = data['image'],
                    author = data['author'],
                    fields = [
                        {"name": "Title", "value": data['title']},
                        {"name": "Url", "value": data['url']}
                    ] + data['fields']
                )
                await prompt.edit(embed = embed)

        self.bot.data['custom_messages'].append(data)
        self.bot.data_manager.save_data()

        embed = self.bot.embed_util.get_embed(
            title = "Custom Embed Created",
            desc = f"See your new embed below. Use `{self.bot.prefix}message` to see the other commands relating to editing and sending your new message.",
            fields = [{"name": "Channels", "value": "\n".join(ch.mention for ch in msg.channel_mentions)}]
        )
        await prompt.edit(embed = embed)
        embed = self.bot.embed_util.get_embed(
            title = data['title'],
            desc = data['description'],
            thumbnail = data['thumbnail'],
            image = data['image'],
            url = data['url'],
            author = data['author'],
            fields = data['fields']
        )
        await ctx.send(embed = embed)

        embed = self.bot.embed_util.get_embed(
            title = "Custom Embed Created",
            desc = f"`{ctx.author}` has created a new custom embedded message.",
            fields = [{"name": "Title", "value": data['title'], "inline": False}, {"name": "Channels", "value": "\n".join(ch.mention for ch in msg.channel_mentions)}],
            ts = True
        )
        log = self.bot.get_channel(self.bot.data['logs']['custom_messages'])
        await log.send(embed = embed)


    """ Command | Send Message

    Shows the user a menu prompt to select what message they want to send.
    """
    @commands.guild_only()
    @message.command(name = "send", aliases = ['start'], help = "Starts a menu prompt for selecting an inactive custom embedded message to start.")
    async def start_message(self, ctx):
        if len(self.bot.data['custom_messages']) > 0:
            entries = [e['title'] for e in self.bot.data['custom_messages']]

            source = MenuListSource(
                self.bot.embed_util,
                title = "Send Custom Messages",
                desc = "Please select a custom message to send.",
                entries = entries,
                selector = True
            )

            pages = MenuListSelector(ctx, source, self.handle_custom_message_start, delete_message_after = True)
            await pages.start(ctx)
        else:
            embed = self.bot.embed_util.get_embed(
                title = "Cannot Send Custom Messages",
                desc = f"There are no custom messages registered to be started. To create a custom message, use `{self.bot.prefix}message create`."
            )
            await ctx.send(embed = embed)

    async def handle_custom_message_start(self, ctx, selection, payload):
        msg = self.bot.data['custom_messages'][selection]
        embed = self.bot.embed_util.get_embed(
            title = msg['title'],
            desc = msg['description'],
            url = msg['url'],
            thumbnail = msg['thumbnail'],
            image = msg['image'],
            author = msg['author'],
            fields = msg['fields']
        )
        for ch in msg['channels']:
            channel = self.bot.get_channel(ch)
            if channel:
                await channel.send(embed = embed)


    @commands.guild_only()
    @message.command(name = "delete", aliases = ['del', 'rem', 'remove'], help = "Starts a menu prompt for selection a custom embedded message to remove from the system.")
    async def del_message(self, ctx):
        if len(self.bot.data['custom_messages']) > 0:
            entries = [e['title'] for e in self.bot.data['custom_messages']]

            source = MenuListSource(
                self.bot.embed_util,
                title = "Remove Custom Messages",
                desc = "Please select a custom message to remove.",
                entries = entries,
                selector = True
            )

            pages = MenuListSelector(ctx, source, self.handle_custom_message_remove, delete_message_after = True)
            await pages.start(ctx)
        else:
            embed = self.bot.embed_util.get_embed(
                title = "Cannot Show Custom Messages",
                desc = f"There are no custom messages registered to be removed. To create a custom message, use `{self.bot.prefix}message create`."
            )
            await ctx.send(embed = embed)

    async def handle_custom_message_remove(self, ctx, selection, payload):
        del self.bot.data['custom_messages'][selection]
        self.bot.data_manager.save_data()

""" Function | Setup

The function called by Discord.py when adding another file in a multi-file project.
"""
def setup(bot):
    bot.add_cog(Message(bot))
