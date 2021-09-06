import requests

ROOT = 'https://scunt-2021.herokuapp.com'
def loginUser(email, code, username, id):
  #login successful, generate team (based on discipline similar to how frosh groups are generated?)
  loginRequest = {
    'email': email, 
    'code': code, 
    'discordUsername': username, 
    'id': id
  }
  r = requests.post(ROOT + '/login/discord', data=loginRequest)
  response = r.json()
  print(response)
  if response["status"] != 200:
    return {
      "errorMsg": response["errorMsg"]
    }
  else:
    return {
      "fullName": response["name"], 
      "team": response["teamNumber"], 
      "alreadyIn": response["discordSignedIn"], 
      "pronoun": response["pronouns"],
      "type": response["type"]
    }

def submit(submission, team, discordTag, discordId, url, mediaConsent):
  #submission - number, name - the persons name submitting (discord nickname), discordUser - username string of person submitting, team - number
  #return the status of the submission (True if success, False if error), takes a string
  #will be a google drive link or a discord link linking to an attachment
  #Sends link to the judges
  if mediaConsent == 'Yes':
    mediaConsentStr = 'true'
  else:
    mediaConsentStr = 'false'
  submitRequest = {
    'discordUsername': discordTag,
    'missionNumber': submission, 
    'teamNumber': team, 
    'submissionLink': url,
    "discordId": discordId,
    'isMediaConsent': mediaConsentStr
  }
  r = requests.post(ROOT + '/post/submission', data=submitRequest)
  response = r.json()
  print(response)
  return response


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

def lookupTeam(userId):
  getTeamParams = {
    'discordId': userId
  }
  r = requests.get(ROOT + '/get/discordUser/team', params=getTeamParams)
  response = r.json()
  return response


