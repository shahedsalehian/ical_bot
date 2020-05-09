import discord
import requests
import re
import sched, time
import threading
import os
from collections import defaultdict
from ics import Calendar
from discord.ext import commands
from datetime import datetime, timedelta

class ICSReader():
    def read(self, url):
        path = url
        c = Calendar(requests.get(path).text)
        birthdays = list(c.events)
        return birthdays

class MyClient(discord.Client):
    a = defaultdict(list)

    async def todays_birthdays(self, channel):
        threading.Timer(3600.0, self.todays_birthdays).start()
        now = datetime.now()

        if self.a[now.month]:
            b = defaultdict(list)
            for bd in self.a[now.month]:
                b[bd.begin.day].append(bd)
            if now.hour == 00:
                if b[now.day]:
                    text = "Here are today's birthdays: \n"
                    for bd in b[now.day]:
                        text += "> " + bd.name + "\n"
                        await channel.send(text)
                else:
                    print("No Birthday's Today")
        else:
            print("No birthday's this month")

            
    async def on_ready(self):
        print('Logged on as', self.user)
        reader = ICSReader()
        birthdays = reader.read(os.environ['ICAL_URL'])
        
        for birthday in birthdays:
            self.a[birthday.begin.month].append(birthday)

        for guild in self.guilds:
            for channel in guild.channels:
                if str(channel) == "general":
                    await self.todays_birthdays(channel)

    async def on_message(self, message):
        if message.author == self.user:
            return
            
        if message.content == '!ping':
            await message.channel.send('pong')
            return

        x = re.search("!bd [0-1][0-9]", message.content)
        if x == None:
            return
        else:
            month = int(x.string.split(" ")[1])
            if (month > 0) and (month <= 12):
                if len(self.a[month]) == 0:
                    await message.channel.send("No Birthdays this month!")
                    return

                text = "Here are the birthdays of this month: \n"
                for birthday in self.a[month]:
                    text += "> " + birthday.name + " is on " + birthday.begin.format("MMMM DD") + "\n"
                
                await message.channel.send(text)
                return

    
client = MyClient()
client.run(os.environ['ACCESS_TOKEN'])

# TODO:
# 1. Graceful shutdown of bot 