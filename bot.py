# Dependencies
# pip install discord
# pip install -U discord-py-slash-command
# pip install --upgrade Pillow


# TODO
# DM when judge assigns points or comments or accepts
# Error checking on frontend

import discord
import sys
import json
import backend
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash.model import SlashCommandOptionType
from PIL import Image, ImageDraw, ImageFont
import io
from discord import File

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
    "yellow": 0xfcd703,
    "black": 0x1c1c1c,
    "white": 0xfcfcfc,
}


@client.event
async def on_message(msg):
    command = msg.content.split(" ")
    print(command)
    try:
        if str(msg.channel.type) == "private":
            if command[0] == "help" or command[0] == "/help":
                await sendHelp(msg)
            elif command[0] == "view" or command[0] == "/view":
                await sendView(msg)
            elif command[0] == "leaderboard" or command[0] == "/leaderboard":
                await sendLeaderboard(msg)
            elif command[0] == "status" or command[0] == "/status":
                await sendStatus(msg, command[1], True)
    except:
        await msg.author.send(embed=errorEmbed(
            "There was an error with your command. You most likely forgot a parameter.\nType /help for more information."))


@client.event
async def on_ready():
    print("Username: " + client.user.name)
    await changeSplash()


@client.event
async def on_member_join(member):
    if sys.argv[1] == 1:
        channel = discord.utils.get(member.guild.channels, name=constants["welcomeChannel"])
        embedVar = discord.Embed(title="🎉 Welcome to the Scunt Discord " + member.display_name + "!", description="",
                                 color=colors["purple"])
        embedVar.add_field(name="Please use the /login <email> <code>", value="(same email as registration)",
                           inline=False)
        await channel.send(embed=embedVar)


# ---------------------------------------------------------------------------------
# Test commands listed below. Use it to test basic functionality of the bot
# ---------------------------------------------------------------------------------
# @slash.slash(name="hello", guild_ids=guildIDs, description="Used to test your bot.", options = [])
# async def hello(ctx):
#   embedVar = discord.Embed(title="Hello " + ctx.author.name, color=colors["purple"])
#   await ctx.send(embed=embedVar)
#   return

@slash.slash(name="login", guild_ids=guildIDs,
             description="Used to get access to your Scunt team. Use the same email as registration.", options=[
        create_option(
            name="email",
            description="Use your registration email for F!rosh week",
            option_type=SlashCommandOptionType.STRING,
            required=True
        ),
        create_option(
            name="code",
            description="Use the code we've given you, you can find this by logging into the orientation or scunt site",
            option_type=SlashCommandOptionType.STRING,
            required=True
        ),
    ])
# todo - send error if email was entered and not in database
# todo - backend can send fullName field or preferred name if not empty
async def login(ctx, email, code):
    print(ctx)
    if getLogin(ctx):
        print(getLogin(ctx))
        await ctx.send(embed=errorEmbed("You have already logged in to Discord."))
        return
    if "@" in email:
        loginResponse = backend.loginUser(email, code)
        print(loginResponse)
        print(ctx)
        if 'errorMsg' in loginResponse:
            print(loginResponse["errorMsg"])
            embedVar = discord.Embed(title="Sent you a DM!", color=colors["purple"])
            msg = await ctx.send(embed=embedVar)
            # await msg.delete()
            await ctx.author.send(embed=errorEmbed(loginResponse['errorMsg']))
            return
        if loginResponse['alreadyIn']:
            print("Already logged in")
            embedVar = discord.Embed(title="Sent you a DM!", color=colors["purple"])
            msg = await ctx.send(embed=embedVar)
            # await msg.delete()
            await ctx.author.send(embed=errorEmbed("You have already logged in."))
            return
        try:
            await ctx.author.add_roles(
                discord.utils.get(ctx.author.guild.roles, name=constants["teamRoles"][int(loginResponse["team"]) - 1]))
            await ctx.author.add_roles(discord.utils.get(ctx.author.guild.roles, name=constants["loggedInRole"]))
            if loginResponse["type"] == 'leadur':
                await ctx.author.add_roles(discord.utils.get(ctx.author.guild.roles, name=f"Team {loginResponse['team']} Leedur"))
            await ctx.author.edit(nick=(loginResponse["fullName"] + " (" + loginResponse["pronoun"] + ")")[0:31])
        except Exception as e:
            print("error:")
            print(e)
            await ctx.send(embed=errorEmbed(str(e)))
        else:
            embedVar = discord.Embed(title="Sent you a DM!", color=colors["purple"])
            print(embedVar)
            msg = await ctx.send(embed=embedVar)
            # await msg.delete()
            embedVar = discord.Embed(title="Login successful, " + loginResponse["fullName"],
                                     description="You are on team #" + str(loginResponse[
                                                                               "team"]) + " and you now have access to the respective channels.",
                                     color=colors["green"])
            await ctx.author.send(embed=embedVar)
    else:
        await ctx.send(
            embed=errorEmbed("Please enter a valid email and try again. Use the same email as you used to register."))


@slash.slash(name="status", guild_ids=guildIDs, description="View the status of a mission", options=[
    create_option(
        name="mission", description="The mission number",
        option_type=SlashCommandOptionType.INTEGER,
        required=True
    ),
])
async def status(ctx, mission):
    await sendStatus(ctx, mission, False)
    embedVar = discord.Embed(title="Sent you a DM!", color=colors["purple"])
    msg = await ctx.send(embed=embedVar)
    # await msg.delete()


async def sendStatus(ctx, mission, DM):
    if (DM):
        await sendMessage(ctx, errorEmbed('Please use this command on the Scunt Discord server only.'), DM)
        return
    if int(mission) <= 0:
        await sendMessage(ctx, errorEmbed('Invalid Mission Number'), DM)
        return
    team = await getTeam(ctx)
    if team is not False:
        statusResponse = backend.status(mission, team, ctx.author.id)
        print(statusResponse)
        if 'errorMsg' in statusResponse:
            await sendMessage(ctx, errorEmbed(statusResponse['errorMsg']), DM)
            return
        embedVar = discord.Embed(title="Challenge " + str(mission), description=createDescription([
            {"title": "Name", "description": statusResponse["name"]},
            {"title": "Category", "description": statusResponse["category"]},
            {"title": "Status", "description": statusResponse["missionStatus"]},
            {"title": "Points rewarded", "description": statusResponse["points"]},
        ]), color=colors["purple"])
        await ctx.author.send(embed=embedVar)
    else:
        await ctx.send(embed=errorEmbed("You are not on a team! Please use /login"))


@slash.slash(name="help", guild_ids=guildIDs, description="See all the commands available.")
async def help(ctx):
    await sendHelp(ctx)
    embedVar = discord.Embed(title="Sent you a DM!", color=colors["purple"])
    msg = await ctx.send(embed=embedVar)
    # await msg.delete()


async def sendHelp(ctx):
    embedVar = discord.Embed(title="Available Scunt " + constants["scuntYear"] + " commands", color=colors["purple"])
    for command in constants["commands"]:
        embedVar.add_field(name=command["title"], value=command["description"], inline=False)
    await ctx.author.send(embed=embedVar)


@slash.slash(name="missions", guild_ids=guildIDs, description="See all the missions available.")
async def missions(ctx):
    await sendMissions(ctx)
    embedVar = discord.Embed(title="Sent you a DM!", color=colors["purple"])
    msg = await ctx.send(embed=embedVar)
    # await msg.delete()


async def sendMissions(ctx):
    embedVar = discord.Embed(title="Scunt " + constants["scuntYear"] + " mission list",
                             description=constants["challengesLink"], color=colors["purple"])
    await ctx.author.send(embed=embedVar)


@slash.slash(name="leaderboard", guild_ids=guildIDs, description="View the current leaderboard standings.")
async def leaderboard(ctx):
    await sendLeaderboard(ctx)
    embedVar = discord.Embed(title="Sent you a DM!", color=colors["purple"])
    msg = await ctx.send(embed=embedVar)
    # await msg.delete()


async def sendLeaderboard(ctx):
    # For testing:
    # teamPoints = [150,100,200,300,400,100,200,300,100,100,200,500]
    leaderboardResponse = backend.leaderboard()
    if 'errorMsg' in leaderboardResponse:
        await sendMessage(ctx, errorEmbed(leaderboardResponse['errorMsg']), True)
        return
    teamPoints = leaderboardResponse["teamScores"]
    if (len(constants["teamRoles"]) != len(teamPoints)):
        print("There was a mismatch between teams and the length of the leaderboard!")
        return

    IMAGE_WIDTH = 800
    heightTeam = 50
    IMAGE_HEIGHT = len(constants["teamRoles"]) * heightTeam + 90
    image = Image.new('RGB', (IMAGE_WIDTH, IMAGE_HEIGHT))

    # create object for drawing
    draw = ImageDraw.Draw(image)

    # white background
    draw.rectangle([0, 0, IMAGE_WIDTH, IMAGE_HEIGHT], fill=colors["white"])

    # draw title
    font = ImageFont.truetype('ComicSansMS3.ttf', 45)
    text = "Scunt " + constants["scuntYear"] + " Leaderboard"
    textWidth, textHeight = draw.textsize(text, font=font)
    x = (IMAGE_WIDTH - textWidth) // 2
    draw.text((x, 20), text, fill=colors["black"], font=font)

    # draw text and bars
    minBarWidth = 75
    maxBarWidth = 500
    offset = 35
    teamNumber = 0
    minValue = min(teamPoints)
    maxValue = max(teamPoints)
    range = maxValue - minValue
    if range == 0:
        range = 100
    for team in constants["teamRoles"]:
        font = ImageFont.truetype('ComicSansMS3.ttf', 26)
        textWidth, textHeight = draw.textsize(team, font=font)
        textWidth = 80
        offset = offset + heightTeam
        textPaddingLeft = 20
        barPaddingLeft = 30
        teamPointsPercent = (teamPoints[teamNumber] - minValue) / range
        draw.rounded_rectangle((textWidth + textPaddingLeft + barPaddingLeft, offset + 3,
                                textWidth + textPaddingLeft + barPaddingLeft + (
                                            teamPointsPercent * maxBarWidth + minBarWidth), offset + textHeight),
                               fill="purple", radius=7)
        draw.text((textPaddingLeft, offset - 2), team, fill=(50, 0, 120), font=font)

        font = ImageFont.truetype('ComicSansMS3.ttf', 20)
        textWidthScore, textHeightScore = draw.textsize(str(teamPoints[teamNumber]), font=font)
        draw.text((textWidth + textPaddingLeft + barPaddingLeft + (teamPointsPercent * maxBarWidth + minBarWidth + 10),
                   offset + 3), str(teamPoints[teamNumber]), fill=(50, 0, 120), font=font)
        teamNumber = teamNumber + 1

    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)
    await ctx.author.send(file=File(buffer, 'myimage.png'))


async def changeSplash():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="you right now..."))


def errorEmbed(errorDescription):
    return discord.Embed(title="Error", description=errorDescription, color=colors["red"])


def createDescription(fields, newline=False):
    outputString = ""
    for field in fields:
        if (field["description"] == "" or field["description"] == False):
            continue
        if (str(field["title"]) != ""):
            outputString += "**" + str(field["title"]) + ":** "
        if (newline):
            outputString += "\n"
        outputString += str(field["description"])
        outputString += "\n"
    return outputString


async def getTeam(ctx):
    for role in ctx.author.roles:
        if ("team" in role.name.lower()):
            return role.name.lower().replace("team", "").replace(" ", "")
    return False


def getLogin(ctx):
    for role in ctx.author.roles:
        if (constants["loggedInRole"] == role.name):
            return True
    return False


def getDiscordTag(ctx):
    print(ctx.author.name + "#" + str(ctx.author.discriminator))
    return ctx.author.name + "#" + str(ctx.author.discriminator)


async def sendMessage(ctx, embed, DM):
    if DM:
        await ctx.author.send(embed=embed)
    else:
        await ctx.send(embed=embed)


client.run(keys["clientToken"])
