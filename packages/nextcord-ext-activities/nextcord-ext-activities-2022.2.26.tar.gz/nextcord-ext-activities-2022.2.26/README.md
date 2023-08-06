# nextcord-ext-activities
nextcord.ext.activities is an extension that helps you to launch activities on Discord.

# Quick example
```py
import nextcord
from nextcord.ext import commands, activities

intents = nextcord.Intents.default()
bot = commands.Bot(command_prefix = "$")

@bot.event
async def on_ready():
    print(f"Logged in as {str(bot.user)} (ID {bot.user.id})")

@bot.command()
async def poker(ctx, channel: nextcord.VoiceChannel):
    invite_link = await channel.create_activity_invite(activities.Activity.poker)
    await ctx.send(invite_link)

@bot.command()
async def betrayal(ctx, channel: nextcord.VoiceChannel):
    invite_link = await channel.create_activity_invite(activities.Activity.betrayal)
    await ctx.send(invite_link)

bot.run('token here')
```
You can find more example in the [example directory](https://github.com/MaskDuck/nextcord-ext-activities/tree/main/examples)
