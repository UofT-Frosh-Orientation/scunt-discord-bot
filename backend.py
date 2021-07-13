def loginUser(email):
  #login successful, generate team (based on discipline similar to how frosh groups are generated?)
  if True:
    return {"fullName":"James Kokoska", "team":"1", "pronouns":"he/him", "alreadyIn":False}
  else:
  #login unsuccessful (user already logged in probably, return team number)
    return {"team":2, "alreadyIn":True}