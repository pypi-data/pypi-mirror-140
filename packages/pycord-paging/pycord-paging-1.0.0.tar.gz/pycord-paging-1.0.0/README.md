# Pycord Paginator
**Pycord Paginator** is a library to paginate your messages or embeds when using [Pycord](https://github.com/Pycord-Development/pycord).

⚠ This library is a fork of https://github.com/FlamptX/paginator.py, made for [Diskord](https://github.com/diskord-dev/diskord).

To install the library, open your terminal and run this command:
```
pip install pycord-paging
```

Example with reactions:
```py
from discord import Embed
from discord.ext import commands
from paginator import Paginator, Page

bot = commands.Bot(command_prefix="!")
paginator = Paginator(bot)

@bot.event
async def on_ready():
    print("Bot online")

@bot.command()
async def paginator(ctx):
    pages = [
        Page(embed=Embed(title="Page #1", description="Testing")),
        Page(embed=Embed(title="Page #2", description="Still testing")),
        Page(embed=Embed(title="Page #3", description="Guess... testing"))
    ]

    await paginator.send(ctx.channel, pages, type=1, author=ctx.author, disable_on_timeout=False)

bot.run("...")
```

Example with buttons:
```py
from discord import Embed
from discord.ext import commands
from paginator import Paginator, Page

bot = commands.Bot(command_prefix="!")
paginator = Paginator(bot)

@bot.event
async def on_ready():
    print("Bot online")

@bot.command()
async def paginator(ctx):
    pages = [
        Page(embed=Embed(title="Page #1", description="Testing")),
        Page(embed=Embed(title="Page #2", description="Still testing")),
        Page(embed=Embed(title="Page #3", description="Guess... testing"))
    ]

    await paginator.send(ctx.channel, pages, type=2, author=ctx.author, disable_on_timeout=False)

bot.run("...")
```

Docs will be published soon... 👀
