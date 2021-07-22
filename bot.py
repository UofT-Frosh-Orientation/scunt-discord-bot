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





#TODO
#new users shouldn't be able to submit - must have logged in role
#see team points list

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
  "green": 0x00ff00,
  "yellow": 0xfcd703
}

@client.event
async def on_ready():
  print("Username: " + client.user.name)
  await changeSplash()

@client.event
async def on_member_join(member):
  channel = discord.utils.get(member.guild.channels, name=constants["welcomeChannel"])
  embedVar = discord.Embed(title="🎉 Welcome to the Scunt Discord " + member.display_name + "!", description="", color=colors["purple"])
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
async def login(ctx, email):
  if "@" in email:
    loginResponse = backend.loginUser(email)
    if loginResponse["alreadyIn"]:
      await ctx.send(embed=errorEmbed("You have already logged in and are on team " + str(loginResponse["team"])))
    else:
      try:
        await ctx.author.add_roles(discord.utils.get(ctx.author.guild.roles, name=constants["teamRoles"][int(loginResponse["team"])-1]))
        await ctx.author.add_roles(discord.utils.get(ctx.author.guild.roles, name=constants["loggedInRole"]))
        await ctx.author.edit(nick=(loginResponse["fullName"]+" ("+loginResponse["pronoun"]+")")[0:31])
      except Exception as e:
        await ctx.send(embed=errorEmbed(str(e)))
      else:
        embedVar = discord.Embed(title="Login successful, "+loginResponse["fullName"], description="You are on team #" + str(loginResponse["team"]) + " and you now have access to the respective channels.", color=colors["green"])
        await ctx.send(embed=embedVar)
  else:
    await ctx.send(embed=errorEmbed("Please enter a valid email and try again. Use the same email as you used to register."))

@slash.slash(name="submit", guild_ids=guildIDs, description="Submit a challenge via discord attachments.", options = [
  create_option(
    name="challenge",
    description="The challenge ID",
    option_type=SlashCommandOptionType.INTEGER,
    required=True
  ),
])
async def submit(ctx, challenge):
  def check(message):
    if ctx.author.id == message.author.id:
      return True
    else:
      return False
  embedVar = discord.Embed(title="Please send your image/video via discord now. The bot is waiting for you...", description="Send any text message to cancel.", color=colors["yellow"])
  await ctx.send(embed=embedVar)
  try: 
    msg = await client.wait_for('message', check=check, timeout=60)
    if msg.attachments:
      team = getTeam(ctx)
      if(team!=False):
        embedVar = discord.Embed(title="Sent to the judges!", description=createDescription([
          {"title": "Challenge", "description":challenge},
          {"title": "Submission", "description":msg.attachments[0].url},
          {"title": "Team", "description":team},
        ]), color=colors["green"])
        await ctx.send(embed=embedVar)
        await msg.add_reaction("✅")
      else:
        await ctx.send(embed=errorEmbed("You are not on a team! Please use /login"))
        await msg.add_reaction("🛑")
    else:
      await ctx.send(embed=errorEmbed("Cancelled. Please upload an attachment via discord next time or use the /submitlink command."))
  except:
    await ctx.send(embed=errorEmbed("Timed out, please run the command and try again."))

@slash.slash(name="submitlink", guild_ids=guildIDs, description="Submit a challenge via discord attachments.", options = [
  create_option(
    name="challenge",
    description="The challenge ID",
    option_type=SlashCommandOptionType.INTEGER,
    required=True
  ),
  create_option(
    name="link",
    description="Link to the challenge submission",
    option_type=SlashCommandOptionType.STRING,
    required=True
  ),
])
async def submitlink(ctx, challenge, link):
  team = getTeam(ctx)
  if(team!=False):
    embedVar = discord.Embed(title="Sent to the judges!", description=createDescription([
      {"title": "Challenge", "description":challenge},
      {"title": "Submission", "description":link},
      {"title": "Team", "description":team},
    ]), color=colors["green"])
    await ctx.send(embed=embedVar)
  else:
    await ctx.send(embed=errorEmbed("You are not on a team! Please use /login"))

@slash.slash(name="status", guild_ids=guildIDs, description="View the status of a challenge", options = [
  create_option(
    name="challenge",
    description="The challenge ID",
    option_type=SlashCommandOptionType.INTEGER,
    required=True
  ),
])
async def status(ctx, challenge):
  team = getTeam(ctx)
  if(team!=False):
    embedVar = discord.Embed(title="Challenge " + str(challenge), description=createDescription([
      {"title": "Status", "description":"incomplete"},
      {"title": "Comments", "description":""},
      {"title": "Points rewarded", "description":""},
    ]), color=colors["purple"])
    await ctx.author.send(embed=embedVar)
    embedVar = discord.Embed(title="Sent you a DM!", color=colors["purple"])
    msg = await ctx.send(embed=embedVar)
    await msg.delete()
  else:
    await ctx.send(embed=errorEmbed("You are not on a team! Please use /login"))

@slash.slash(name="help", guild_ids=guildIDs, description="See all the commands available.")
async def help(ctx):
  embedVar = discord.Embed(title="Available Scunt " + constants["scuntYear"] + " commands", color=colors["purple"])
  for command in constants["commands"] :
    embedVar.add_field(name=command["title"],value=command["description"],inline=False)
  await ctx.author.send(embed=embedVar)
  embedVar = discord.Embed(title="Sent you a DM!", color=colors["purple"])
  msg = await ctx.send(embed=embedVar)
  await msg.delete()

@slash.slash(name="view", guild_ids=guildIDs, description="See all the challenges available.")
async def view(ctx):
  embedVar = discord.Embed(title="Scunt " + constants["scuntYear"] + " challenge list", description=constants["challengesLink"],color=colors["purple"])
  await ctx.author.send(embed=embedVar)
  embedVar = discord.Embed(title="Sent you a DM!", color=colors["purple"])
  msg = await ctx.send(embed=embedVar)
  await msg.delete()


async def changeSplash():
  await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="you right now..."))

def errorEmbed(errorDescription):
  return discord.Embed(title="Error", description=errorDescription, color=colors["red"])

def createDescription(fields, newline=False):
  outputString = ""
  for field in fields:
    if(field["description"]=="" or field["description"]==False):
      continue
    outputString+="**"+str(field["title"])+":** "
    if(newline):
      outputString+="\n"
    outputString+=str(field["description"])
    outputString+="\n"
  return outputString

def getTeam(ctx):
  for role in ctx.author.roles:
    if("team" in role.name.lower()):
      return role.name.lower().replace("team","").replace(" ","")
  return False

client.run(keys["clientToken"])