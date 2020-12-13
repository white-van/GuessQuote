# QuoteBot

This is a fun Discord bot made with Python! 
It reads from a quotes.py file of quotes saved from UB3R-Bot, randomly chooses a quote, and uses regex to print the quote without the speaker. Once the correct speaker is guessed, the bot replies with the full original quote. 

## How it works

bot.py obtains the quotes list from `quotes.py`


## Getting Started

These instructions will get you a copy of the bot up and running on your local machine and on the discord servers as well.

## Setup
Make sure to create the two following files:
`.env`
`quotes.py`

### .env
This is where you store your bot's discord token.
The file should contain the following:

DISCORD_TOKEN={your discord token here}

Alternatively, you could replace `TOKEN = os.getenv('DISCORD_TOKEN')` line 9 in `bot.py` with your token itself. Though this is not recommended if you are planning on pushing this to github (as your token will cry).

### Quotes.py
The quotes dump from UB3R-B0T could be found here: https://admin.ub3r-b0t.com/api/quotes/514949893278924802

Simply populate your `quotes.py` with the following:
```
quotes={UB3R-B0T QUOTE DUMP HERE}
```
replace `{UB3R-B0T QUOTE DUMP HERE}` with the entire list of JSON quotes from UB3R-B0T


## Authors

* **Niveditha Kani** - *Developer* - [NivedithaK](https://github.com/NivedithaK)

* **Lance Santiago** - *Developer* - [LanceSantiago](https://github.com/LanceSantiago)

## Acknowledgments

Inspired by the members of the UTM White Van:
discord.gg/whitevan