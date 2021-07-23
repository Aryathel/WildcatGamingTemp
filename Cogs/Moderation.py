import discord
from discord.ext import commands, tasks
import datetime
from enum import Enum

from Resources.Utility import TimeLength

class LogType(Enum):
    mute = "mute"
    unmute = "unmute"
    member_ban = "member ban"
    member_unban = "member unban"
    member_join = "member join"
    member_leave = "member leave"
    member_update = "member update"
    stats = "stats"
    twitter = "twitter"
    role_reaction = "role reaction"
    school_roles = "school roles"
    custom_messages = "custom messages"
    errors = "errors"

"""Cog | Moderation

This Cog contains commands and listeners pertaining to
user moderation and automatic moderation.

Commands:
<> indicates required arg
[] indicates optional arg
----------
mute <user> [length] - Assigns a role to the specified user which prevents them
    from sending messages. The role will either be removed when the unmute command
    is used, or automatically if a time for unmuting is specified.
"""
class Moderation(commands.Cog, name = "Moderation"):
    """Commands pertaining to user moderation."""

    """ Method | Init

    This function is called when the Cog is loaded.
    """
    def __init__(self, bot):
        # Give access to the Bot instance.
        self.bot = bot

        # Make sure moderation data is initialized.
        save = False
        if not "logs" in self.bot.data:
            self.bot.data["logs"] = {}
            save = True
        if not "mute" in self.bot.data:
            self.bot.data['mute'] = {
                "role": self.bot.muted_role_id,
                "mutes": []
            }
            self.bot.data['logs']['mute'] = self.bot.log_channel_id
            self.bot.data['logs']['unmute'] = self.bot.log_channel_id
            save = True
        if not "member_join" in self.bot.data['logs']:
            self.bot.data['logs']['member_join'] = self.bot.log_channel_id
            save = True
        if not "member_leave" in self.bot.data['logs']:
            self.bot.data['logs']['member_leave'] = self.bot.log_channel_id
            save = True
        if not "member_update" in self.bot.data['logs']:
            self.bot.data['logs']['member_update'] = self.bot.log_channel_id
            save = True
        if not "member_ban" in self.bot.data['logs']:
            self.bot.data['logs']['member_ban'] = self.bot.log_channel_id
            save = True
        if not "member_unban" in self.bot.data['logs']:
            self.bot.data['logs']['member_unban'] = self.bot.log_channel_id
            save = True
        if not "stats" in self.bot.data['logs']:
            self.bot.data['logs']['stats'] = self.bot.log_channel_id
            save = True
        if not "twitter" in self.bot.data['logs']:
            self.bot.data['logs']['twitter'] = self.bot.log_channel_id
            save = True
        if not "role_reaction" in self.bot.data['logs']:
            self.bot.data['logs']['role_reaction'] = self.bot.log_channel_id
            save = True
        if not "school_roles" in self.bot.data['logs']:
            self.bot.data['logs']['school_roles'] = self.bot.log_channel_id
            save = True
        if not "custom_messages" in self.bot.data['logs']:
            self.bot.data['logs']['custom_messages'] = self.bot.log_channel_id
            save = True
        if not "errors" in self.bot.data['logs']:
            self.bot.data['logs']['errors'] = self.bot.log_channel_id
            save = True
        if save:
            self.bot.data_manager.save_data()

        # Start moderation tasks.
        self.check_mutes.start()
        self.server_stats.start()

        print(f"{bot.OK} {bot.TIMELOG()} Loaded Moderation Cog.")


    """ Method | Unload

    This function is called when the Cog is unloaded.
    """
    def cog_unload(self):
        # Stop the moderation tasks gracefully.
        self.check_mutes.cancel()
        self.server_stats.cancel()

        print(f"{self.bot.OK} {self.bot.TIMELOG()} Unloaded Moderation Cog.")


    """ Command Group | Logs

    This command group is used to change the channels that certain types of logs will go to,
    and to display where all current logs are going to.
    """
    @commands.guild_only()
    @commands.group(name = "logs", aliases = ['log'], help = "View all registered log channels.", brief = "", invoke_without_command = True)
    async def logs(self, ctx):
        # Format an embed with all registered log channels.
        embed = self.bot.embed_util.get_embed(
            title = "Log Channels",
            desc = f"Use `{self.bot.prefix}logs edit log_type #channel` to change what channel a log type uses.",
            fields = [{"name": " ".join(s.capitalize() for s in getattr(LogType, log).value.split(" ")), "value": self.bot.get_channel(self.bot.data['logs'][log]).mention} for log in sorted(LogType._member_map_)]
        )

        await ctx.send(embed = embed)


    """ Command | Edit Log

    This command is used to change the channels that certain types of logs will go to.

    Args:
        - type (LogType):
            The type of mod action to update the channel for.
        - channel (discord.TextChannel):
            Either a mention, case sensitive name, or ID of a text channel to put the logs in.
    """
    @commands.guild_only()
    @logs.command(name = "edit", help = "Edit a registered log channel.", brief = "type #channel")
    async def edit_logs(self, ctx, type: str, channel: discord.TextChannel):
        # Make sure that the entered Log Type is valid.
        try:
            type = LogType(type.lower().replace('_', ' '))
        except ValueError as e:
            embed = self.bot.embed_util.get_embed(
                title = "Type Not Recognized",
                desc = f"The log type `{type}` is not recognized, please retry with a valid log type.",
                fields = [
                    {
                        "name": "Valid Log Types",
                        "value": "\n".join([f"`{log}`" for log in LogType._member_names_])
                    }
                ]
            )
            await ctx.send(embed = embed)
            return

        # Make sure that the new Log Channel is not the same as the one that is already registered.
        if self.bot.data['logs'][type.name] == channel.id:
            embed = self.bot.embed_util.get_embed(
                title = "Channel ALready Registered",
                desc = f"The log type `{type.name}` is already tied to the {channel.mention} channel."
            )
            await ctx.send(embed = embed)
            return

        # Register the new log channel.
        old_channel = self.bot.get_channel(self.bot.data['logs'][type.name])
        self.bot.data['logs'][type.name] = channel.id
        self.bot.data_manager.save_data()

        # Format the embed confirming the log channel update.
        embed = self.bot.embed_util.get_embed(
            title = f"{' '.join(s.capitalize() for s in type.value.split(' '))} Log Channel Updated",
            fields = [
                {
                    "name": "New Channel",
                    "value": channel.mention,
                    "inline": False
                },
                {
                    "name": "Old Channel",
                    "value": old_channel.mention,
                    "inline": False
                }
            ]
        )
        # Log the Log Channel update.
        if ctx.channel.id == self.bot.log_channel_id:
            embed.set_author(
                name = ctx.author.name,
                icon_url = ctx.author.avatar_url
            )
            await ctx.send(embed = embed)
        else:
            await ctx.send(embed = embed)
            embed.set_author(
                name = ctx.author.name,
                icon_url = ctx.author.avatar_url
            )
            await self.bot.log_channel.send(embed = embed)


    """ Command | Mute

    This command is used to mute a specified user. This mute can either be indefinite,
    or have a specified length of time to mute a use for.

    Args:
        - user (discord.Member):
            The server member who is to be muted. Accepts a mention, case sensitive username, or a Discord user ID.
        - length (Optional[str]):
            An optional string argument which specifies how long to mute a user for.
    """
    @commands.guild_only()
    @commands.command(name = "mute", help = "Prevents a user from sending messages either indefinitely or for a set amount of time.", brief = "@username 1h 2m 30s")
    async def mute(self, ctx, user: discord.Member, *, length = None):
        # Get the Muted role.
        role = ctx.guild.get_role(self.bot.data['mute']['role'])

        # Give the user the role if they do not have it.
        if not role in user.roles:
            await user.add_roles(role)

        # If there is a time specified, register the time to remove the mute.
        other = None
        if length:
            time_data = TimeLength(length)

            self.bot.data['mute']['mutes'].append({
                "id": user.id,
                "time": (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
                    days = time_data.days,
                    hours = time_data.hours,
                    minutes=  time_data.minutes
                )).isoformat(),
                "guild": ctx.guild.id
            })

            self.bot.data_manager.save_data()

            other = f"Muted for {time_data.days} days, {time_data.hours} hours, and {time_data.minutes} minutes."

        # Format an embed to log the mute.
        embed = self.bot.embed_util.get_embed(
            title = "User Muted",
            desc = f"{user} was muted."
        )
        await ctx.send(embed = embed)

        # Send the mute information to the Mute log channel.
        await self.log_mod_action(ctx, LogType('mute'), user, other)


    """ Command | Unmute

    This command is used to unmute a muted user.

    Args:
        - user (discord.Member):
            The user to unmute.
    """
    @commands.guild_only()
    @commands.command(name = "unmute", help = "Unmutes a muted member.", brief = "@user")
    async def unmute(self, ctx, user: discord.Member):
        # Get the Muted role.
        role = ctx.guild.get_role(self.bot.data['mute']['role'])

        # If the user has the role, remove it.
        if role in user.roles:
            await user.remove_roles(role)

            self.clear_mutes(user)

            # Log the unmute.
            embed = self.bot.embed_util.get_embed(
                title = "User Unmuted",
                desc = f"{user} was unmuted."
            )
            await ctx.send(embed = embed)

            await self.log_mod_action(ctx, LogType('unmute'), user)

        else:
            # If the user was not muted.
            embed = self.bot.embed_util.get_embed(
                title = "User Already Unmuted",
                desc = f"{user.name} is not muted."
            )
            await ctx.send(embed = embed)


    """ Loop | Check Mute Status

    This is a function which is triggered every 50 seconds after the bot is online,
    it will check to see if any users that were given a mute on a timer need to be unmuted.
    """
    @tasks.loop(seconds = 50)
    async def check_mutes(self):
        # Loop through all mutes that are on a timer.
        for user in self.bot.data['mute']['mutes']:
            # Check if the mute timer is done.
            now = datetime.datetime.now(datetime.timezone.utc)
            if now > datetime.datetime.fromisoformat(user['time']):
                # Get the user object and remove the mutedrole from them.
                guild = self.bot.get_guild(user['guild'])
                member = guild.get_member(user['id'])

                role = guild.get_role(self.bot.data['mute']['role'])
                if role in member.roles:
                    await member.remove_roles(role)

                    # Log the mute timer ending.
                    embed = self.bot.embed_util.get_embed(
                        title = "Mute Timer Ended",
                        desc = f"{member.name}'s mute timer ended.",
                        ts = True
                    )
                    channel = self.bot.get_channel(self.bot.data['logs'][LogType.unmute.name])
                    await channel.send(embed = embed)


    """ Event Listener | Member Join

    Triggers every time a member joins, sends a message to the user who joined,
    and logs their arrival in the "join" log channel.
    """
    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Format the embed for the given member's arrival, as well as the total server member count.
        embed = self.bot.embed_util.get_embed(
            desc = f"\N{INBOX TRAY} `{member}` has joined the server. {member.mention}",
            footer = f"Online: {len([member for member in member.guild.members if member.status in [discord.Status.online, discord.Status.idle, discord.Status.dnd]])} | Total: {member.guild.member_count}",
            ts = True
        )
        channel = self.bot.get_channel(self.bot.data['logs'][LogType.member_join.name])
        await channel.send(embed = embed)


    """ Event Listener | Member Leave

    Triggers every time a member leave,
    logging their leaving in the "leave" log channel.
    """
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        # Clear the mute of a member to not break the mute checking.
        self.clear_mutes(member)

        # Format the embed for the given member's leave, as well as the total server member count.
        embed = self.bot.embed_util.get_embed(
            desc = f"\N{OUTBOX TRAY} `{member}` has left the server.",
            footer = f"Online: {len([member for member in member.guild.members if member.status in [discord.Status.online, discord.Status.idle, discord.Status.dnd]])} | Total: {member.guild.member_count}",
            ts = True
        )

        channel = self.bot.get_channel(self.bot.data['logs'][LogType.member_leave.name])
        await channel.send(embed = embed)


    """ Event Listener | Member Update

    Triggers whenever a member is updated, whether that be name, status, activity, or roles.

    Currently is only used to track role changes.
    """
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if not before.roles == after.roles:
            added = []
            removed = []
            for role in before.roles:
                if not role in after.roles:
                    removed.append(role)

            for role in after.roles:
                if not role in before.roles:
                    added.append(role)

            fields = [{
                "name": "Member Updated",
                "value": f"{after} | {after.mention}"
            }]
            if len(added) > 0:
                fields.append({
                    "name": "Roles Added",
                    "value": "\n".join(role.mention for role in added),
                    "inline": False
                })
            if len(removed) > 0:
                fields.append({
                    "name": "Roles Removed",
                    "value": "\n".join(role.mention for role in removed),
                    "inline": False
                })
            embed = self.bot.embed_util.get_embed(
                title = "Member Roles Updates",
                fields = fields,
                ts = True
            )

            channel = self.bot.get_channel(self.bot.data['logs'][LogType.member_update.name])
            await channel.send(embed = embed)


    """ Event Listener | Member Ban

    This listener is triggered when a member is banned from the server.
    """
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        embed = self.bot.embed_util.get_embed(
            title = "Member Banned",
            desc = f"User `{user}` was banned from `{guild.name}`.",
            ts = True
        )

        channel = self.bot.get_channel(self.bot.data['logs'][LogType.member_ban.name])
        await channel.send(embed = embed)


    """ Event Listener | Member Unban

    This listener is triggered when a member is unbanned from the server.
    """
    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        embed = self.bot.embed_util.get_embed(
            title = "Member Unbanned",
            desc = f"User `{user}` was unbanned from `{guild.name}`.",
            ts = True
        )

        channel = self.bot.get_channel(self.bot.data['logs'][LogType.member_unban.name])
        await channel.send(embed = embed)


    """ Loop | Server Stats

    Sends stats about the server to the server analytics
    channel every 24 hours after the bot comes online.
    """
    @tasks.loop(hours=24)
    async def server_stats(self):
        # Get the channel to log server stats to.
        channel = self.bot.get_channel(self.bot.data['logs'][LogType.stats.name])
        guild = channel.guild

        # Format the server stats message.
        embed = self.bot.embed_util.get_embed(
            title = f"{guild.name}",
            thumbnail = guild.icon_url,
            ts = True,
            fields = [
                {
                    "name": "Server Created Date",
                    "value": f"`{guild.created_at.strftime('%m/%d/%Y | %I:%M:%S %p')}`",
                    "inline": False
                },
                {
                    "name": "Days Since Then",
                    "value": f"`{abs((guild.created_at - datetime.datetime.now()).days)}`",
                    "inline": False
                },
                {
                    "name": "Region",
                    "value": f"`{guild.region}`",
                    "inline": True
                },
                {
                    "name": "Users",
                    "value": f"`Online: {len([member for member in guild.members if member.status in [discord.Status.online, discord.Status.idle, discord.Status.dnd]])}` `Total: {guild.member_count}`",
                    "inline": True
                },
                {
                    "name": "Text Channels",
                    "value": f"`{len(guild.text_channels)}`",
                    "inline": True
                },
                {
                    "name": "Voice Channels",
                    "value": f"`{len(guild.voice_channels)}`",
                    "inline": True
                },
                {
                    "name": "Roles",
                    "value": f"`{len(guild.roles)}`",
                    "inline": True
                },
                {
                    "name": "Owner",
                    "value": f"{guild.owner.mention}",
                    "inline": True
                }
            ]
        )
        await channel.send(embed = embed)


    """ Check | Before Loops

    A check function that is executed before any loops are started,
    is used to verify that the bot is online, connected to Discord, and receiving data.
    """
    @check_mutes.before_loop
    @server_stats.before_loop
    async def before_check_mutes(self):
        # Wait until the bot is online and connected ot discord.
        await self.bot.wait_until_ready()


    """ Method | Log Moderator Action

    This method is called when any moderator actions are used, in order to log the information of said action.
    The logging methods vary based on the type of action taken.

    Args:
        - ctx (discord.Context):
            The context of the mod action taken, used to pull information about the time of the mod action
            and who called the mod action.
        - type (LogType):
            An enum representing the type of moderation action to be logged.
        - target (discord.User):
            The user who is the target of the given mod action.
        - other (Optional[int]):
            Any extra informatino to be noted about an action.
    """
    async def log_mod_action(self, ctx, type, target, other = None):
        # Logging the mod action in the command line.
        print(f"{self.bot.OK} {self.bot.TIMELOG()} New Moderation Action:")
        print(f"{' '*35} Action Type: {type.name.capitalize()}")
        print(f"{' '*35} Moderator: {ctx.author} | ID: {ctx.author.id}")
        print(f"{' '*35} Target: {target} | ID: {target.id}")

        # Creating information fields for an embedded message
        fields = [
            {
                "name": "Action Type",
                "value": f"`{type.name.capitalize()}`",
                "inline": False
            },
            {
                "name": "Moderator",
                "value": f"`{ctx.author}`",
                "inline": True
            },
            {
                "name": "Target",
                "value": f"`{target}`",
                "inline": True
            }
        ]

        # Adding extra information.
        if other:
            print(f"{' '*35} Other Information: {other}")
            fields.append({
                "name": "Other Info",
                "value": other,
                "inline": False
            })

        # Creating the actual embedded message.
        embed = self.bot.embed_util.get_embed(
            title = "New Moderation Action",
            fields = fields,
            ts = True
        )

        # Sending the message to the channel for the specific action type.
        channel = self.bot.get_channel(self.bot.data['logs'][type.name])
        await channel.send(embed = embed)

    """ Method | Clear Mute Data

    Clears the active mute timer for a given user.
    """
    def clear_mutes(self, user):
        # If the user had a mute timer that is being overridden by this, end it.
        if user.id in [u['id'] for u in self.bot.data['mute']['mutes']]:
            for i, u in enumerate(self.bot.data['mute']['mutes']):
                if user.id == u['id']:
                    break

            del self.bot.data['mute']['mutes'][i]
            self.bot.data_manager.save_data()

""" Function | Setup

The function called by Discord.py when adding another file in a multi-file project.
"""
def setup(bot):
    cog = Moderation(bot)
    cog.__cog_description__ = "Commands pertaining to user moderation and automated moderation systems."
    bot.add_cog(cog)
