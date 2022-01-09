# bot.py
import os
import discord
import random
import re
from dotenv import load_dotenv
load_dotenv()

from quotes import name_alias, quotes

#The Discord Auth token
TOKEN = os.getenv('DISCORD_TOKEN')
#QUOTES_PATH="quotes.txt"
client = discord.Client()

#Prefix
prefix = '-'

# The different playable games
gameStates = {
    'guessGame': {
        'ans': None,
        'origQuote': None,
        'namelessQuote': None,
    }
}

leaderboards = {
    'guessGame': {
        'userIdToPoints': {},
        'leaderboard': []
    }
}


#Display helper functions
def DisplayHelp():
    embed=discord.Embed(title='Guess Quote Commands!', color=0x702eb2)
    embed.add_field(name='{0}guessquote ({0}gq)'.format(prefix), value='Starts a quote guessing game!', inline=False)
    embed.add_field(name='{}giveup'.format(prefix), value='Ends the current game', inline=False)
    embed.add_field(name='{}leaderboard'.format(prefix), value='displays the current leaderboard', inline=False)
    embed.add_field(name='{}quote'.format(prefix), value='Repeats current quote', inline=True)
    return embed

def DisplayGuessGame(ans = None, origQuote = None, namelessQuote = None):
    embed=discord.Embed(title="Guess who said this quote!", color=0x702eb2)
    embed.add_field(name="‎", value=namelessQuote, inline=True)
    return embed

def DisplayNoGame():
    return discord.Embed(title="Oh no!", description="There currently isn't a game running, start one with {0}guessquote or {0}gq!".format(prefix), color=0x702eb2)

def DisplayGiveup(ans = None, origQuote = None, namelessQuote = None):
    embed=discord.Embed(title="So close!", description="You weren't able to guess the quote, that sucks!", color=0x702eb2)
    embed.add_field(name="Original Quote", value=origQuote, inline=True)
    return embed

def DisplayCorrect(ans = None, origQuote = None, namelessQuote = None):
    embed=discord.Embed(title="Correct!", description="Spot on, you got it right!", color=0x702eb2)
    embed.add_field(name="Original Quote", value=origQuote, inline=True)
    return embed

def DisplayIncorrect():
    embed=discord.Embed(title="Guess the Quote!", description="Incorrect, ya got the wrong person!", color=0x702eb2)
    return embed

async def DisplayLeaderboard(clientUser):
    embed=discord.Embed(title="Leaderboard!", color=0x702eb2)
    curLeaderboard = leaderboards['guessGame']
    if curLeaderboard['userIdToPoints'].get(clientUser, None) != None:
        theirRank = [cliId for cliId, _ in curLeaderboard['leaderboard']].index(clientUser) + 1
        embed.add_field(name="Your Rank!",value=theirRank, inline= False)
        embed.add_field(name="Your Points!",value=curLeaderboard['leaderboard'][theirRank - 1][1], inline = False)

    if len(curLeaderboard['leaderboard']) != 0:
        counter = 1
        for leader, value in curLeaderboard['leaderboard'][:10]:
            leaderName = await client.fetch_user(leader)
            embed.add_field(name='{}. {}'.format(counter,leaderName), value=value, inline = False)
            counter += 1
    return embed



def has_match(lstOne, lstTwo):
    seen = {}
    for element in lstOne:
        seen[element] = 1
    for element in lstTwo:
        if seen.get(element,None) != None:
            return True 
    return False 

#Game one

def parseGameOne(message, clientUser, ans, origQuote, namelessQuote):
    global currentGame
    name = None 
    messageList = message.split(' ')
    if len(messageList)  > 1:
        name = ' '.join(messageList[1:]).lower()
    #check if they try to initiate here
    if message in ['gq','guessquote']:
        #Trying to be sneaky
        return discord.Embed(title='Oh no!', description='You tried to start a new game, when a current game is already in session! Use -quote to repeat the quote, or -giveup to quit the game!', color=0x702eb2)
    elif message in ['quote']:
        #Repeat Quote
        return DisplayGuessGame(namelessQuote = namelessQuote)
    elif message in ['giveup']:
        #Gave up
        currentGame = 0
        resetGameOne()
        return DisplayGiveup(origQuote = origQuote)
    elif ans.lower() in message.lower() or (name_alias.get(name, None) != None and has_match(name_alias[name], name_alias[ans.lower()])):
        #Winner!
        curLeaderboard = leaderboards['guessGame']
        curLeaderboard['userIdToPoints'][clientUser] = curLeaderboard.get(clientUser, 0) + 1
        rankings = list(curLeaderboard['userIdToPoints'].items())
        rankings.sort(key=lambda tup: tup[1], reverse=True)
        curLeaderboard['leaderboard'] = rankings

        #Rest state
        currentGame = 0
        resetGameOne()
        return DisplayCorrect(origQuote = origQuote)
    else:
        #Wrong Guess
        return DisplayIncorrect()


def resetGameOne():
    gameStates["guessGame"] = {
        'ans': None,
        'origQuote': None,
        'namelessQuote': None,
    }
    
#The current game playing, 0 if none
currentGame = 0


parseGameFunc = [None, ('guessGame',parseGameOne)]

resetGameFunc = [None, resetGameOne]



def randquote():
    quote = quotes[random.randint(0, len(quotes)-1)]
    quoteText = quote['text']
    quoteAuthor = quote['nick']
    OGQuote = quote['id'] + ": " + quoteText + " - " + quoteAuthor
    output = [quoteText, quoteAuthor, OGQuote]
    return output

@client.event
async def on_ready():
    resetGameOne()
    # Everything under here, the bot executes for "commands"
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    global currentGame
    global gameStates
    if message.author == client.user:
        return

    clientUser = message.author.id
    messageContent = (message.content).lower()

    if len(messageContent) > 0 and messageContent[0] == prefix:
        messageContent = messageContent[1:]
        response = None
            # List of Commands

        if messageContent == 'help':
            response = DisplayHelp()
        
        elif messageContent in ['leaderboard', 'lb']:
            response = await DisplayLeaderboard(clientUser)
        
            # Prevents starting a new game if a game is on progress
        elif currentGame != 0: 
            key, curGameParser = parseGameFunc[currentGame]
            response= curGameParser(messageContent,clientUser, **gameStates[key])
        else:
            #Start the game
            if (messageContent in ['guessquote','gq']):
                quoteText, quoteAuthor, OGQuote = randquote()
                currentGame = 1
                gameStates['guessGame'] = {
                    'ans': quoteAuthor,
                    'origQuote': OGQuote,
                    'namelessQuote': quoteText
                }
                response = DisplayGuessGame(**gameStates['guessGame'])
            elif (messageContent in ['giveup', 'quote','guess']):
                response = DisplayNoGame()

        if response != None:
            await message.channel.send(embed = response)

client.run(TOKEN)
