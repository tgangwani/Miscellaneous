#!/usr/bin/env python

import sys, threading, math, itertools

listOfTuples=[]
numThreads=2
chunk=0
threads=[]
map1Out={}  # output of map stage1
map2Out={}  # output of map stage2
triplets=[]

def readInput():
  for line in open('test.txt'):
    myTuple = line.lstrip('(').rstrip('\n').rstrip(')').split(',')
    if len(myTuple) != 2:
      print 'Input read error'
      sys.exit(1)
    listOfTuples.append((int(myTuple[0]),int(myTuple[1].lstrip())))

def map1(threadID, lock):
  # initial allocation begin
  _start=threadID*chunk
  _end=min((threadID+1)*chunk, len(listOfTuples))
  _listOfTuples=listOfTuples[_start:_end] # first:last, last not included!
  # initial allocation end

  _keyValue={} # _keyValue is the local dictionary (key-value pair) with each thread
  for _tuple in _listOfTuples:
    if _tuple[0] in _keyValue.keys():
      _keyValue[_tuple[0]].append((1, _tuple[1]))
    else:
      _keyValue[_tuple[0]] = [(1, _tuple[1])]
    if _tuple[1] in _keyValue.keys():
      _keyValue[_tuple[1]].append((2, _tuple[0]))
    else:
      _keyValue[_tuple[1]] = [(2, _tuple[0])]

  # local dictionary computation complete. Now merge values in the global
  # dictionary - synchronization required!

  lock.acquire(1)
  for k,v in _keyValue.items():
    if k in map1Out.keys():
      map1Out[k].extend(v)
    else:
      map1Out[k] = v
  lock.release()
  return 

def map2(threadID, lock):
  # shuffle map1 output begin
  _start=threadID*chunk
  _end=min((threadID+1)*chunk, len(map1Out))
  i = iter(map1Out.items())
  _localDict=dict(itertools.islice(i, _start, _end))
  # shuffle map1 output end

  # reduce1 begin
  _reduce1Out=[]
  for k in _localDict.keys():
    _following=[]
    _followers=[]
    for _tuple in _localDict[k]:
      if _tuple[0] == 1:
        _following.append(_tuple[1])
      else:
        _followers.append(_tuple[1])
    _reduce1Out.append((k, _following, _followers))
  # reduce1 end
  
  # map2 begin - same node!
  _keyValue={}
  for _tuple in _reduce1Out:
    if _tuple[0] in _keyValue.keys():
      _keyValue[_tuple[0]].append((1, _tuple[1]))
    else:
      _keyValue[_tuple[0]] = [(1, _tuple[1])]
    for node in _tuple[1]:
      if node in _keyValue.keys():
        _keyValue[node].append((2, _tuple[2], _tuple[0]))
      else:
        _keyValue[node] = [(2, _tuple[2], _tuple[0])]
  
  # local dictionary computation complete. Now merge values in the global
  # dictionary - synchronization required!

  lock.acquire(1)
  for k,v in _keyValue.items():
    if k in map2Out.keys():
      map2Out[k].extend(v)
    else:
      map2Out[k] = v
  lock.release()
  # map2 end 
  return

def reduce2(threadID, lock):
  # shuffle map2 output begin
  _start=threadID*chunk
  _end=min((threadID+1)*chunk, len(map2Out))
  i = iter(map2Out.items())
  _localDict=dict(itertools.islice(i, _start, _end)) 
  # shuffle map2 output end

  for k in _localDict.keys():
    _listOfTuples=sorted(_localDict[k])
    _firstTuple=_listOfTuples[0]
    _listOfTuples.pop(0)
    assert _firstTuple[0]==1
    _following=_firstTuple[1]
    for _tuple in _listOfTuples:
      assert _tuple[0]==2
      for toCheckNode in _tuple[1]:
        if toCheckNode in _following:
          lock.acquire(1)
          # only add a triplet once!
          if [toCheckNode, _tuple[2], k] == sorted([toCheckNode, _tuple[2], k]):
            triplets.append((toCheckNode, _tuple[2], k))
          lock.release()

#if __name__=="__main__":
#  global threads, listOfTuples, chunk
#  readInput()

#reading from twitterJson.py rather than a text file
def calculateTriplets(twitterInput):
  global threads, listOfTuples, chunk
  listOfTuples = twitterInput
  lock = threading.Lock()
  
  # map1 start
  chunk = int(math.ceil(len(listOfTuples)*1.0 / numThreads))
  for i in range(numThreads):
    t = threading.Thread(target=map1, args=(i,lock,))
    threads.append(t)
    t.start()

  for i in range(numThreads):
    threads[i].join()
  threads=[]
  # map1 end
  
  # reduce1+map2 start
  chunk = int(math.ceil(len(map1Out)*1.0 / numThreads))
  for i in range(numThreads):
    t = threading.Thread(target=map2, args=(i,lock,))
    threads.append(t)
    t.start()

  for i in range(numThreads):
    threads[i].join()
  threads=[]
  # reduce1+map2 end

  #reduce2 start
  chunk = int(math.ceil(len(map2Out)*1.0 / numThreads))
  for i in range(numThreads):
    t = threading.Thread(target=reduce2, args=(i,lock))
    threads.append(t)
    t.start()

  for i in range(numThreads):
    threads[i].join()
  #reduce2 end

  return triplets
