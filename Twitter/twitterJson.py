#!/usr/bin/env python

import oauth2, json, sys, time, traceback
from mapReduce import calculateTriplets

CONSUMER_KEY = ""
CONSUMER_SECRET = ""
ACCESS_KEY = ""
ACCESS_SECRET = ""
consumer = None
access_token = None
client = None
apiCallCount = 0

#Ronaldo
seed=155659213
listOfTuples=[]
idsList=[seed]
idToNameMap={}

firstLevelFanout=100
secondLevelFanout=100

def getDataFromAPI():
  # connect using authorization
  global consumer, access_token, client, apiCallCount
  consumer = oauth2.Consumer(key=CONSUMER_KEY, secret=CONSUMER_SECRET)
  access_token = oauth2.Token(key=ACCESS_KEY, secret=ACCESS_SECRET)
  client = oauth2.Client(consumer, access_token)
  apiCallCount = 1;             
  data = None
  
  try:
    # seed call.
    # 5000 entries in 1 request. Use cursor for next page (next 5000)
    timeline_endpoint = "https://api.twitter.com/1.1/friends/ids.json?cursor=-1&user_id="+str(seed)
    response, data = client.request(timeline_endpoint)
    friends = json.loads(data)['ids'][:firstLevelFanout]
    for friend in friends:
      idsList.append(friend)
      listOfTuples.append((seed, friend))
    
      if(apiCallCount % 15 == 0):
        print 'Make 15 calls to Twitter. Sleeping for 15 min.'
        time.sleep(900) 

      timeline_endpoint = "https://api.twitter.com/1.1/friends/ids.json?cursor=-1&user_id="+str(friend)
      apiCallCount = apiCallCount+1
      response, data = client.request(timeline_endpoint)
      moreFriendsDict = json.loads(data)
      if 'ids' in moreFriendsDict.keys():
        moreFriends = moreFriendsDict['ids'][:secondLevelFanout]
        for moreFriend in moreFriends:
          idsList.append(moreFriend)
          listOfTuples.append((friend, moreFriend))
        
  except Exception as error:
    print traceback.format_exc()
    print json.loads(data)

def writeToFile(fileHandle, writeList):
  fileHandle.write(writeList)

# Max 100 IDs in 1 request
def getNamesForIds():
  global apiCallCount
  _start=0
  _size=len(idsList)
  while(_start < _size):
    stringIds = [str(x) for x in idsList[_start:_start+100]]
    ids=','.join(stringIds)
    _start = _start+100
    data = None

    if(apiCallCount % 15 == 0):
        print 'Make 15 calls to Twitter. Sleeping for 15 min.'
        time.sleep(900)  

    try:
      timeline_endpoint = "https://api.twitter.com/1.1/users/lookup.json?user_id="+ids
      apiCallCount = apiCallCount+1
      response, data = client.request(timeline_endpoint)
      info = json.loads(data)
      for i in range(len(info)):
        idToNameMap[info[i]['id']] = info[i]['screen_name']

    except Exception as error:
      print traceback.format_exc()
      print json.loads(data)

if __name__ == "__main__":
  getDataFromAPI()
  getNamesForIds()
  triplets=calculateTriplets(listOfTuples)

  for _triplet in triplets:
    print idToNameMap[_triplet[0]],'->',idToNameMap[_triplet[1]],'->',idToNameMap[_triplet[2]]

  print 'Total Twitter API calls made = ', apiCallCount
  sys.exit(1)

  fileHandle = open('list.txt','w')
  for myTuple in listOfTuples:
    writeToFile(fileHandle, str(myTuple) + "\n")
  fileHandle.close()
