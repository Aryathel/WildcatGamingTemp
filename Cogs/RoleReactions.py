import asyncio

import discord
from discord.ext import commands, menus
import datetime

from Resources.Utility import Confirmation
from Resources.Menus import MenuListSource, MenuListSelector

""" Class | Role Reactions

This Cog is used to handle the creation, management, and usage of role reactions.
"""
class RoleReaction(commands.Cog, name = "Role Reaction"):
    """Commands pertaining to creating, modifying, and handling role reactions."""

    """ Method | On Cog Load

    This method is called when the Cog is created, and handles any setup necessary to run.
    """
    def __init__(self, bot):
        self.bot = bot

        if not 'role_reactions' in self.bot.data:
            self.bot.data['role_reactions'] = []
            self.bot.data_manager.save_data()

        print(f"{bot.OK} {bot.TIMELOG()} Loaded Role Reaction Cog.")


    """ Method | On Cog Unload

    This method is called when the Cog is unloaded.
    """
    def cog_unload(self):
        print(f"{self.bot.OK} {self.bot.TIMELOG()} Unloaded Role Reaction Cog.")


    """ Command | View Role Reactions

    This is the parent command for all role reaction commands,
    and will display a list of all current role reactions, and if they are active.
    """
    @commands.guild_only()
    @commands.group(name = "rr", aliases = ['rrs', 'rolereaction', 'rolereactions'], help = "All commands pertaining to role reactions, use just this command to view the current ones.", brief = "", invoke_without_command = True)
    async def rr(self, ctx):
        # Display the list to the user.
        await self.display_rr_menu(ctx, msg = "Here are all registered role reactions.", selector = False)


    """ Command | Create Role Reaction

    This command is used to create a role reaction, and will start a prompt asking for a series of inputs.

    NOTE: Yes, I am aware that the number of while loops and break statements in this function is absolutely atrocious.
    Sue me.
    """
    @commands.guild_only()
    @rr.command(name = "create", help = "Start the role reaction creation prompt.", brief = "")
    async def rr_create(self, ctx):
        # Start the prompt asking for the title of the role reaction.
        embed = self.bot.embed_util.get_embed(
            title = "Create New Role Reaction",
            desc = "To get starting creating a new role reaction message, please __**enter the title of the role reaction**__:",
            footer = f"You have 3m | Step [1/4]"
        )
        prompt = await ctx.send(embed = embed)

        # The check function used to make sure responses are only recorded from the original command author.
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        # The check function used to make sure reactions are only recorded from the original command author.
        def check_reaction(reaction, user):
            return user == ctx.author and reaction.message.id == prompt.id

        # Get a message from the user for the title.
        try:
            msg = await self.bot.wait_for('message', check = check, timeout = 180)
        except asyncio.TimeoutError:
            # If the user does not respond in time, end the prompt session.
            await prompt.delete()
            try:
                await ctx.message.add_reaction('\N{CROSS MARK}')
            except:
                pass
            return

        # Record the role reaction title.
        title = msg.content
        await msg.delete()

        # Ask for the optional role reaction description.
        embed = self.bot.embed_util.get_embed(
            title = f"Create \"{title}\" Role Reaction",
            desc = "Alright, now that you have a title, please __**enter a description**__:",
            footer = f"Enter \"none\" to skip | You have 3m | Step [2/4]"
        )
        await prompt.edit(embed = embed)

        # get user input for the description.
        try:
            msg = await self.bot.wait_for('message', check = check, timeout = 180)
        except asyncio.TimeoutError:
            await prompt.delete()
            try:
                await ctx.message.add_reaction('\N{CROSS MARK}')
            except:
                pass
            return

        # Ignore the description if the user input "none", otherwise record the description.
        description = msg.content if not msg.content.lower() == 'none' else None
        await msg.delete()

        # Ask the user to mention a role to add to the role reactions.
        embed = self.bot.embed_util.get_embed(
            title = f"Create \"{title}\" Role Reaction",
            desc = "Ok, now let's add the role reactions. To get started, please __**mention a role that you want to be self-assignable**__:",
            footer = f"You have 3m | Step [3/4]"
        )
        if description:
            embed.add_field(name = "Description", value = description)
        await prompt.edit(embed = embed)

        # Make sure that the user actually mentioned a role.
        while True:
            try:
                msg = await self.bot.wait_for('message', check = check, timeout = 180)
            except asyncio.TimeoutError:
                await prompt.delete()
                try:
                    await ctx.message.add_reaction('\N{CROSS MARK}')
                except:
                    pass
                return

            # Redo the prompt if an improper message is passed.
            if not len(msg.role_mentions) > 0:
                await msg.delete()
                embed.description = "Your response must __**mention a role**__. To get started, please __**mention a role that you want to be self-assignable**__:"
                await prompt.edit(embed = embed)
                continue
            else:
                break

        # Looping for the rest of the input, guarantee that at least one role is on the role reaction.
        roles = []
        while True:
            # Record the role that was mentioned.
            role = msg.role_mentions[0]
            await msg.delete()

            # Ask the user to add a reaction to the message with the emoji they want to use for the role reaction.
            embed = self.bot.embed_util.get_embed(
                title = f"Create \"{title}\" Role Reaction",
                desc = f"Got it, now you need an emoji to pair with the {role.mention} role.\nPlease __**add an emoji as a reaction to this message to pair it**__.",
                footer = f"You have 3m | Step [3/4]"
            )
            if description:
                embed.add_field(name = "Description", value = description)
            if len(roles) > 0:
                embed.add_field(
                    name = "Role Reactions",
                    value = "\n".join(f"{r['emoji']} - {r['role_mention']}" for r in roles),
                    inline = False
                )
            await prompt.edit(embed = embed)

            # Verify that the bot can use the reaction that the user added.
            while True:
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout = 180, check = check_reaction)
                except asyncio.TimeoutError:
                    await prompt.delete()
                    try:
                        await ctx.message.add_reaction('\N{CROSS MARK}')
                    except:
                        pass
                    return

                await prompt.remove_reaction(reaction.emoji, user)
                if not type(reaction.emoji) == str:
                    emoji = reaction.emoji
                    if type(emoji) == discord.PartialEmoji:
                        emoji = self.bot.get_emoji(emoji.id)
                    if not emoji:
                        embed.description = f"I'm sorry, I cannot access that emoji. I recommend using standard Discord emojis or emojis from this server.\nPlease __**add an emoji as a reaction to this message to pair it**__."
                        await prompt.edit(embed = embed)
                        continue
                    if emoji in [r['emoji'] for r in roles]:
                        embed.description = f"You cannot register an emoji that is already in use!\nPlease __**add an emoji as a reaction to this message to pair it**__."
                        await prompt.edit(embed = embed)
                        continue
                # Record the role information.
                    roles.append({'emoji': emoji.id, 'role': role.id, 'role_mention': role.mention})
                else:
                    if reaction.emoji in [r['emoji'] for r in roles]:
                        embed.description = f"You cannot register an emoji that is already in use!\nPlease __**add an emoji as a reaction to this message to pair it**__."
                        await prompt.edit(embed = embed)
                        continue
                    roles.append({'emoji': reaction.emoji, 'role': role.id, 'role_mention': role.mention})

                break

            # Ask the user to input another role mention to add to the role reaction, but this time give them the option to enter "done" to quit.
            embed = self.bot.embed_util.get_embed(
                title = f"Create \"{title}\" Role Reaction",
                desc = f"Reaction added! Now, let's add more reactions to the message.\nPlease __**mention a role that you want to be self-assignable**__:",
                footer = f"Enter \"done\" to quit. | You have 3m | Step [3/4]"
            )
            if description:
                embed.add_field(name = "Description", value = description)
            if len(roles) > 0:
                embed.add_field(
                    name = "Role Reactions",
                    value = "\n".join(f"{r['emoji']} - {r['role_mention']}" for r in roles),
                    inline = False
                )
            await prompt.edit(embed = embed)

            # Handle the user input nearly identically to how it was first handled, minus allowing the user to quit.
            while True:
                try:
                    msg = await self.bot.wait_for('message', check = check, timeout = 180)
                except asyncio.TimeoutError:
                    await prompt.delete()
                    try:
                        await ctx.message.add_reaction('\N{CROSS MARK}')
                    except:
                        pass
                    return

                cont = msg.content.lower()
                if not len(msg.role_mentions) > 0 and not cont == 'done':
                    await msg.delete()
                    embed.description = "Your response must __**mention a role**__. Please __**mention a role that you want to be self-assignable**__:"
                    await prompt.edit(embed = embed)
                    continue
                else:
                    break

            if cont == 'done':
                await msg.delete()
                break

        # All role reactions are registered, now prompt the user to enter the channel the reaction will belong to.
        embed = self.bot.embed_util.get_embed(
            title = f"Create \"{title}\" Role Reaction",
            desc = f"Alright, the reactions are registered! For the final step, please __**mention a channel that the role reaction will be put in.**__\n\n**Note**: The role reaction will not start automatically. Once the role reaction is created, use `{self.bot.prefix}rr start` to start role reactions.",
            footer = f"You have 3m | Step [4/4]"
        )
        if description:
            embed.add_field(name = "Description", value = description)
        if len(roles) > 0:
            embed.add_field(
                name = "Role Reactions",
                value = "\n".join(f"{r['emoji']} - {r['role_mention']}" for r in roles),
                inline = False
            )

        await prompt.edit(embed = embed)

        # Make sure that the user has input a mention of a channel to use.
        while True:
            try:
                msg = await self.bot.wait_for('message', check = check, timeout = 180)
            except asyncio.TimeoutError:
                await prompt.delete()
                try:
                    await ctx.message.add_reaction('\N{CROSS MARK}')
                except:
                    pass
                return

            if not len(msg.channel_mentions) > 0 or not type(msg.channel_mentions[0]) == discord.TextChannel:
                await msg.delete()
                embed.description = "Your response must __**mention a channel**__. Please __**mention a channel that the role reaction will be put in**__:"
                await prompt.edit(embed = embed)
                continue
            else:
                await msg.delete()
                break

        # Record the channel entered
        channel = msg.channel_mentions[0]

        # Finish by outputting the full set of data to the user and adding a reaction to their original command.
        embed = self.bot.embed_util.get_embed(
            title = f"\"{title}\" Role Reaction Created!",
            desc = f"Your role reaction message is created! Remember, use `{self.bot.prefix}rr start` to start role reactions."
        )
        if description:
            embed.add_field(name = "Description", value = description)
        if len(roles) > 0:
            embed.add_field(
                name = "Role Reactions",
                value = "\n".join(f"{r['emoji']} - {r['role_mention']}" for r in roles),
                inline = False
            )
        embed.add_field(
            name = "Channel",
            value = channel.mention,
            inline = False
        )
        await prompt.edit(embed = embed)
        try:
            await ctx.message.add_reaction('\N{WHITE HEAVY CHECK MARK}')
        except:
            pass

        for role in roles:
            if not type(role['emoji']) == str:
                role['emoji'] = role['emoji'].id

        # Save the data on the completed role reaction.
        self.bot.data['role_reactions'].append({
            "title": title,
            "description": description,
            "roles": roles,
            "guild": ctx.guild.id,
            "channel": channel.id,
            "id": None
        })
        self.bot.data_manager.save_data()

        embed.description = f"`{ctx.author}` created a role reaction."
        embed.set_author(
            name = ctx.author.name,
            icon_url = ctx.author.avatar_url
        )

        log = self.bot.get_channel(self.bot.data['logs']['role_reaction'])
        await log.send(embed = embed)


    """ Command | Delete Role Reaction

    This command is used to delete a role reaction, will also delete the message associated with it.
    """
    @commands.guild_only()
    @rr.command(name = "delete", help = "Delete a role reaction, removing the message related to it if active.", brief = "")
    async def rr_delete(self, ctx):
        # Display the selection options to the user.
        await self.display_rr_menu(ctx, msg = "Please select a role reaction to delete.", handler = self.handle_rr_delete, selector = True)


    """ Coroutine | Handle Role Reaction Deletion

    This coroutine is te callback for the MenuListSelector that users use to select role reactions to delete.
    """
    async def handle_rr_delete(self, ctx, selection, payload):
        rr = self.bot.data['role_reactions'][selection]
        # Confirm that the user wants to delete the role reaction
        roles = self.load_rr_roles(rr)
        rr_channel = self.bot.get_channel(rr['channel'])
        confirm = await Confirmation(
            title = "Are You Sure?",
            url = f"https://discord.com/channels/{rr['guild']}/{rr['channel']}/{rr['id']}" if rr['id'] else None,
            msg = "This action will completely delete the Role Reaction from the system, including shutting it down if it is currently active.\n\n" +
                "\n".join(f"{r['emoji']} - {r['role']}" for r in roles)
        ).prompt(ctx)

        if confirm:
            if self.bot.data['role_reactions'][selection]['id']:
                ch = self.bot.get_channel(self.bot.data['role_reactions'][selection]['channel'])
                message = await ch.fetch_message(self.bot.data['role_reactions'][selection]['id'])
                await message.delete()

            del self.bot.data['role_reactions'][selection]
            self.bot.data_manager.save_data()
            await ctx.send(embed = self.bot.embed_util.get_embed(
                title = "Role Reaction Deleted",
                desc = "The role reaction was successfully deleted."
            ))

            embed = self.bot.embed_util.get_embed(
                title = "Role Reaction Deleted",
                desc = f"`{payload.member}` removed a Role Reaction from the {rr_channel.mention} channel.",
                ts = True
            )
            log = self.bot.get_channel(self.bot.data['logs']['role_reaction'])
            await log.send(embed = embed)


    """ Command | Edit Role Reaction

    This command is used to edit an already existing role reaction.
    """
    @commands.guild_only()
    @rr.command(name = "edit", help = "Modify an already existing role reaction, even if it is active.", brief = "")
    async def rr_edit(self, ctx):
        # Display the selection options to the user.
        await self.display_rr_menu(ctx, msg = "Please select a role reaction to edit.", handler = self.handle_rr_edit, selector = True)


    """ Coroutine | Handle Role Reaction Edit

    This coroutine handles the response from which role reaction was selected to be edited.
    """
    async def handle_rr_edit(self, ctx, selection, payload):
        rr = self.bot.data['role_reactions'][selection]
        # Confirm that the user wants to delete the role reaction
        roles = self.load_rr_roles(rr)
        rr_channel = self.bot.get_channel(rr['channel'])

        # Create the list of role reactions registered, based on if they are active.
        entries = [
            "Edit Title",
            "Edit Description",
            "Remove Role Reactions",
            "Add Role Reactions",
            "Edit Channel"
        ]

        # Create the source for handling the paginated menu displaying the list.
        source = MenuListSource(
            self.bot.embed_util,
            title = "Role Reactions",
            desc = "Please select a category to edit.",
            entries = entries,
            rr = (rr, roles, rr_channel, selection),
            selector = True
        )
        # Created the paginated menu.
        pages = MenuListSelector(ctx = ctx, source = source, handler = self.handle_rr_edit_select, delete_message_after = True)
        await pages.start(ctx)


    """ Coroutine | Handle Role Reaction Edit Selection

    This coroutine handles the user's selection of what category of the role reaction they want to edit.
    """
    async def handle_rr_edit_select(self, ctx, selection, payload, rr):
        rr = self.bot.data['role_reactions'][rr]
        roles = self.load_rr_roles(rr)
        rr_channel = self.bot.get_channel(rr['channel'])
        fields = []
        fields.append({"name": "Title", "value": rr['title']})
        fields.append({"name": "Description", "value": rr['description']})
        fields.append({"name": "Channel", "value": rr_channel.mention})
        fields.append({"name": "Roles", "value": "\n".join(f"{r['emoji']} - {r['role']}" for r in roles)})

        if selection == 0:
            await self.rr_edit_title(ctx, rr, fields)
        elif selection == 1:
            await self.rr_edit_description(ctx, rr, fields)
        elif selection == 2:
            if len(roles) > 1:
                await self.display_rr_remove_menu(ctx, rr)
            else:
                embed = self.bot.embed_util.get_embed(
                    title = "Process Complete",
                    desc = "You must keep at least 1 role reaction tied to your message, you cannot remove them all.",
                    fields = fields
                )
                await ctx.send(embed = embed)
        elif selection == 3:
            await self.rr_add_reactions(ctx, rr, fields)
        elif selection == 4:
            await self.rr_edit_channel(ctx, rr, fields, rr_channel)


    """ Coroutine | Handle Editing Role Reaction Title

    This coroutine handles the user interaction necessary to edit an existing role reaction's title.
    """
    async def rr_edit_title(self, ctx, rr, fields):
        # Prompt the user to enter a new title.
        embed = self.bot.embed_util.get_embed(
            title = f"Edit \"{rr['title']}\" Role Reaction Title",
            desc = "Please __**enter a new title for the role reaction**__:",
            fields = fields,
            footer = "You have 3m"
        )
        prompt = await ctx.send(embed = embed)

        # The check function used to make sure responses are only recorded from the original command author.
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        # Get a message from the user for the title.
        try:
            msg = await self.bot.wait_for('message', check = check, timeout = 180)
        except asyncio.TimeoutError:
            # If the user does not respond in time, end the prompt session.
            await prompt.delete()
            try:
                await ctx.message.add_reaction('\N{CROSS MARK}')
            except:
                pass
            await msg.delete()
            return

        await msg.delete()

        # Display updated information
        embed = self.bot.embed_util.update_embed(
            embed = embed,
            title = "Role Reaction Title Updated",
            desc = f"The title was updated from `{rr['title']}` to `{msg.content}`.",
            footer = self.bot.footer
        )
        embed.set_field_at(0, name = "Title", value = msg.content, inline = True)
        await prompt.edit(embed = embed)

        # Save updated information
        rr['title'] = msg.content
        self.bot.data_manager.save_data()

        if rr['id']:
            channel = self.bot.get_channel(rr['channel'])
            msg = await channel.fetch_message(rr['id'])
            embed = self.bot.embed_util.update_embed(embed = msg.embeds[0], title = rr['title'])
            await msg.edit(embed = embed)

        # Log the changes
        embed = self.bot.embed_util.update_embed(embed = embed, author = ctx.author)
        log = self.bot.get_channel(self.bot.data['logs']['role_reaction'])
        await log.send(embed = embed)


    """ Coroutine | Handle Editing Role Reaction Description

    This coroutine handles the user interaction necessary to edit an existing role reaction's description.
    """
    async def rr_edit_description(self, ctx, rr, fields):
        # Prompt the user to enter a new title.
        embed = self.bot.embed_util.get_embed(
            title = f"Edit \"{rr['title']}\" Role Reaction Description",
            desc = "Please __**enter a new description for the role reaction**__:",
            fields = fields,
            footer = "You have 3m"
        )
        prompt = await ctx.send(embed = embed)

        # The check function used to make sure responses are only recorded from the original command author.
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        # Get a message from the user for the title.
        try:
            msg = await self.bot.wait_for('message', check = check, timeout = 180)
        except asyncio.TimeoutError:
            # If the user does not respond in time, end the prompt session.
            await prompt.delete()
            try:
                await ctx.message.add_reaction('\N{CROSS MARK}')
            except:
                pass
            await msg.delete()
            return

        await msg.delete()

        # Display updated information
        embed = self.bot.embed_util.update_embed(
            embed = embed,
            title = "Role Reaction Description Updated",
            desc = f"The description was updated from `{rr['description']}` to `{msg.content}`.",
            footer = self.bot.footer
        )
        embed.set_field_at(1, name = "Description", value = msg.content, inline = True)
        await prompt.edit(embed = embed)

        # Save updated information
        rr['description'] = msg.content
        self.bot.data_manager.save_data()

        if rr['id']:
            channel = self.bot.get_channel(rr['channel'])
            msg = await channel.fetch_message(rr['id'])
            embed = self.bot.embed_util.update_embed(
                embed = msg.embeds[0],
                desc = rr['description']  + "\n\n" + "\n".join(f"{r['emoji']} - {r['role']}" for r in self.load_rr_roles(rr))
            )
            await msg.edit(embed = embed)

        # Log the changes
        embed = self.bot.embed_util.update_embed(embed = embed, author = ctx.author)
        log = self.bot.get_channel(self.bot.data['logs']['role_reaction'])
        await log.send(embed = embed)


    """ Coroutine | Handle Removing Role Reactions

    This coroutine handles the user interaction necessary to remove registered roles from a role reaction.
    """
    async def rr_handle_reaction_remove(self, ctx, selection, payload, rr):
        if rr['id']:
            channel = self.bot.get_channel(rr['channel'])
            msg = await channel.fetch_message(rr['id'])
            roles = self.load_rr_roles(rr)
            await msg.clear_reaction(roles[selection]['emoji'])
            del roles[selection]
            del rr['roles'][selection]
            self.bot.data_manager.save_data()

            embed = self.bot.embed_util.update_embed(
                embed = msg.embeds[0],
                desc = rr['description'] + "\n\n" + "\n".join(f"{r['emoji']} - {r['role']}" for r in roles)
            )
            await msg.edit(embed = embed)
        else:
            del rr['roles'][selection]
            self.bot.data_manager.save_data()

        fields = [
            {
                "name": "Title", "value": rr['title']
            },
            {
                "name": "Description", "value": rr['description']
            },
            {
                "name": "Channel", "value": self.bot.get_channel(rr['channel']).mention
            },
            {
                "name": "Roles",
                "value": "\n".join(f"{r['emoji']} - {r['role']}" for r in self.load_rr_roles(rr)),
                "inline": False
            }
        ]

        # Display updated information
        embed = self.bot.embed_util.get_embed(
            title = "Role Reactions Updates",
            desc = f"The roles for the `{rr['title']}` role reaction have been updated.",
            author = ctx.author,
            fields = fields
        )

        log = self.bot.get_channel(self.bot.data['logs']['role_reaction'])
        await log.send(embed = embed)

        if len(rr['roles']) > 1:
            await self.display_rr_remove_menu(ctx, rr)
        else:
            embed = self.bot.embed_util.get_embed(
                title = "Process Complete",
                desc = "You must keep at least 1 role reaction tied to your message, you cannot remove them all.",
                fields = fields
            )
            await ctx.send(embed = embed)

    """ Coroutine | Display Role Reaction Remove Options

    This command shows the user their options for choosing roles to remove from a role reaction.
    """
    async def display_rr_remove_menu(self, ctx, rr):
        roles = self.load_rr_roles(rr)
        rr_channel = self.bot.get_channel(rr['channel'])

        # Create the list of role reactions registered, based on if they are active.
        entries = [f" {r['emoji']} - {r['role']}" for r in roles]

        # Create the source for handling the paginated menu displaying the list.
        source = MenuListSource(
            self.bot.embed_util,
            title = "Remove Role Reactions",
            desc = "Please select a reaction to remove.",
            entries = entries,
            rr = (rr, roles, rr_channel, rr),
            selector = True
        )
        # Created the paginated menu.
        pages = MenuListSelector(ctx = ctx, source = source, handler = self.rr_handle_reaction_remove, delete_message_after = True)
        await pages.start(ctx)


    """ Coroutine | Handle Adding Role Reactions

    This coroutine handles the user interaction necessary to add roles to an existing role reaction.
    """
    async def rr_add_reactions(self, ctx, rr, fields, num = None):
        # The check function used to make sure responses are only recorded from the original command author.
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        def check_reaction(reaction, user):
            return user == ctx.author and reaction.message.id == prompt.id

        if num is None:
            num = len(rr['roles'])

        # Ask the user to mention a role to add to the role reactions.
        embed = self.bot.embed_util.get_embed(
            title = f"Add \"{rr['title']}\" Role Reactions",
            desc = "To add new reactions, please __**mention a role that you want to be self-assignable**__:",
            footer = f"Enter \"done\" to quit | You have 3m",
            fields = fields
        )
        prompt = await ctx.send(embed = embed)

        # Make sure that the user actually mentioned a role.
        while True:
            try:
                msg = await self.bot.wait_for('message', check = check, timeout = 180)
            except asyncio.TimeoutError:
                await prompt.delete()
                try:
                    await ctx.message.add_reaction('\N{CROSS MARK}')
                except:
                    pass

                if not num == len(rr['roles']):
                    possible = [rr for rr in self.bot.data['role_reactions'] if rr['id'] is not None]
                    i = possible.index(rr)
                    await self.rr_stop_callback(ctx, i, None)
                    possible = [rr for rr in self.bot.data['role_reactions'] if rr['id'] is None]
                    i = possible.index(rr)
                    await self.rr_start_callback(ctx, i, None)
                    embed = self.bot.embed_util.update_embed(
                        embed = embed,
                        author = ctx.author,
                        footer = self.bot.footer
                    )
                    log = self.bot.get_channel(self.bot.data['logs']['role_reaction'])
                    await log.send(embed = embed)
                return

            # Redo the prompt if an improper message is passed.
            await msg.delete()
            if msg.content.lower() == "done":
                # Display updated information
                embed = self.bot.embed_util.update_embed(
                    embed = embed, title = "Role Reactions Updated", desc = f"The role reactions for `{rr['title']}` were updated.",
                    footer = self.bot.footer
                )
                embed.set_field_at(3, name = "Roles", value = "\n".join(f"{r['emoji']} - {r['role']}" for r in self.load_rr_roles(rr)), inline = True)
                await prompt.edit(embed = embed)

                # Log the changes
                print(num)

                if not num == len(rr['roles']):
                    possible = [rr for rr in self.bot.data['role_reactions'] if rr['id'] is not None]
                    i = possible.index(rr)
                    await self.rr_stop_callback(ctx, i, None)
                    possible = [rr for rr in self.bot.data['role_reactions'] if rr['id'] is None]
                    i = possible.index(rr)
                    await self.rr_start_callback(ctx, i, None)
                    embed = self.bot.embed_util.update_embed(
                        embed = embed,
                        author = ctx.author,
                        footer = self.bot.footer
                    )
                    log = self.bot.get_channel(self.bot.data['logs']['role_reaction'])
                    await log.send(embed = embed)
                return
            if not len(msg.role_mentions) > 0:
                embed.description = "Your response must __**mention a role**__. To get started, please __**mention a role that you want to be self-assignable**__:"
                await prompt.edit(embed = embed)
                continue
            else:
                break

        role = msg.role_mentions[0]

        # Ask the user to add a reaction to the message with the emoji they want to use for the role reaction.
        embed = self.bot.embed_util.update_embed(
            embed = embed,
            desc = f"Got it, now you need an emoji to pair with the {role.mention} role.\nPlease __**add an emoji as a reaction to this message to pair it**__.",
            footer = f"You have 3m"
        )
        await prompt.edit(embed = embed)

        # Verify that the bot can use the reaction that the user added.
        while True:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout = 180, check = check_reaction)
            except asyncio.TimeoutError:
                await prompt.delete()
                try:
                    await ctx.message.add_reaction('\N{CROSS MARK}')
                except:
                    pass
                if not num == len(rr['roles']):
                    possible = [rr for rr in self.bot.data['role_reactions'] if rr['id'] is not None]
                    i = possible.index(rr)
                    await self.rr_stop_callback(ctx, i, None)
                    possible = [rr for rr in self.bot.data['role_reactions'] if rr['id'] is None]
                    i = possible.index(rr)
                    await self.rr_start_callback(ctx, i, None)
                    embed = self.bot.embed_util.update_embed(
                        embed = embed,
                        author = ctx.author,
                        footer = self.bot.footer
                    )
                    log = self.bot.get_channel(self.bot.data['logs']['role_reaction'])
                    await log.send(embed = embed)
                return

            await prompt.remove_reaction(reaction.emoji, user)
            if not type(reaction.emoji) == str:
                emoji = reaction.emoji
                if type(emoji) == discord.PartialEmoji:
                    emoji = self.bot.get_emoji(emoji.id)
                if not emoji:
                    embed.description = f"I'm sorry, I cannot access that emoji. I recommend using standard Discord emojis or emojis from this server.\nPlease __**add an emoji as a reaction to this message to pair it**__."
                    await prompt.edit(embed = embed)
                    continue
            # Record the role information.
                if emoji in [r['emoji'] for r in rr['roles']]:
                    embed.description = f"You cannot register an emoji that is already in use!\nPlease __**add an emoji as a reaction to this message to pair it**__."
                    await prompt.edit(embed = embed)
                    continue
                rr['roles'].append({'emoji': emoji.id, 'role': role.id, 'role_mention': role.mention})
            else:
                if reaction.emoji in [r['emoji'] for r in rr['roles']]:
                    embed.description = f"You cannot register an emoji that is already in use!\nPlease __**add an emoji as a reaction to this message to pair it**__."
                    await prompt.edit(embed = embed)
                    continue
                rr['roles'].append({'emoji': reaction.emoji, 'role': role.id, 'role_mention': role.mention})

            break

        self.bot.data_manager.save_data()
        await prompt.delete()

        roles = self.load_rr_roles(rr)
        fields[3] = {"name": "Roles", "value": "\n".join(f"{r['emoji']} - {r['role']}" for r in roles)}
        await self.rr_add_reactions(ctx, rr, fields, num)


    """ Coroutine | Handle Editing Role Reaction Channel

    This coroutine handles the user interaction necessary to edit an existing role reaction's channel.
    """
    async def rr_edit_channel(self, ctx, rr, fields, channel):
        # Prompt the user to enter a new title.
        embed = self.bot.embed_util.get_embed(
            title = f"Edit \"{rr['title']}\" Role Reaction Channel",
            desc = "Please __**mention a new channel for the role reaction**__:",
            fields = fields,
            footer = "You have 3m"
        )
        prompt = await ctx.send(embed = embed)

        # The check function used to make sure responses are only recorded from the original command author.
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        # Make sure that the user has input a mention of a channel to use.
        while True:
            try:
                msg = await self.bot.wait_for('message', check = check, timeout = 180)
            except asyncio.TimeoutError:
                await prompt.delete()
                try:
                    await ctx.message.add_reaction('\N{CROSS MARK}')
                except:
                    pass
                return

            if not len(msg.channel_mentions) > 0 or not type(msg.channel_mentions[0]) == discord.TextChannel:
                await msg.delete()
                embed.description = "Your response must __**mention a channel**__. Please __**mention a channel that the role reaction will be put in**__:"
                await prompt.edit(embed = embed)
                continue
            else:
                await msg.delete()
                break

        # Display updated information
        embed = self.bot.embed_util.update_embed(
            embed = embed,
            title = "Role Reaction Channel Updated",
            desc = f"The channel was updated from {channel.mention} to {msg.channel_mentions[0].mention}.",
            footer = self.bot.footer
        )
        embed.set_field_at(2, name = "Channel", value = msg.channel_mentions[0].mention, inline = True)
        await prompt.edit(embed = embed)

        if rr['id']:
            possible = [rr for rr in self.bot.data['role_reactions'] if rr['id'] is not None]
            i = possible.index(rr)
            await self.rr_stop_callback(ctx, i, None)
            # Save updated information
            rr['channel'] = msg.channel_mentions[0].id
            self.bot.data_manager.save_data()

            possible = [rr for rr in self.bot.data['role_reactions'] if rr['id'] is None]
            i = possible.index(rr)
            await self.rr_start_callback(ctx, i, None)
        else:
            # Save updated information
            rr['channel'] = msg.channel_mentions[0].id
            self.bot.data_manager.save_data()

        # Log the changes
        embed = self.bot.embed_util.update_embed(
            embed = embed,
            author = ctx.author
        )
        log = self.bot.get_channel(self.bot.data['logs']['role_reaction'])
        await log.send(embed = embed)


    """ Command | Start Role Reaction

    This command is used to start a role reaction.
    """
    @commands.guild_only()
    @rr.command(name = "start", help = "Start a registered role reaction menu.", brief = "")
    async def rr_start(self, ctx):
        await self.display_rr_menu(ctx, msg = "Please select a Role Reaction to start.", handler = self.rr_start_callback, selector = True, active = False)


    async def rr_start_callback(self, ctx, selection, payload):
        possible = [rr for rr in self.bot.data['role_reactions'] if rr['id'] is None]
        rr = possible[selection]
        channel = self.bot.get_channel(rr['channel'])
        roles = self.load_rr_roles(rr)
        if channel:
            permissions = channel.permissions_for(ctx.guild.get_member(self.bot.user.id))
            if permissions.send_messages and permissions.read_messages:
                embed = self.bot.embed_util.get_embed(
                    title = rr['title'],
                    desc = rr['description'] + "\n\n" + "\n".join(f"{r['emoji']} - {r['role']}" for r in roles)
                )
                msg = await channel.send(embed = embed)

                for role in roles:
                    await msg.add_reaction(role['emoji'])

                rr['id'] = msg.id
                self.bot.data_manager.save_data()

                if payload:
                    embed = self.bot.embed_util.get_embed(
                        title = "Role Reaction Started",
                        desc = f"`{ctx.author}` has started a role reaction in {channel.mention}.",
                        author = ctx.author,
                        ts = True
                    )
                    log = self.bot.get_channel(self.bot.data['logs']['role_reaction'])
                    await log.send(embed = embed)
                return

        embed = self.bot.embed_util.get_embed(
            title = "Cannot Start Role Reaction",
            desc = f"It appears that I cannot access the channel to start the role reaction. Either update the channel permissions to allow me to read messages and send messages, or chang ethe channel for the role reaction using `{self.bot.prefix}rr edit`."
        )
        await ctx.send(embed = embed)

    """ Command | Stop Role Reaction

    This command will stop an active role reaction,but will not delete it from the system.
    """
    @commands.guild_only()
    @rr.command(name = "stop", help = "Stop an active role reaction, without deleting it from the system.", brief = "")
    async def rr_stop(self, ctx):
        await self.display_rr_menu(ctx, msg = "Please select a Role Reaction to stop.", handler = self.rr_stop_callback, selector = True, active = True)


    async def rr_stop_callback(self, ctx, selection, payload):
        possible = [rr for rr in self.bot.data['role_reactions'] if rr['id'] is not None]
        rr = possible[selection]

        channel = self.bot.get_channel(rr['channel'])
        msg = await channel.fetch_message(rr['id'])

        await msg.delete()
        rr['id'] = None
        self.bot.data_manager.save_data()

        if payload:
            embed = self.bot.embed_util.get_embed(
                title = "Role Reaction Stopped",
                desc = f"`{ctx.author}` has stopped a role reaction in {channel.mention}.",
                author = ctx.author,
                ts = True
            )

            log = self.bot.get_channel(self.bot.data['logs']['role_reaction'])
            await log.send(embed = embed)


    """ Event Listener | On Reaction Add

    This listener handles users adding a reaction to a role reaction message.
    """
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if not payload.user_id == self.bot.user.id:
            try:
                i = [r['id'] for r in self.bot.data['role_reactions']].index(payload.message_id)
                rr = self.bot.data['role_reactions'][i]
                if payload.emoji.is_custom_emoji():
                    i = [r['emoji'] for r in rr['roles']].index(payload.emoji.id)
                elif payload.emoji.is_unicode_emoji():
                    i = [r['emoji'] for r in rr['roles']].index(payload.emoji.name)

                guild = self.bot.get_guild(payload.guild_id)
                role = guild.get_role(rr['roles'][i]['role'])
                if not role in payload.member.roles:
                    await payload.member.add_roles(role)
            except ValueError:
                pass


    """ Event Listener | On Reaction Remove

    This listener handles users removing reactions from a role reaction message.
    """
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if not payload.user_id == self.bot.user.id:
            try:
                i = [r['id'] for r in self.bot.data['role_reactions']].index(payload.message_id)
                rr = self.bot.data['role_reactions'][i]
                if payload.emoji.is_custom_emoji():
                    i = [r['emoji'] for r in rr['roles']].index(payload.emoji.id)
                elif payload.emoji.is_unicode_emoji():
                    i = [r['emoji'] for r in rr['roles']].index(payload.emoji.name)

                guild = self.bot.get_guild(payload.guild_id)
                role = guild.get_role(rr['roles'][i]['role'])
                member = guild.get_member(payload.user_id)
                if role in member.roles:
                    await member.remove_roles(role)
            except ValueError:
                pass


    """ Coroutine | Display Role Reaction Menu

    This coroutine displays the menu of all registered role reactions in one of two ways:
        1 - This is simply a display, and the user can browse role reactions.
        2 - The user is prompted to select a role reaction, after which that selection is passed to a handler function.
    """
    async def display_rr_menu(self, ctx, msg, handler = None, selector = False, active = None):
        # If there are role reactions created.
        if len(self.bot.data['role_reactions']) > 0:
            # Create the list of role reactions registered, based on if they are active.
            entries = []
            for e in self.bot.data['role_reactions']:
                if e['id'] is not None:
                    if active in [True, None]:
                        entries.append(f"[{e['title']}](https://discord.com/channels/{e['guild']}/{e['channel']}/{e['id']}) | Active: `True`")
                else:
                    if active in [False, None]:
                        entries.append(f"{e['title']} | Active: `False`")

            # Handle the case that no entries were found for the specified type.
            if not entries:
                if active == False:
                    embed = self.bot.embed_util.get_embed(
                        title = "Cannot Start Role Reactions",
                        desc = f"There are no inactive role reactions to start. To create a new role reaction, use `{self.bot.prefix}rr create`."
                    )
                    await ctx.send(embed = embed)
                elif active == True:
                    embed = self.bot.embed_util.get_embed(
                        title = "Cannot Stop Role Reactions",
                        desc = f"There are no active role reactions to stop. To start a role reaction, use `{self.bot.prefix}rr start`."
                    )
                    await ctx.send(embed = embed)
                return


            # Create the source for handling the paginated menu displaying the list.
            source = MenuListSource(
                self.bot.embed_util,
                title = "Role Reactions",
                desc = msg,
                entries = entries,
                selector = selector
            )
            # Created the paginated menu.
            if handler:
                pages = MenuListSelector(ctx = ctx, source = source, handler = handler, delete_message_after = True)
            else:
                pages = menus.MenuPages(source = source, delete_message_after = True)
            await pages.start(ctx)
        else:
            # If no role reactions are registered, prompt the user to create one.
            embed = self.bot.embed_util.get_embed(
                title = "No Role Reactions Registered",
                desc = f"To create a role reaction message, use `{self.bot.prefix}rr create`."
            )
            await ctx.send(embed = embed)

    """ Method | Load Role Reaction Roles

    This method takes in a role reaction data structure and pulls the emojis and paired role role_mentions
    from that data in order to have it be displayed through Discord.
    """
    def load_rr_roles(self, rr):
        roles = []
        for r in rr['roles']:
            if type(r['emoji']) == str:
                roles.append({'emoji': r['emoji'], 'role': r['role_mention']})
            else:
                emoji = self.bot.get_emoji(r['emoji'])
                if emoji:
                    roles.append({'emoji': emoji, 'role': r['role_mention']})
                else:
                    roles.append({'emoji': "Error", 'role': r['role_mention']})

        return roles

""" Function | Setup

The function called by Discord.py when adding another file in a multi-file project.
"""
def setup(bot):
    bot.add_cog(RoleReaction(bot))
