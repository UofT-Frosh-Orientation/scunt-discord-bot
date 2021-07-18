# Scunt Discord Bot
## Setup
### Dependencies
* This discord bot uses python version 3
* The following libraries need to be installed for the bot to function, via pip
  * ```pip install discord```
  * ```pip install -U discord-py-slash-command```

### Creating the bot and credentials
1. Head to the discord developer portal and create a new application
    * https://discord.com/developers/applications
2.  On the ```Bot``` side page, enable intents 
    ![intents](/setup/Intents.png)
3. On the ```OAuth2``` side page, specify scopes corresponding to the scope required by the bot
    ![scope](/setup/Scopes.png)
    * If the administrator permission cannot be enabled (may need discord server owner permissions) then only check the respective permissions used by the bot
    * Copy the link and invite to created Scunt discord
4. (optional) On the ```Bot``` side page change the ```ICON``` and ```USERNAME```
5. On the ```Bot``` side page copy the ```TOKEN``` for the ```keys.json```
    * Create a ```keys.json``` file in the root of the repository using the template below
    * Add the ```MONGOURI``` to access the registration database, and add all server IDs where the bot would connect to in the ```guildIDs``` list
    * Get server ID by right clicking the server name, ```Copy ID```
    * ```SERVERID``` : int
    * ```TOKEN``` and ```MONGOURI``` : str
    * Ensure this is added to ```.gitignore```
    ```
    {
      "clientToken": "TOKEN",
      "guildIDs":[SERVERID, SERVERID],
      "mongoURI": "MONGOURI"
    }
    ```
### Setting up the Scunt Discord - Roles and Permissions
  * Add the following roles to the discord channel
    
    > Add: ```Team 1```, ```Team 2```, ```Team 3```, ```Team 4```, ```Team 5```, ```Team 6```, ```Team 7```, ```Team 8``` roles - As defined under ```teamRoles``` in ```constants.json```

    > Add: ```Logged In``` role - As defined under the ```loggedInRole``` in ```constants.json```

    > Create a ```#welcome``` text channel - As defined under the ```welcomeChannel``` in ```constants.json```

    All invites to the Scunt server should redirect to this text channel

  * Manage permissions manually in the Discord server settings, for access to specific team text/audio channels
  * Users with the ```Logged In``` role should not have access to type messages in the ```#welcome``` channel

## Usage
### Automatic functionality
  * Status updates - DMs the user the status command if the status of a challenge they submitted changes. Usually updated the submitter with info on points rewarded and judge comments.
  * Upload updates - DMs the user with information on the content they just submitted, as a confirmation

### Commands
  * ```/login <email>``` - Adds a user to the respective team roles within the server, sets the ```Logged In``` role, and sets nickname to preferred name and appends pronouns
  * ```/submit <number>``` - Submits via discord to the judges. The next message the user sends should be an attachment, and the bot will push this to the judges. If the user does not send another message within the timeout (30 seconds), an error message will be sent. User needs to reference the challenge number, and users info gets pushed along to judges as well (name, team, discord user etc.)
  * ```/submit <number> <link>``` - Submits a challenge to the judges with a link (This link can be user submitted via Google Drive, Dropbox, etc.). User needs to reference the challenge number, and users info gets pushed along to judges as well (name, team, discord user etc.)
  * ```/status <number>``` - Retrieves and displays the status of a challenge. Can be submitted, not submitted, pending, or completed. When completed, judges comments, points earned etc. will return.
  * ```/help``` - DMs the user with commands the bot can do
  * ```/view``` - DMs the user with the list of challenges, or provides a link to the website/pdf (supplied in ```consatnts.json```)

### Backend functionality
  * Accesses the registration database to retrieve information on a user after login to the discord. Retrieves users name, pronouns, Scunt team, etc.
  * Submissions and status updates on challenges
  * Challenges get forwarded to the judges automatically 