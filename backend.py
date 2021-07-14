from pymongo import MongoClient
import bcrypt
import json

with open('keys.json', encoding='utf-8-sig') as k:
    keys = json.load(k)

client = MongoClient(keys["mongoURI"])
db = client.get_default_database()
froshes = db.froshes


async def login_user(email, password):
    # TODO: still need to check if user already signed in before, should probably make scunt collection in mongo

    # login successful, generate team (based on discipline similar to how frosh groups are generated?)
    frosh = froshes.find_one({"email": email})
    logged_in = bcrypt.checkpw(password, frosh["password"])
    if logged_in:
        return {"fullName": frosh["fullName"], "team": "1", "alreadyIn": False, "pronoun": frosh["pronouns"]}
    else:
        # login unsuccessful (user already logged in to discord, return team number)
        return {"team": "2", "alreadyIn": True}


def submit(submission, name, discordUser, team):
    # submission - number, name - the persons name submitting (discord nickname), discordUser - username string of person submitting, team - number
    # return the status of the submission (True if success, False if error), takes a string
    # will be a google drive link or a discord link linking to an attachment
    # Sends link to the judges
    return True


def status(submission):
    # submission - number
    # return the status of the submission, any judge comments? Has been seen by judge etc
    return True
