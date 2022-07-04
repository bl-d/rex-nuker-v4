import os
import logging
#import aiosonic 
import random
import json
import discord
import aiohttp
from discord.ext import commands

logging.basicConfig(
    level=logging.INFO,
    format="\033[38;5;82m[\033[0m%(asctime)s.%(msecs)03d\033[38;5;82m] \033[0m%(message)s\033[0m", 
    datefmt="%H:%M:%S" 
)

class webhook(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.clear = lambda: os.system("cls; clear")
        self.spammed = 0
        with open("settings.json", encoding="utf8") as file:
            try:
                self.settings = json.load(file)
                self.webhook_usernames = self.settings["Nuke Settings"]["Webhook Usernames"]
                self.webhook_spammsgs = self.settings["Nuke Settings"]["Spam Contents"]
                self.webhook_spam = self.settings["Nuke Settings"]["Webhook Spam"]
                self.show_logs  = self.settings["General Settings"]["Show Logs"]
            except Exception as error:
                logging.error(error)


    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        "webhooks spam when a channel is made | do {prefixlwhspam to spam without creating channels"
        try:
            if self.webhook_spam:
                if isinstance(channel, discord.TextChannel):
                    if self.show_logs: logging.info("Started creating & spamming webhooks in #{}".format(channel))
                    webhookOBJ = await channel.create_webhook(
                        name = random.choice(self.webhook_usernames)
                    )
                    webhookURL = webhookOBJ.url
                    async with aiohttp.ClientSession() as client:
                        while self.spammed <= 1500:
                            async with client.post(webhookURL, json={"content": random.choice(self.webhook_spammsgs)}) as response:
                                if response.status in [200, 201, 204]: self.spammed += 1
        except Exception as error:
            logging.error(error)


def setup(client):
    client.add_cog(webhook(client))
