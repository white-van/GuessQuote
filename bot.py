# bot.py
import os
import discord
import random
import re
from dotenv import load_dotenv
import keep_alive
load_dotenv()

from quotes import name_alias, quotes, id_to_name

#The Discord Auth token
TOKEN = os.getenv('DISCORD_TOKEN')
#QUOTES_PATH="quotes.txt"
client = discord.Client()

#Prefix
prefix = '-'

WRONG_ANSWERS_NEEDED = 4

# The different playable games
gameState = {
        'ans': None,
        'origQuote': None,
        'namelessQuote': None,
        'hints': [],
        'guesses': 0
}

leaderboard = {
        'userIdToPoints': {},
        'leaderboard': []
}


#Display helper functions
def DisplayHelp():
    embed=discord.Embed(title='Guess Quote Commands!', color=0x702eb2)
    embed.add_field(name=f'{prefix}guessquote ({prefix}gq)', value='Starts a quote guessing game!', inline=False)
    embed.add_field(name=f'{prefix}giveup', value='Ends the current game', inline=False)
    embed.add_field(name=f'{prefix}leaderboard', value='displays the current leaderboard', inline=False)
    embed.add_field(name=f'{prefix}quote', value='Repeats current quote', inline=True)
    embed.add_field(name=f'{prefix}hint', value=f'Displays some hints, can only be used after {WRONG_ANSWERS_NEEDED} wrong guesses', inline=True)
    return embed

def DisplayGuessGame():
    global gameState

    namelessQuote = gameState['namelessQuote']

    embed=discord.Embed(title="Guess who said this quote!", color=0x702eb2)
    embed.add_field(name="‎", value=namelessQuote, inline=True)
    return embed

def DisplayNoGame():
    return discord.Embed(title="Oh no!", description=f'There currently isn\'t a game running, start one with {prefix}guessquote or {prefix}gq!', color=0x702eb2)

def DisplayGiveup():
    global gameState

    origQuote = gameState['origQuote']

    embed=discord.Embed(title="So close!", description="You weren't able to guess the quote, that sucks!", color=0x702eb2)
    embed.add_field(name="Original Quote", value=origQuote, inline=True)
    return embed

def DisplayCorrect():
    global gameState

    origQuote = gameState['origQuote']

    embed=discord.Embed(title="Correct!", description="Spot on, you got it right!", color=0x702eb2)
    embed.add_field(name="Original Quote", value=origQuote, inline=True)
    return embed

async def DisplayLeaderboard(clientUser):
    embed=discord.Embed(title="Leaderboard!", color=0x702eb2)
    if leaderboard['userIdToPoints'].get(clientUser, None) != None:
        theirRank = [cliId for cliId, _ in leaderboard['leaderboard']].index(clientUser) + 1
        embed.add_field(name="Your Rank!",value=theirRank, inline= False)
        embed.add_field(name="Your Points!",value=leaderboard['leaderboard'][theirRank - 1][1], inline = False)

    if len(leaderboard['leaderboard']) != 0:
        counter = 1
        for leader, value in leaderboard['leaderboard'][:10]:
            leaderName = await client.fetch_user(leader)
            embed.add_field(name=f'{counter}. {leaderName}', value=value, inline = False)
            counter += 1
    return embed

def DisplayHint():
    global gameState
    embed=discord.Embed(title="Here's a hint for ya!", color=0x702eb2)
    embed.set_footer(text=f'you can bring up this hint again with {prefix}hint')

    hints = gameState['hints']
    for index,hint in enumerate(hints):
        embed.add_field(name=f'{index + 1}. {hint}',value="‎", inline= False)
    return embed

def DisplayKeepGuessing():
    global gameState

    guesses = gameState['guesses']
    embed= discord.Embed(title=f'Keep guessing!', color=0x702eb2)

    embed.add_field(name=f"You need {WRONG_ANSWERS_NEEDED - guesses} more guesses to unlock this command", value="‎")
    return embed



def has_match(lstOne, lstTwo):
    seen = {}
    for element in lstOne:
        seen[element] = 1
    for element in lstTwo:
        if seen.get(element,None) != None:
            return True 
    return False 

def get_mc_choices(numChoicesNeeded, ansUser):
    listOfIds = random.sample(id_to_name.keys(),numChoicesNeeded)

    isAlreadyIn = False
    newNameChoices = []
    for curId in listOfIds:
        names = id_to_name[curId]
        if ansUser in names and not isAlreadyIn:
            newNameChoices.append(ansUser)
            isAlreadyIn = True
        else:
            newNameChoices.append(random.choice(list(names)))
    
    if isAlreadyIn:
        return newNameChoices
    else:
        random_index = random.randint(0,len(newNameChoices)-1)
        
        if random_index == 0:
            return [ansUser] + newNameChoices[1:]
        elif random_index == len(newNameChoices) - 1:
            return newNameChoices[:-1] + [ansUser]
        return newNameChoices[:random_index] + [ansUser] + newNameChoices[random_index + 1:]


#Game one

async def parseGameOne(messageObj, message, clientUser):
    global currentGame
    global gameState

    ans = gameState['ans']
    guesses = gameState['guesses']
    namelessQuote = gameState['namelessQuote']
    
    name = None 
    messageList = message.split(' ')
    if len(messageList)  > 1:
        name = ' '.join(messageList[1:]).lower()
    #check if they try to initiate here
    if message in ['gq','guessquote']:
        #Trying to be sneaky
        embed =  discord.Embed(title='Oh no!', description=f'A game is already in progress! Use -guess to guess or -giveup to quit the game', color=0x702eb2)
        embed.add_field(name='Quote',value=f'{namelessQuote}', inline= False)
        return embed
    elif message in ['quote']:
        #Repeat Quote
        return DisplayGuessGame()
    elif message in ['giveup']:
        #Gave up
        currentGame = 0
        embed = DisplayGiveup()
        resetGameOne()
        return embed
    elif message in ['hint']:
        if guesses >= WRONG_ANSWERS_NEEDED:
            return DisplayHint()
        else:
            return DisplayKeepGuessing()
    elif ans.lower() in message.lower() or (name_alias.get(name, None) != None and has_match(name_alias[name], name_alias[ans.lower()])):
        #Winner!
        leaderboard['userIdToPoints'][clientUser] = leaderboard.get(clientUser, 0) + 1
        rankings = list(leaderboard['userIdToPoints'].items())
        rankings.sort(key=lambda tup: tup[1], reverse=True)
        leaderboard['leaderboard'] = rankings

        #Rest state
        currentGame = 0
        embed = DisplayCorrect()
        resetGameOne()
        await messageObj.add_reaction('✅')
        return embed
    else:
        #Wrong Guess
        await messageObj.add_reaction('❌')

        gameState['guesses'] += 1
        if (gameState['guesses'] == WRONG_ANSWERS_NEEDED):
            return DisplayHint()


def resetGameOne():
    global gameState
    gameState = {
        'ans': None,
        'origQuote': None,
        'namelessQuote': None,
        'hints': [],
        'guesses': 0
    }
    
#The current game playing, 0 if none
currentGame = 0


parseGameFunc = [None, parseGameOne]

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
    global gameState
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
        
        elif currentGame != 0: 
            curGameParser = parseGameFunc[currentGame]
            response= await curGameParser(message, messageContent,clientUser)
        else:
            #Start the game
            if (messageContent in ['guessquote','gq']):
                quoteText, quoteAuthor, OGQuote = randquote()
                hints = get_mc_choices(4,quoteAuthor)
                currentGame = 1
                gameState= {
                    'ans': quoteAuthor,
                    'origQuote': OGQuote,
                    'namelessQuote': quoteText,
                    'hints': hints,
                    'guesses': 0
                }
                response = DisplayGuessGame()
            elif (messageContent in ['giveup', 'quote','guess','hint']):
                response = DisplayNoGame()

        if response != None:
            await message.reply(embed = response, mention_author = False)

keep_alive.keep_alive()
client.run(TOKEN)
