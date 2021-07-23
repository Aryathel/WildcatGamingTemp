import random

import discord
from discord.ext import commands
import datetime

from Resources.Utility import Confirmation
from Resources.Menus import MenuListSource, MenuListSelector, SchoolMenuSelect, SchoolMenuList

""" Class | School Roles

This Cog contains commands for the management and assignment of roles for specific schools, sorted alphabetically.
"""
class SchoolRoles(commands.Cog, name = "School Roles"):
    """Commands for the management and assignment of roles for specific schools."""

    """ Method | Cog Setup

    This method is called when the Cog is addded to the system, and verifies that necessary components are there.
    """
    def __init__(self, bot):
        self.bot = bot

        if not 'school_roles' in self.bot.data:
            self.bot.data['school_roles'] = {}
            for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                self.bot.data['school_roles'][letter] = []
            self.bot.data_manager.save_data()

        print(f"{bot.OK} {bot.TIMELOG()} Loaded School Roles Cog.")


    """ Method | On Cog Unload

    Ths method is called when the Cog is unloaded from the system.
    """
    def cog_unload(self):
        print(f"{self.bot.OK} {self.bot.TIMELOG()} Unloaded School Roles Cog.")


    """ Command | Sample

    This is a template for a standard command.
    """
    @commands.guild_only()
    @commands.group(name = "school", aliases = ['schools'], help = "Show a menu for selecting a school roles to assign to yourself.", brief = "", invoke_without_command = True)
    async def schools(self, ctx):
        entries = []
        for mapping in [self.get_school_mapping(ctx.guild, l) for l in self.bot.data['school_roles']]:
            if mapping['roles']:
                entries.append(mapping)

        source = SchoolMenuList(
            self.bot.embed_util,
            title = "Select School Category Letter",
            desc = "Please select the letter that the school you want to add is under. Select a school role you already have to remove it.",
            entries = entries
        )
        pages = SchoolMenuSelect(ctx, source, self.handle_school_letter_select, delete_message_after = True)

        await pages.start(ctx)


    """ Coroutine | School Letter Select

    This command is te callback for the menu selection for choosing what letter of school you want to add to yourself.
    """
    async def handle_school_letter_select(self, ctx, letter):
        entries = []
        for r in self.bot.data['school_roles'][letter]:
            r = ctx.guild.get_role(r)
            if r:
                entries.append(r)

        if len(entries) == 1:
            await self.update_school_role(ctx, entries[0])
        else:
            entries = sorted(entries, key = lambda x: x.name)
            source = MenuListSource(
                self.bot.embed_util,
                title = "Select School Role",
                desc = "Please react with the corresponding number of the role you wish to get.",
                entries = [e.mention for e in entries],
                roles = entries,
                selector = True
            )

            pages = MenuListSelector(ctx, source, self.update_school_role, delete_message_after = True)
            await pages.start(ctx)


    """ Coroutine | Give School Role

    Give the given role to the author of the context passed.
    """
    async def update_school_role(self, ctx, role):
        if role in ctx.author.roles:
            await ctx.author.remove_roles(role)
        else:
            await ctx.author.add_roles(role)


    """ Command | Add School Role

    This command is used to add a role to the list of registered school roles.
    """
    @commands.guild_only()
    @schools.command(name = "add", aliases = ['create'], help = "Add a school role to the system to be self assignable.", brief = "A @University of Arizona")
    async def add_school(self, ctx, letter: str, *, role):
        letter = letter.strip()[0].upper()
        if not letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            embed = self.bot.embed_util.get_embed(
                title = "Invalid Letter",
                desc = f"Your input, `{letter}`, was not valid. Please use a letter in the alphabet."
            )
            return await ctx.send(embed = embed)

        if role.lower().strip() in [r.name.lower() for r in ctx.guild.roles]:
            print("Role Already Exists")
            role = ctx.guild.roles[[r.name.lower() for r in ctx.guild.roles].index(role.lower().strip())]
        else:
            role = await ctx.guild.create_role(
                name = role.strip(),
                color = discord.Color.from_rgb(random.randint(0,  255), random.randint(0,  255), random.randint(0,  255)),
                reason = f"{ctx.author} is adding a new school role to the system."
            )

        for l in self.bot.data['school_roles']:
            for r in self.bot.data['school_roles'][l]:
                if role.id == r:
                    embed = self.bot.embed_util.get_embed(
                        title = "Role Already Registered",
                        desc = f"The {role.mention} role is already registered with the letter `{l}` and cannot be re-registered."
                    )
                    return await ctx.send(embed = embed)

        self.bot.data['school_roles'][letter].append(role.id)
        self.bot.data_manager.save_data()

        embed = self.bot.embed_util.get_embed(
            title = "Role Registered",
            desc = f"The {role.mention} role was added to the list of registered school roles."
        )
        await ctx.send(embed = embed)

        embed = self.bot.embed_util.update_embed(
            embed = embed,
            desc = f"`{ctx.author}` added the {role.mention} role to the list of registered school roles.",
            author = ctx.author,
            ts = True
        )
        log = self.bot.get_channel(self.bot.data['logs']['school_roles'])
        await log.send(embed = embed)


    """ Command | Remove School Role

    This command is used to remove a registered school role from the list of school roles, using a menu system.
    """
    @commands.guild_only()
    @schools.command(name = "remove", aliases = ['rem', 'del', 'delete'], help = "Remove a school role from the self-assignable system.", brief = "")
    async def rem_school(self, ctx):
        entries = []
        for mapping in [self.get_school_mapping(ctx.guild, l) for l in self.bot.data['school_roles']]:
            if mapping['roles']:
                entries.append(mapping)

        source = SchoolMenuList(
            self.bot.embed_util,
            title = "Select School Category Letter",
            desc = "Please select the letter that the school you want to remove from the system is under.",
            entries = entries
        )
        pages = SchoolMenuSelect(ctx, source, self.school_letter_remove_select, delete_message_after = True)

        await pages.start(ctx)


    """ Coroutine | School Letter Remove Select

    This command is te callback for the menu selection for choosing what letter of school you want to have removed form the system.
    """
    async def school_letter_remove_select(self, ctx, letter):
        entries = []
        for r in self.bot.data['school_roles'][letter]:
            r = ctx.guild.get_role(r)
            if r:
                entries.append(r)

        if len(entries) == 1:
            await self.remove_school_from_system(ctx, entries[0])
        else:
            entries = sorted(entries, key = lambda x: x.name)
            source = MenuListSource(
                self.bot.embed_util,
                title = "Select School Role",
                desc = "Please react with the corresponding number of the role you wish to get.",
                entries = [e.mention for e in entries],
                roles = entries,
                selector = True
            )

            pages = MenuListSelector(ctx, source, self.remove_school_from_system, delete_message_after = True)
            await pages.start(ctx)


    """ Coroutine | Remove School From System

    This coroutine handles the final selection of a role to remove from the school system.
    This only deletes the role, the `get_school_mapping` method handles removing the role from the data later.
    """
    async def remove_school_from_system(self, ctx, role):
        await role.delete(reason = f"`{ctx.author}` has removed the role from the system.")

        embed = self.bot.embed_util.get_embed(
            title = "School Role Deleted",
            desc = f"`{ctx.author}` has deleted the `{role.name}` role from the school system",
            ts = True
        )
        log = self.bot.get_channel(self.bot.data['logs']['school_roles'])
        await log.send(embed = embed)


    """ Method | Get School Mapping

    This method handled formatting a specific set of schools for a certain letter to be used in menus.
    """
    def get_school_mapping(self, guild, letter):
        letters = {
            "A": "\N{REGIONAL INDICATOR SYMBOL LETTER A}", "B": "\N{REGIONAL INDICATOR SYMBOL LETTER B}",
            "C": "\N{REGIONAL INDICATOR SYMBOL LETTER C}", "D": "\N{REGIONAL INDICATOR SYMBOL LETTER D}",
            "E": "\N{REGIONAL INDICATOR SYMBOL LETTER E}", "F": "\N{REGIONAL INDICATOR SYMBOL LETTER F}",
            "G": "\N{REGIONAL INDICATOR SYMBOL LETTER G}", "H": "\N{REGIONAL INDICATOR SYMBOL LETTER H}",
            "I": "\N{REGIONAL INDICATOR SYMBOL LETTER I}", "J": "\N{REGIONAL INDICATOR SYMBOL LETTER J}",
            "K": "\N{REGIONAL INDICATOR SYMBOL LETTER K}", "L": "\N{REGIONAL INDICATOR SYMBOL LETTER L}",
            "M": "\N{REGIONAL INDICATOR SYMBOL LETTER M}", "N": "\N{REGIONAL INDICATOR SYMBOL LETTER N}",
            "O": "\N{REGIONAL INDICATOR SYMBOL LETTER O}", "P": "\N{REGIONAL INDICATOR SYMBOL LETTER P}",
            "Q": "\N{REGIONAL INDICATOR SYMBOL LETTER Q}", "R": "\N{REGIONAL INDICATOR SYMBOL LETTER R}",
            "S": "\N{REGIONAL INDICATOR SYMBOL LETTER S}", "T": "\N{REGIONAL INDICATOR SYMBOL LETTER T}",
            "U": "\N{REGIONAL INDICATOR SYMBOL LETTER U}", "V": "\N{REGIONAL INDICATOR SYMBOL LETTER V}",
            "W": "\N{REGIONAL INDICATOR SYMBOL LETTER W}", "X": "\N{REGIONAL INDICATOR SYMBOL LETTER X}",
            "Y": "\N{REGIONAL INDICATOR SYMBOL LETTER Y}", "Z": "\N{REGIONAL INDICATOR SYMBOL LETTER Z}"
        }

        res = {
            "letter": letter,
            "emoji": letters[letter],
            "roles": []
        }

        for school in self.bot.data['school_roles'][letter]:
            role = guild.get_role(school)
            if role:
                res['roles'].append(role)
            else:
                del self.bot.data['school_roles'][letter][self.bot.data['school_roles'][letter].index(school)]
                self.bot.data_manager.save_data()

        res['roles'] = sorted(res['roles'], key = lambda x: x.name)

        return res



""" Function | Setup

The function called by Discord.py when adding another file in a multi-file project.
"""
def setup(bot):
    bot.add_cog(SchoolRoles(bot))
