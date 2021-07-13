# Dependencies
# pip install discord
# pip install -U discord-py-slash-command

import discord
import json
import backend
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash.model import SlashCommandOptionType

with open('keys.json', encoding='utf-8-sig') as k:
    keys = json.load(k)

client = discord.Client(intents=discord.Intents.all())
slash = SlashCommand(client, sync_commands=True)
guildIDs = keys["guildIDs"]

@client.event
async def on_ready():
  print("Username: " + client.user.name)
  await changeSplash()

@client.event
async def on_message(message):
  if message.content[0:2]=="//":
    # await message.channel.send()
    await message.delete()
    embedVar = discord.Embed(title="Welcome to the Scunt Discord!", description="Please use the login command", color=0x00ff00)
    embedVar.add_field(name="//login <email>", value=message.content[2:], inline=False)
    await message.channel.send(embed=embedVar)

@slash.slash(name="login", guild_ids=guildIDs, description="This is just a test command, nothing more.", options = [
   create_option(
    name="email",
    description="Use your registration email for F!rosh week",
    option_type=SlashCommandOptionType.STRING,
    required=True
  ),
])
async def test(ctx, email):
  if "@" in email:
    loginResponse = backend.loginUser(email)
    if loginResponse["alreadyIn"]:
      await ctx.send(embed=errorEmbed("You have already logged in and are on team " + loginResponse["team"]))
    embedVar = discord.Embed(title="Thanks for logging in "+loginResponse["fullName"], description="You are on team #" + loginResponse["team"] + " and you now have access to the respective channels.", color=0x00ff00)
    await ctx.send(embed=embedVar)
  else:
    await ctx.send(embed=errorEmbed("Please enter a valid email and try again."))

async def changeSplash():
  await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="out for you"))

def errorEmbed(errorDescription):
  return discord.Embed(title="Error", description=errorDescription, color=0xeb402d)


client.run(keys["clientToken"])