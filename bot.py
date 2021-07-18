# Dependencies
# pip install discord
# pip install -U discord-py-slash-command

#TODO
#Welcome message
#Submit command - google drive - please make sure you share - can check permissions with drive api
#     pass in team name and name
#Status command - see the status of a challenge, DM
#View challenges - link to all the challenges, DM
#View challenges completion - DM
#Search challenges - DM
#Login command - set nickname and pronoun
#DM when judge assigns points or comments or accepts

#Challenges structure
# Item number (#1)
# Item Description (Jump into a body of water)
# Category (The Classics)
# Points (a number, ie 300)
# NEW: Completed status?
# Comment (from judge?)

#welcome channel should have permissions - send messages to false for logged in role

import discord
import json
import backend
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash.model import SlashCommandOptionType

with open('keys.json', encoding='utf-8-sig') as k:
  keys = json.load(k)
with open('constants.json', encoding='utf-8-sig') as c:
  constants = json.load(c)

client = discord.Client(intents=discord.Intents.all())
slash = SlashCommand(client, sync_commands=True)
guildIDs = keys["guildIDs"]
colors = {
  "purple": 0xb042f5,
  "red": 0xeb402d,
  "green": 0x00ff00
}

@client.event
async def on_ready():
  print("Username: " + client.user.name)
  await changeSplash()

@client.event
async def on_member_join(member):
  channel = discord.utils.get(member.guild.channels, name=constants["welcomeChannel"])
  embedVar = discord.Embed(title="Welcome to the Scunt Discord " + member.display_name + "!", description="", color=colors["purple"])
  embedVar.add_field(name="Please use the /login <email>", value="(same email as registration)", inline=False)
  await channel.send(embed=embedVar)

@slash.slash(name="login", guild_ids=guildIDs, description="Used to get access to your Scunt team. Use the same email as registration.", options = [
   create_option(
    name="email",
    description="Use your registration email for F!rosh week",
    option_type=SlashCommandOptionType.STRING,
    required=True
  ),
])

#todo - send error if email was entered and not in database
#todo - backend can send fullName field or preferred name if not empty
async def test(ctx, email):
  if "@" in email:
    loginResponse = backend.loginUser(email)
    if loginResponse["alreadyIn"]:
      await ctx.send(embed=errorEmbed("You have already logged in and are on team " + str(loginResponse["team"])))
    else:
      try:
        await ctx.author.add_roles(discord.utils.get(ctx.author.guild.roles, name=constants["teamRoles"][int(loginResponse["team"])-1]))
        await ctx.author.edit(nick=(loginResponse["fullName"]+" ("+loginResponse["pronoun"]+")")[0:31])
        await ctx.author.add_roles(discord.utils.get(ctx.author.guild.roles, name=constants["loggedInRole"]))
      except Exception as e:
        await ctx.send(embed=errorEmbed(str(e)))
      else:
        embedVar = discord.Embed(title="Login successful, "+loginResponse["fullName"], description="You are on team #" + str(loginResponse["team"]) + " and you now have access to the respective channels.", color=colors["green"])
        await ctx.send(embed=embedVar)
  else:
    await ctx.send(embed=errorEmbed("Please enter a valid email and try again. Use the same email as you used to register."))

async def changeSplash():
  await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="out for you"))

def errorEmbed(errorDescription):
  return discord.Embed(title="Error", description=errorDescription, color=colors["red"])


client.run(keys["clientToken"])