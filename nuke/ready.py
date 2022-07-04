import os
import discord
import time
import logging
import json
import threading
import requests
from discord.ext import commands

try: from pystyle import Colors, Colorate
except (ModuleNotFoundError): os.system("pip install pystyle"); from pystyle import Colors, Colorate

logging.basicConfig(
    level=logging.INFO,
    format="\033[38;5;21m[\033[0m%(asctime)s.%(msecs)03d\033[38;5;21m] \033[0m%(message)s\033[0m", 
    datefmt="%H:%M:%S" 
)

class ready(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.clear = lambda: os.system("cls; clear")
        self.delay = 1
        self.version = 0.4


    async def menu(self):
        os.system("cls & mode 100, 25 & title Rex Nuker V4")
        try: await self.client.change_presence(status=discord.Status.invisible)
        except Exception: pass
        print(Colorate.Horizontal(Colors.blue_to_cyan, menu, 1))
        print()
        logging.info("Welcome to Rex V4! - Krypton")
        logging.info("Client loaded as {}".format(self.client.user))

    @commands.Cog.listener()
    async def on_connect(self):
        self.clear()
        await self.menu()

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        try: await ctx.message.delete()
        except: pass
        logging.error(error)


file = open("settings.json", encoding="utf8")
json = json.load(file)
prefix = json["Nuke Settings"]["Prefix"]


menu = f"""
                            ▄▄▄  ▄▄▄ .▐▄• ▄      ▐ ▄ ▄• ▄▌▄ •▄ ▄▄▄ .▄▄▄  
                            ▀▄ █·▀▄.▀· █▌█▌▪    •█▌▐██▪██▌█▌▄▌▪▀▄.▀·▀▄ █·
                            ▐▀▀▄ ▐▀▀▪▄ ·██·     ▐█▐▐▌█▌▐█▌▐▀▀▄·▐▀▀▪▄▐▀▀▄ 
                            ▐█•█▌▐█▄▄▌▪▐█·█▌    ██▐█▌▐█▄█▌▐█.█▌▐█▄▄▌▐█•█▌
                            .▀  ▀ ▀▀▀ •▀▀ ▀▀    ▀▀ █▪ ▀▀▀ ·▀  ▀ ▀▀▀ .▀  ▀                
           ──────────────────────────────────────────────────────────────────────────────
                ────────────────────────────────────────────────────────────────────
                                         * Nuke Commands *
                   +────────────────────────────────────────────────────────────+
                   | {prefix}nuke - Destroys Server     | {prefix}prune - Prune Members       |
                   | {prefix}massban - Bans All Members | {prefix}lag - Audit Hangs Server    |
                   | {prefix}cc - Creates Channels      | {prefix}spam - Spams Messages       |
                   | {prefix}rc - Creates Roles         | {prefix}testban - Tests Mass Ban    |
                   +────────────────────────────────────────────────────────────+
- 
│ Created By Krypton
| Version: 4.1
- 
"""


def setup(client):
    client.add_cog(ready(client))
