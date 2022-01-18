import discord
import requests
import re
import os
from collections import defaultdict
from ics import Calendar
from datetime import datetime
from discord.ext import tasks


class ICSReader():
    def read(self, url):
        path = url
        c = Calendar(requests.get(path).text)
        birthdays = list(c.events)
        return birthdays

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

client = discord.Client()
reader = ICSReader()
birthdays = reader.read(os.environ['ICAL_URL'])
for birthday in birthdays:
    a[birthday.begin.month].append(birthday)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$ping'):
        await message.channel.send('Pong!')

    if message.content == '$help':
        text = ("Valid input to get the birthdays of a month:\n"
                "$bd 1 - 12\n"
                "$bd 01 - 12\n"
                "$bd jan - dec\n"
                "$bd january - december\n"
                "e.g.: `$bd 05` or `$bd 5` or `$bd may`")
        await message.channel.send(text)

    if re.search("\$bde? [0-1]?[0-9]", message.content):
        month = int(message.content.split(" ")[1])
        await send_birthdays_of_month(month, message)

    if re.search("\$bde? (?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|june?|july?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)", message.content.lower()):
        month = int(months[message.content.split(" ")[1].lower()])
        await send_birthdays_of_month(month, message)

async def send_birthdays_of_month(month, message):
    if (month > 0) and (month <= 12):
        if len(a[month]) == 0:
            await message.channel.send("No Birthdays this month!")
            return
    else:
        await message.channel.send("OI MATE. WHAT ARE YOU DOING?")
        return

    text = "Here are the birthdays of this month: \n"

    for birthday in a[month]:
        text = text + "> **" + birthday.name + "** is on **" + birthday.begin.format("MMMM DD") + "**"
        description = birthday.description.replace('\n', '')
        if re.match("BIRTH_YEAR?=?[1-9][0-9]{3}$", description):
            birth_year = int(birthday.description.split("=")[1])
            text += attach_age_to_birthday(birth_year)
        text += '\n'

    await message.channel.send(text)

@tasks.loop(seconds=3600.0)
async def print_todays_birthdays():
    now = datetime.now()
    if a[now.month]:
        b = defaultdict(list)

        for bd in a[now.month]:
            b[bd.begin.day].append(bd)

        if now.hour == 00 and b[now.day]:
            text = "Here are today's birthdays: \n"
            for bd in b[now.day]:
                text += "> " + bd.name + "\n"
            for guild in client.guilds:
                for channel in guild.channels:
                    if str(channel) == "🎁birthdays" or str(channel) == "general":
                        await channel.send(text)

def attach_age_to_birthday(birth_year):
    current_year = int(datetime.now().year)
    age = str(current_year - birth_year)
    return " and is turning **" + age + "** years old"

print_todays_birthdays.start()
client.run(os.environ['ACCESS_TOKEN'])
