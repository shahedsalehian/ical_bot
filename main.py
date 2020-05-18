import discord
import requests
import re
import asyncio
import os
from collections import defaultdict
from ics import Calendar
from datetime import datetime

class ICSReader():
    def read(self, url):
        path = url
        c = Calendar(requests.get(path).text)
        birthdays = list(c.events)
        return birthdays

class MyClient(discord.Client):
    a = defaultdict(list)
    months = {
        'january':'01',
        'february':'02',
        'march':'03',
        'april':'04',
        'may':'05',
        'june':'06',
        'july':'07',
        'august':'08',
        'september':'09',
        'october':'10',
        'november':'11',
        'december':'12',
        'jan':'01',
        'feb':'02',
        'mar':'03',
        'apr':'04',
        'jun':'06',
        'jul':'07',
        'aug':'08',
        'sep':'09',
        'oct':'10',
        'nov':'11',
        'dec':'12'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bg_task = self.loop.create_task(self.print_todays_birthdays())

    async def print_todays_birthdays(self):
        await self.wait_until_ready()

        while not self.is_closed():
            now = datetime.now()
            if self.a[now.month]:
                b = defaultdict(list)
                for bd in self.a[now.month]:
                    b[bd.begin.day].append(bd)
                if now.hour == 00 and b[now.day]:
                    text = "Here are today's birthdays: \n"
                    for bd in b[now.day]:
                        text += "> " + bd.name + "\n"

                    for guild in self.guilds:
                        for channel in guild.channels:
                            # str(channel) == "🎁birthdays" or 
                            if str(channel) == "general":
                                await channel.send(text)                    
            await asyncio.sleep(3600)

    async def on_ready(self):
        print('Logged on as', self.user)
        reader = ICSReader()
        birthdays = reader.read(os.environ['ICAL_URL'])
        
        for birthday in birthdays:
            self.a[birthday.begin.month].append(birthday)

    async def on_message(self, message):
        if message.author == self.user:
            return
            
        if message.content == '!ping':
            await message.channel.send('pong')
            return

        if message.content == '!help':
            text = ("Valid input to get the birthdays of a month:\n"
                    "!bd 1 - 12\n"
                    "!bd 01 - 12\n"
                    "!bd jan - dec\n"
                    "!bd january - december\n"
                    "e.g.: `!bd 05` or `!bd 5` or `!bd may`")
            await message.channel.send(text)
            return

        if re.search("!bde? [0-1]?[0-9]", message.content):
            await self.print_birthdays_by_month(int(message.content.split(" ")[1]), message)
            return

        if re.search("!bde? (?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|june?|july?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)", message.content.lower()):
            month = int(self.months[message.content.split(" ")[1].lower()])
            await self.print_birthdays_by_month(month, message)
            return
        
        return
        
    async def print_birthdays_by_month(self, month, message):
        if (month > 0) and (month <= 12):
            if len(self.a[month]) == 0:
                await message.channel.send("No Birthdays this month!")
                return

            text = "Here are the birthdays of this month: \n"
            for birthday in self.a[month]:
                text += "> " + birthday.name + " is on " + birthday.begin.format("MMMM DD") + "\n"

            await message.channel.send(text)
    
client = MyClient()
client.run(os.environ['ACCESS_TOKEN'])
