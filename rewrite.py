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

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    reader = ICSReader()
    birthdays = reader.read(os.environ['ICAL_URL'])
    for birthday in birthdays:
        a[birthday.begin.month].append(birthday)

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
    text = "Here are the birthdays of this month: \n"

    for birthday in a[month]:
        text = text + "\n" + "> **" + birthday.name + "** is on **" + birthday.begin.format("MMMM DD") + "**"

    await message.channel.send(text)
        

client.run(os.environ['ACCESS_TOKEN'])
