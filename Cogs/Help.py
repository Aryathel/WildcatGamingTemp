import discord
from discord.ext import commands, menus
import datetime

"""Help Command Paginator

This class is used to create a paginated help command.
"""
class HelpSource(menus.ListPageSource):
    def __init__(self, ctx, fields, per_page = 3):
        self.ctx = ctx
        self.num_fields = int(len(fields) / per_page)
        if len(fields) % per_page:
            self.num_fields += 1
        super().__init__(fields, per_page = per_page)

    async def format_page(self, menu, entries):
        offset = menu.current_page * self.per_page

        embed = self.ctx.bot.embed_util.get_embed(
            title = f"\N{NEWSPAPER} Help Menu [{menu.current_page + 1}/{self.num_fields}]",
            desc = f"A listing of all available commands sorted by grouping.\nTo learn more about specific commands, use `{self.ctx.bot.prefix}help <command>`",
            fields = [field for i, field in enumerate(entries, start = offset)],
            footer = f"{self.ctx.bot.footer}"
        )
        return embed

"""Custom Help Command

Contains all of the features for a custom help message depending on certain
values set when defining a command in the first place.

NOTE: Users who use the help command can only see commands that they are actually allowed to use in permissions.
Similarly, any commands that have `hidden=True` in their decorator are hidden.
"""
class TheHelpCommand(commands.MinimalHelpCommand):
    async def send_bot_help(self, mapping):
        """Send a help list for all of the bot commands.

        Is now using pagination as well.
        """
        fields = []
        # Parsing through all cogs and all commands contained within each command.
        for cog in mapping.keys():
            if cog:
                command_list = await self.filter_commands(mapping[cog], sort = True)
                if len(command_list) > 0:
                    # If a cog contains visible commands, add the to an embed field.
                    fields.append({
                        "name": cog.qualified_name,
                        "value": f"{cog.description}\nCommands:\n" + ", ".join(f"`{command}`" for command in command_list),
                        "inline": False
                    })

        # Create the paginated help menu
        pages = menus.MenuPages(source = HelpSource(self.context, fields), delete_message_after = True)
        await pages.start(self.context)

    async def send_cog_help(self, cog):
        """Cog Specific

        Sends help for all commands contained within a cog, by
        cog name.
        """
        embed = self.context.bot.embed_util.get_embed(
            title = f"{cog.qualified_name} Help",
            desc = f"{cog.description}\nTo learn more about specific commands, use `{self.clean_prefix}help <command>`",
            author = self.context.message.author,
            fields = [{
                "name": "Commands",
                "value": "\n".join("`{1.qualified_name}`".format(self, command) for command in cog.walk_commands() if not command.hidden),
                "inline": False
            }]
        )
        await self.get_destination().send(embed = embed)

    async def send_group_help(self, group):
        """Grouped Commands

        Sends help message for all commands grouped in a parent command.
        """
        command_list = group.walk_commands()
        command_activation = []
        command_example = []
        for command in command_list:
            if "`" + command.qualified_name + " " + command.signature + "` - {}".format(command.help) not in command_activation and not command.hidden:
                command_activation.append("`" + command.qualified_name + " " + command.signature + "` - {}".format(command.help))
                if command.brief not in [None, ""]:
                    command_example.append("`" + self.clean_prefix + command.qualified_name + " " + command.brief + "`")
                else:
                    command_example.append("`" + self.clean_prefix + command.qualified_name + "`")

        fields = []
        if group.aliases:
            fields.append({
                "name": "Aliases",
                "value": ", ".join('`{}`'.format(alias) for alias in group.aliases),
                "inline": False
            })
        fields.append({
            "name": "Commands",
            "value": "\n".join(command_activation),
            "inline": False
        })
        fields.append({
            "name": "Examples",
            "value": "\n".join(command_example),
            "inline": False
        })

        embed = self.context.bot.embed_util.get_embed(
            title = f"'{group.qualified_name.capitalize()}' Help",
            desc = f"{group.help}\n\nFor more information on each command, use `{self.clean_prefix}help [command]`.",
            fields = fields,
            author = self.context.message.author
        )
        await self.get_destination().send(embed = embed)

    async def send_command_help(self, command):
        """Command Specific

        Send help for a specific given single command.
        """
        fields = []
        if command.aliases:
            fields.append({
                "name": "Aliases",
                "value": ", ".join('`{}`'.format(alias) for alias in command.aliases),
                "inline": False
            })
        fields.append({
            "name": "Usage",
            "value": f"`{self.clean_prefix}{command.qualified_name}{' ' + command.signature if command.signature else ''}`",
            "inline": False
        })
        fields.append({
            "name": "Example",
            "value": f"`{self.clean_prefix}{command.qualified_name}{' ' + command.brief if command.brief else ''}`",
            "inline": False
        })

        embed = self.context.bot.embed_util.get_embed(
            title = f"'{command.name.capitalize()}' Help",
            desc = f"{command.help}",
            fields = fields,
            author = self.context.message.author
        )
        await self.get_destination().send(embed = embed)

"""Class | Help Loader

The actual discord cog that is loaded when this file is added, simply wrapping the help command.
"""
class LoadHelp(commands.Cog, name = "Help"):
    """
    Get help for all cogs/commands.
    """
    def __init__(self, bot):
        self._original_help_command = bot.help_command
        bot.help_command = TheHelpCommand()
        bot.help_command.cog = self
        print(f"{bot.OK} {bot.TIMELOG()} Loaded Help Cog.")

    """ Method | Cog Unload

    Called when the cog is unloaded from the system.
    """
    def cog_unload(self):
        print(f"{self.bot.OK} {self.bot.TIMELOG()} Unloaded Help Cog.")

def setup(bot):
    """Setup

    The function called by Discord.py when adding another file in a multi-file project.
    """
    bot.add_cog(LoadHelp(bot))
