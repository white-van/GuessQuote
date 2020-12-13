# bot.py
import os
import discord
import random
import re

from quotes import *

TOKEN = os.getenv('DISCORD_TOKEN')
#QUOTES_PATH="quotes.txt"
client = discord.Client()


game=False
ans=""
response=""
origQuote=""
namelessQuote=""
global name_alias
name_alias = {"orange": ["nivy"], "iandur": ["lance", "lander"], "laptop monkey": ["kyo", "desktop monkey"], "emily w": ["emily", "goose"],
"blossom": ["naaz"], "onion": ["onion", "ritvik", "aipiox"], "jc": ["jerry"], "absurdism": ["krish"], "redvilder": ["nick"],"doomgooey": ["sergey", "doom"], "jonjonnho": ["jonathan"], "みお" : ["mio"],
"luciars": ["shiba", "lucas"], "garboguy": ["liam", "garbo" ,"mailman"], "dripbot": ["bolt"], "the-call-of-the-void": ["jessica", "obomo"], "voidlord": ["chonky","chonky birb", "StarLight "], "givemewater": ["water"], "kay911kay": ["broke&homeless", "broke", "daniel"], "salazareo": ["daniel", "salazar"], 
"riddle": ["kana"], "theraghavsharma": ["raghav", "kyo's butler"], "winghawk": ["georges","shanker"], "lukasz345": ["lukasz"], "starlight": ["chonky","chonky birb", "voidlord"],
"1!":["wan"], "iloveubb":["hans"], 
"undefined_kimchi": ["kimchi", "kim"], "cluelessKimchi一IlirFan": ["kimchi", "kim"], "kimchi_bot": ["kimchi", "kim"], "Chonky Rebel BOT Kimchi": ["kimchi", "kim"], "cluelessKimchi-IlirFan": ["kimchi", "kim"]
}

def randquote():
    quote = quotes[random.randint(0, len(quotes)-1)]
    quoteText = quote['text']
    quoteAuthor = quote['nick']
    OGQuote = quote['id'] + ": " + quoteText + " - " + quoteAuthor
    output = [quoteText, quoteAuthor, OGQuote]
    return output

def setState(gameState,answerState,originalQuote, quote):
    global game
    global ans
    global origQuote
    global namelessQuote

    game=gameState
    ans=answerState
    origQuote=originalQuote
    namelessQuote=quote

def getState():
    return [game, ans, origQuote,namelessQuote]

@client.event
async def on_ready():
    game=False
    ans=""
    # Everything under here, the bot executes for "commands"
    print(f'{client.user} has connected to Discord!')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    messageContent = (message.content).lower()

    if len(messageContent) > 0 and messageContent[0] == "-":
        response=""
            # List of Commands

        if messageContent == '-help':
            response="**Guess Quote Commands!**\n **-guessquote** -> starts a quote guessing game! (short form -**gq**)\n **-giveup** -> Stops the game and reveals the answer!\n **-[username]** -> guessing that username for the current quote\n **-quote** -> Repeats the current quote being guessed!"
        
            # Prevents starting a new game if a game is on progress
        elif (messageContent == '-guessquote' or messageContent == '-gq') and getState()[0]: 
            response="Guess the previous quote! use -giveup to giveup\n Current Quote:\n" + getState()[3]

            # Starting the Game
        elif (messageContent == '-guessquote' or messageContent == '-gq') and not getState()[0]:
            quote = randquote()
            response = quote[0]
            setState(True,quote[1],quote[2],quote[0])
            # re-prints the quote
        elif(messageContent == '-quote') and getState()[0]:
            response=getState()[3]
            # Giving up
        elif messageContent == '-giveup' and getState()[0]:
            response = "Original quote:\n\n" + getState()[2]
            setState(False,"","","")

            # Giving up when no game is running
        elif (messageContent == '-giveup' or messageContent == '-quote') and not getState()[0]:
            reponse = "There is currently no game running!\nUse -guessquote to start a game!"

            # Correct Guess
        elif getState()[0] and ((getState()[1]).lower() in messageContent) or (getState()[1].lower() in name_alias) and messageContent[1:] in (name_alias[getState()[1].lower()]):
            response = "**Correct!** \nOriginal quote:\n\n" + getState()[2]
            setState(False,"","","")

            # Wrong Guess
        elif getState()[0]:
            response = "Guess again or type -giveup to giveup." 
        if response != "":
            await message.channel.send(response)

client.run(TOKEN)
