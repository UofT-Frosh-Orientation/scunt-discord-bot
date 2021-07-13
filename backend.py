def loginUser(email):
  #login successful, generate team (based on discipline similar to how frosh groups are generated?)
  if True:
    return {"fullName":"James Kokoska", "team":"1", "alreadyIn":False, "pronoun":"He/Him"}
  else:
  #login unsuccessful (user already logged in to discord, return team number)
    return {"team":"2", "alreadyIn":True}

def submit(submission, name, discordUser, team):
  #submission - number, name - the persons name submitting (discord nickname), discordUser - username string of person submitting, team - number
  #return the status of the submission (True if success, False if error), takes a string
  #will be a google drive link or a discord link linking to an attachment
  #Sends link to the judges
  return True


def status(submission):
  #submission - number
  #return the status of the submission, any judge comments? Has been seen by judge etc
  return True

