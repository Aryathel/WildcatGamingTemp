"""Library Imports

Standard Library Modules:
    asynncio:
        Allows for multiple tasks to happen at the same time and maintains the discord connection gateway
    datetime:
        For, well... date and time
    os:
        A standardized set of operations pertaining to operating systems (file operations, environment variables, etc)

3rd Party Modules:
    colorama:
        Used for coloring console/terminal output, makes things pretty
    discord:
        A complete wrapper for the Discord API
    yaml:
        A module for reading yaml files, used to read the config in this case

Local Modules:
    (their names correspond with internal file structure as well)

    Resources:
        Data:
            DataManager:
                The data manager class, which is used to... manage data. Primarily persisting data between restarts and loading the config.
        Utility:
            EmbedUtil:
                The utility class for creating and handling the Discord embedded message formatting.
            Confirmation:
                The utility class for giving users a confirmation menu.
"""

# standard python modules
import asyncio
import datetime
import os

# 3rd party modules
import discord
from discord.ext import commands
import yaml
from colorama import init
init()

# local modules
from Resources.Data import DataManager
from Resources.Utility import EmbedUtil, Confirmation

def get_prefix(bot, message):
    """Allows for a dynamic prefix option to be anabled for the bot.

    The 'prefix' command can update the bot prefix in this way, if enabled.

    Parameters:
        - bot (:class:`Discord.Client`) -
            An instance of the discord client which is automatically passed in by the client
            when retrieving the prefix.
        - message (:class:`Discord.Message`) -
            An instance of a discord Message, which can be used to determine the prefix depending on a variety of situations,
            such as differing prefixes for channels, or guilds.
    """
    return bot.prefix

# Allows the Discord client to see all Members, Roles, etc by default.
intents = discord.Intents.default()
intents.members = True
intents.presences = True

# Create the 'bot' instance, using the fucntion above for getting the prefix.
bot = commands.Bot(command_prefix=get_prefix, description="Heroicos_HM's Custom Bot", case_insensitive = True, intents = intents)

# Remove the help command to leave room for implementing a custom one.
bot.remove_command('help')

# Give the bobt global access to the yaml reading module.
bot.yaml = yaml

"""Initial Data Loading/Prep

Create a DataManager instance, then call pertinent loading functions.

Then, create an instance of the Embed tool for use later.
The bot's config and data contain information
"""
bot.data_manager = DataManager(bot)
bot.data_manager.load_config()
bot.data_manager.load_permissions()
bot.data_manager.load_data()

bot.embed_util = EmbedUtil(bot)

# List of extension files to load.
bot.exts = [
    'Cogs.General',
    'Cogs.Help',
    # 'Cogs.Moderation',
    # 'Cogs.Twitter',
    'Cogs.RoleReactions',
    # 'Cogs.SchoolRoles',
    # 'Cogs.Messages',
    # 'Cogs.Tickets'
]

# Check if the bot is meant to be run in DEBUG mode.
# When DEBUG mode is inactive, error logging to the console is limited,
# but the error logs are also shown in Discord as well.
if bot.DEBUG:
    # Print to the user that the bot will run in Debug mode.
    print(f"{bot.WARN} {bot.TIMELOG()} Debug mode active.")
else:
    # Adds the custom error logging if no in debug mode.
    bot.exts.append('Cogs.Errors')

# Load the extension files listed above.
for extension in bot.exts:
    bot.load_extension(extension)

print(f"{bot.OK} {bot.TIMELOG()} Connecting to Discord...")

@bot.event
async def on_ready():
    """Triggers once the bot has established a Discord gateway connection successfully.

    WARNING: This function can be triggered multiple times, make sure anything in here can accept that.

    Sets up any configuration for the bot that requires a Discord connection first.
    """
    # Get the log channel object first, this allows logging to happen without having to retrieve the channel every time.
    bot.log_channel = bot.get_channel(bot.log_channel_id)

    # Print the connection message.
    print(f"{bot.OK} {bot.TIMELOG()} Logged in as {bot.user} and connected to Discord! (ID: {bot.user.id})")

    # Set the "playing" status of the bot to what is set in the config.
    if bot.show_game_status:
        # Create an instance of a Game for the bot to be playing, set to whatever text that is to be shown.
        game = discord.Game(name=bot.game_to_show.format(prefix = bot.prefix))
        # Show that text.
        await bot.change_presence(activity=game)

    # Create online message using the embed utility.
    embed = bot.embed_util.get_embed(
        title=bot.online_message.format(username=bot.user.name),
        ts=True
    )

    # Send the embed "online" message to the log channel.
    await bot.log_channel.send(embed = embed)

    # Set the bot start time for use in the uptime command.
    bot.start_time = bot.embed_ts()

@bot.check
async def command_permissions(ctx):
    """Global Permission Manager

    By setting this with the @bot.check attribute, this function is attached globally to all commands.

    When a comand is used this function will use the permissions imported
    from Permissions.yml to verify that a user is/is not allowed
    to use a command.
    """
    # Administrators are always allowed to use the command.
    if ctx.author.guild_permissions.administrator:
        return True
    else:
        # Finding permission name scheme of a command.
        # e.g. "!command" is "command" and "!category command" is "category-command"
        name = ctx.command.name
        if ctx.command.parent:
            command = ctx.command
            parent_exists = True
            while parent_exists == True:
                name = ctx.command.parent.name + '-' + name
                command = ctx.command.parent
                if not command.parent:
                    parent_exists = False

        """Checking command permissions

        For each role ID listed for a command, check if the user has that role id.

        If they do, allow command usage, otherwise, proceed to checking next role on the list.

        If the user does not have any of the roles, deny the command usage.
        """
        if name in ctx.bot.permissions.keys():
            for permission in ctx.bot.permissions[name]:
                try:
                    role = ctx.guild.get_role(int(permission))
                    if role in ctx.author.roles:
                        return True
                except Exception as e:
                    print(e)
            return False
        else:
            return True

class Internal(commands.Cog, name = "Internal"):
    """
    Commands related to internal management.
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name = "restart", help = "Restarts the bot.", brief = "")
    async def restart(self, ctx):
        """Restarts the bot.

        Sends a message to the log channel, adds a reaction to the message, then
        attempts to gracefully disconnect from Discord.

        Either a Batch or Shell script (depending on operating system) will then
        re-activate the bot, which allows the bot to take in file updates on the fly.
        """
        # Confirm that the user wants to restart
        confirm = await Confirmation(
            title = "Restart?",
            msg = "This will completely shut down the bot and potentially cause errors if the code has been modified and not tested."
        ).prompt(ctx)

        if confirm:
            embed = self.bot.embed_util.get_embed(
                title = self.bot.restarting_message.format(username = self.bot.user.name),
                ts = True,
                author = ctx.author
            )
            await self.bot.log_channel.send(embed = embed)

            try:
                await ctx.message.add_reaction('\N{WHITE HEAVY CHECK MARK}')
            except:
                pass

            for extension in self.bot.exts:
                self.bot.remove_cog(extension)

            await self.bot.close()
            sys.exit()
        else:
            embed = self.bot.embed_util.get_embed(
                title = "Restart Cancelled"
            )
            m = await ctx.send(embed = embed)
            await asyncio.sleep(5)
            await m.delete()

    """ DISABLED UNTIL NEW PREFIX COMMAND IS FIGURED OUT. SHOULDN'T BE NECESSARY FOR BOTS ONLY RUNNING IN A SINGLE SERVER
    @commands.guild_only()
    @commands.command(name = "prefix", help = "Changes the command prefix for the bot.", brief = "?")
    async def prefix(self, ctx, prefix: str):
        if self.bot.delete_commands:
            await ctx.message.delete()

        old = self.bot.prefix
        self.bot.config['Prefix'] = prefix
        with open('./Config.yml', 'w') as file:
            self.bot.yaml.dump(self.bot.config, file)

        self.bot.prefix = prefix
        if self.bot.show_game_status:
            game = discord.Game(name = self.bot.game_to_show.format(prefix = self.bot.prefix))
            await self.bot.change_presence(activity = game)

        embed = self.bot.embed_util.get_embed(
            title = "Prefix Updated",
            desc = f"New Prefix: `{self.bot.prefix}`",
            fields = [
                {"name": "New", "value": f"{self.bot.prefix}command", "inline": True},
                {"name": "Old", "value": f"{old}command", "inline": True},
            ],
            author = ctx.author
        )
        await ctx.send(embed = embed)
        embed = self.bot.embed_util.update_embed(embed, ts = True, author = ctx.author)
        await self.bot.log_channel.send(embed = embed)
    """

    @commands.group(name = 'cog', aliases=['cogs'], help = "A group of commands for loading, unloading, and reloading cogs.", invoke_without_command=True)
    async def cog(self, ctx):
        """The parent command for all commands related to cogs.
        """
        pass

    @cog.command(name = 'load', help = 'Load a cog by name.', brief = "Cogs.General")
    async def load(self, ctx, cog_name):
        """Loading a cog.

        Loads a cog into the system by name. Folder path separators are replaced by "."
        """
        try:
            if cog_name in self.bot.cog_exts:
                self.bot.reload_extension(cog_name)
                embed = self.bot.embed_util.get_embed(
                    title = f"Loaded {cog_name}",
                    author = ctx.author,
                )
                await ctx.send(embed = embed)
                embed = self.bot.embed_util.update_embed(
                    embed = embed,
                    ts = True
                )
                await self.bot.log_channel.send(embed = embed)
            else:
                raise
        except Exception as e:
            embed = self.bot.embed_util.get_embed(
                title = f"Failed to load {cog_name}",
                author = ctx.author,
            )
            await ctx.send(embed = embed)
            embed = self.bot.embed_util.update_embed(
                embed = embed,
                desc = str(e),
                author = ctx.author,
                ts = True
            )
            await self.bot.log_channel.send(embed = embed)

    @cog.command(name = 'unload', help = 'Unload a cog by name.', brief = "Cogs.General")
    async def unload(self, ctx, cog_name):
        """Unload a cog.

        Turns off a registered cog by name.
        """
        try:
            if cog_name in self.bot.cog_exts:
                self.bot.remove_cog(cog_name.split('.')[-1])
                embed = self.bot.embed_util.get_embed(
                    title = f"Unloaded {cog_name}",
                    author = ctx.author,
                )
                await ctx.send(embed = embed)
                embed = self.bot.embed_util.update_embed(
                    embed = embed,
                    ts = True
                )
                await self.bot.log_channel.send(embed = embed)
            else:
                raise
        except:
            embed = self.bot.embed_util.get_embed(
                title = f"Failed to unload {cog_name}",
                author = ctx.author,
            )
            await ctx.send(embed = embed)

    @cog.command(name = 'reload', help = 'Reload a cog by name.', brief = "Cogs.General")
    async def reload(self, ctx, cog_name):
        """Reload a specific cog.

        Can be used to register updates to a cog without needing to restart the entire bot.

        Essentially just unloads and then reloads a cog.
        """
        try:
            if cog_name in self.bot.cog_exts:
                self.bot.reload_extension(cog_name)
                embed = self.bot.embed_util.get_embed(
                    title = f"Reloaded {cog_name}",
                    author = ctx.author,
                )
                await ctx.send(embed = embed)
                embed = self.bot.embed_util.update_embed(
                    embed = embed,
                    ts = True
                )
                await self.bot.log_channel.send(embed = embed)
            else:
                raise
        except Exception as e:
            embed = self.bot.embed_util.get_embed(
                title = f"Failed to reload {cog_name}",
                author = ctx.author,
            )
            await ctx.send(embed = embed)
            embed = self.bot.embed_util.update_embed(
                embed = embed,
                desc = str(e),
                author = ctx.author,
                ts = True
            )
            await self.bot.log_channel.send(embed = embed)

# Register the internal cogs as a cog.
bot.add_cog(Internal(bot))

# Run the bot, or print an error if the bot's token is invalid.
try:
    bot.run(bot.TOKEN, bot = True, reconnect = True)
except discord.LoginFailure:
    print(f"{bot.ERR} {bot.TIMELOG()} Invalid TOKEN Variable: {bot.TOKEN}")
    input("Press enter to continue.")
