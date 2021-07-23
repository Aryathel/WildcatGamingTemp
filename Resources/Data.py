"""Resource | Data Manager

This class manages all of the loading and
saving of the config, permissions, and data.
"""
import json
import os
from discord import Color
from colorama import Fore
import datetime

""" Class | Data Manager

This class is used to, well, manage data. Specifically any data pertaining to
the bot's config, as well as data storage for persisting data between restarts.
"""
class DataManager:
    def __init__(self, bot):
        self.bot = bot

    """ Setup | Bot Config

    Loading Config variables into bot attributes.

    See 'Config.yml' for specifics on each setting.
    """
    def load_config(self):
        with open("./Config.yml", 'r') as file:
            config = self.bot.yaml.load(file, Loader = self.bot.yaml.Loader)

        # Save config files to the bot.
        self.bot.config = config

        # Main Settings
        self.bot.TOKEN               = os.getenv(config['Token Env Var'])
        self.bot.DEBUG               = config['DEBUG']
        self.bot.prefix              = config['Prefix']
        self.bot.online_message      = config['Online Message']
        self.bot.restarting_message  = config['Restarting Message']
        self.bot.data_file           = os.path.abspath(config['Data File'])
        self.bot.show_game_status    = config['Game Status']['Active']
        self.bot.game_to_show        = config['Game Status']['Game']
        self.bot.log_channel_id      = config['Log Channel']

        # Embed Options
        self.bot.embed_color = Color.from_rgb(
            config['Embed Settings']['Color']['r'],
            config['Embed Settings']['Color']['g'],
            config['Embed Settings']['Color']['b']
        )
        self.bot.footer =              config['Embed Settings']['Footer']['Text']
        self.bot.footer_image =        config['Embed Settings']['Footer']['Icon URL']
        self.bot.delete_commands =     config['Embed Settings']['Delete Commands']
        self.bot.show_command_author = config['Embed Settings']['Show Author']
        self.bot.embed_ts =            lambda: datetime.datetime.now(datetime.timezone.utc)

        # Logging Variables
        self.bot.OK = f"{Fore.GREEN}[OK]{Fore.RESET}  "
        self.bot.WARN = f"{Fore.YELLOW}[WARN]{Fore.RESET}"
        self.bot.ERR = f"{Fore.RED}[ERR]{Fore.RESET} "
        self.bot.TIMELOG = lambda: datetime.datetime.now().strftime('[%m/%d/%Y | %I:%M:%S %p]')

    """ Setup | Command Permissions

    Loading Permission variables into bot attributes.

    See 'Permissions.yml' for specifics on each setting.
    """
    def load_permissions(self):
        bot_permissions = {}
        with open("./Permissions.json", 'r') as file:
            permissions = json.load(file)
            # Raw permission input is formatted to have role IDs in place.
            roles = dict(permissions['roles'])
            for key in permissions["permissions"].keys():
                bot_permissions[key] = []
                for permission in permissions["permissions"][key]:
                    bot_permissions[key].append(permission.format(**roles))

        self.bot.permissions = bot_permissions

    """ Data | Saving

    Open the data file and save the bot's data to it.

    Overwrites previous data in file.
    """
    def save_data(self):
        with open(self.bot.data_file, 'w+', encoding = "utf-8") as save_file:
            try:
                save_file.write(json.dumps(self.bot.data, indent = 2))
            except Exception as e:
                print('Could not save data: ' + str(e))

    """ Data | Loading

    Check if the data file exists, if it does, load it, if not, create it.

    If the data file exists but has not data, give it a new empty data object.
    """
    def load_data(self):
        if os.path.exists(self.bot.data_file):
            with open(self.bot.data_file, 'r', encoding = "utf-8") as file:
                content = file.read()
                if len(content) == 0:
                    self.bot.data = {}
                    self.save_data()
                else:
                    self.bot.data = json.loads(content)
        else:
            self.bot.data = {}
            self.save_data()
