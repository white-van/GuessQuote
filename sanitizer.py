from old_quotes import quotes



IdToName = {}

allQuotes = []


filteredChannels = [] #add filtered channels here
filteredUserIds = [] #add filtered userid's here
for quote in quotes:
  id = quote['id'].encode("ascii", "ignore").decode()
  nick = quote['nick'].encode("ascii", "ignore").decode()
  userId = quote['userId']
  channel = quote.get('channel', None)
  if channel != None:
    channel = channel.encode("ascii", "ignore").decode()
  text = quote['text'].encode("ascii", "ignore").decode()
  
  isClean = True
  if channel != None:
    for filteredChannel in filteredChannels:
      if filteredChannel in channel:
        isClean = False 
        break
  for filteredUserId in filteredUserIds:
    if filteredUserId == userId:
      isClean = False
      break

  if nick == '' or text == '':
    isClean = False

  if isClean:
    newSet = IdToName.get(userId, set())
    newSet.add(nick.lower())
    IdToName[userId] = newSet
    allQuotes += [{'id': id, 'text': text, 'nick': nick.lower()}]

del IdToName['0'] #random additions

counter = 1

name_alias = {}
for aliases in IdToName.values():
  for alias in aliases:
    if (name_alias.get(alias, None) != None):
      print('found dup:', alias, name_alias[alias])
    
    name_alias[alias] = name_alias.get(alias, []) + [counter]
  counter += 1

#print(allQuotes)
#print(name_alias)