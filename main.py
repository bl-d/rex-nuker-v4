"""
Created By: Krypton/krypton#4165
An easy asynchronous Python "Discord Nuke Bot" for educational purposes *ONLY*!
Features: Fast Mass Banning, Fast Webhook Spamming, Customizable Delay & Tasks, Proxy Support.
"""
import discord
import json
import logging
import os
from discord.ext import commands

logging.basicConfig(
    level=logging.INFO,
    format="\033[38;5;21m[\033[0m%(asctime)s.%(msecs)03d\033[38;5;21m] \033[0m%(message)s\033[0m", 
    datefmt="%H:%M:%S" 
)

os.system("cls & mode 100, 25 & title Rex Nuker V4")

with open("settings.json", encoding="utf8") as file:
    try:
        settings = json.load(file)
        token = settings["Nuke Settings"]["Token"]
        prefix = settings["Nuke Settings"]["Prefix"]
        bot = settings["Nuke Settings"]["Prefix"]
    except Exception as error:
        logging.error(error)


client = commands.Bot(
    command_prefix = prefix,
    intents = discord.Intents.all(),
    case_insensitive = True,
    help_command = None
)


for cog in ["nuke.nuke", "nuke.ready", "nuke.webhook"]:
    try:
        client.load_extension(cog)
        logging.info("Loaded extention {}".format(cog))
    except Exception as error:
        logging.error(error)


if __name__ == "__main__":
    try: client.run(token, reconnect=True, bot=bot)
    except Exception as error: logging.error(error); input()
