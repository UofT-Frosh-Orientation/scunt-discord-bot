import requests

ROOT = 'https://api.orientation.skule.ca/scunt'
def loginUser(email, code):
  #login successful, generate team (based on discipline similar to how frosh groups are generated?)
  loginRequest = {
    'email': email,
    'code': code, 
  }
  print(loginRequest)
  r = requests.post(ROOT + '/login/discord', json=loginRequest)
  print(r.content)
  response = r.json()
  if r.status_code != 200:
    return {
      "errorMsg": response["errorMessage"]
    }
  else:
    return {
      "fullName": response["name"], 
      "team": response["teamNumber"], 
      "alreadyIn": False,
      "pronoun": response["pronouns"],
      "type": response["type"]
    }

def status(submission, team, discordId):
  #submission - number
  #return the status of the submission, any judge comments? Has been seen by judge etc
  statusRequest = {
    'missionNumber': submission, 
    'teamNumber': team,
    'discordId': discordId
  }
  r = requests.get(ROOT + '/get/mission/status', params=statusRequest)
  response = r.json()
  return response

def leaderboard():
  leaderboardParams = {
    'discord': 'true'
  }
  r = requests.get(ROOT + '/get/leaderboard/scores', params=leaderboardParams)
  response = r.json()
  return response


# Backend structure - these functions are not yet called by the frontend

# /status <challenge>
# View status of a challenge
# def status(challenge, team)
# challenge - int
# team - int
# return [
#   {title:"Item description","description":value},
#   {title:"Category","description":value},
#   {title:"Points","description":value},
#   {title:"Completed status","description":value},
#   {title:"Points rewarded","description":value},
#   {title:"Judges comments","description":value},
# ]
# Put value to False or "" if missing info for status command

# /leaderboard
# View the leaderboard and points of every team
# def leaderboard()
# return [100,200,300,400,500,600,700,800]
# array of points - needs to correspond to team names listed in constants.json - teamRoles (chronological order)

# /login <email> <code?>
# Logs a user in, assigns nickname and team roles, store the discord tag in the database (in case we need to look up team name)
# def login(email, code, discordUserID)
# email - str
# code - int
# discordUserID - int
# if login successful:
# return {
#   "fullName" : value,
#   "team" : value,       #int or str shouldn't matter
#   "pronoun" : value
# }
# if error:
# return False