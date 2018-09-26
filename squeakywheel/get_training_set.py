#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 18 10:14:39 2018

@author: rcarns
"""

def RetrieveSingleAccountTweets(api,accountname,isSupport,maxTweets=10000):
    # the below code draws from 
    # https://stackoverflow.com/questions/38555191/get-all-twitter-mentions-using-tweepy-for-users-with-millions-of-followers

    import tweepy
    import pandas as pd
    import numpy as np
    import pickle
    from connections import twitterapi
    
    tweetsPerQry = 100
    sinceId = None
    atuser = '@'+account

    retweet_filter='-filter:retweets'
    reply_filter = '-filter:replies'
    searchQuery = atuser+' AND '+retweet_filter+' AND '+reply_filter
    

    max_id = -1
    tweetdict_list = []
    tweetCount = 0
    tweetProgress = 0
    #fName = 'tweetlist.txt'
    #with open(fName, 'w') as fname:
    list_of_tweets = []
    while tweetCount < maxTweets:
            try:
                if (max_id <= 0):
                    if (not sinceId):
                        new_tweets = api.search(q=searchQuery, count=tweetsPerQry, tweet_mode='extended')
                    else:
                        new_tweets = api.search(q=searchQuery, count=tweetsPerQry,
                                                since_id=sinceId)
                else:
                    if (not sinceId):
                        new_tweets = api.search(q=searchQuery, count=tweetsPerQry,
                                                max_id=str(max_id - 1),tweet_mode='extended')
                        print('foo')
                    else:
                        new_tweets = api.search(q=searchQuery, count=tweetsPerQry,
                                                max_id=str(max_id - 1),
                                                since_id=sinceId)
                if not new_tweets:
                    print("No more tweets found")
                    break
                for tweet in new_tweets:
                    #print(tweet.created_at.strftime('%x %X')+' '+tweet.full_text)
                    tweetson = tweet._json
                    list_of_tweets.append(tweet._json)
                    tweetdict = {}
                    tweetdict['text'] = tweetson['full_text']
                    tweetdict['mentions'] = tweetson['entities']['user_mentions']
                    tweetdict['source'] = accountname
                    if isSupport == True:
                        tweetdict['choose_one']='complaint'
                        tweetdict['class_label'] = 1
                    elif isSupport == False:
                        tweetdict['choose_one']='neutral'
                        tweetdict['class_label'] = 0
                    tweetdict_list.append(tweetdict)

                tweetCount += len(new_tweets)
                if tweetCount//1000>tweetProgress:
                    print("Downloaded {0} tweets for {1}".format(tweetCount,accountname))
                    tweetProgress+=1
                    print(str(tweetCount),str(maxTweets))
                max_id = new_tweets[-1].id
            except tweepy.TweepError as e:
                # Just exit if any error
                print("some error : " + str(e))
                break
    #dataframe = pd.DataFrame(tweetdict_list)
    #picklefile = open(storagefile,'wb')
    #pickle.dump(list_of_tweets,picklefile)
    #picklefile.close()
    return tweetdict_list,tweetCount
    
import tweepy
import pandas as pd
import numpy as np
import pickle
import time
from connections import twitterapi, postgresconnect

api = twitterapi()

# check how many searches are left in this time window
check = api.rate_limit_status()
reset_time = check['resources']['search']['/search/tweets']['reset']
import datetime
reset_formatted = datetime.datetime.fromtimestamp(reset_time).strftime('%X')
print(reset_formatted)
print(check['resources']['search'])

# get names of corporate twitters
CorpTwitters = pd.read_csv('CorpTwittersAll.txt',names=['Main','Support','Sector'])
#CorpTwitters = CorpTwitters[CorpTwitters['Sector']=='retail']
ComplaintAccounts = CorpTwitters['Support'].apply(lambda x: x[1:].lower())
MainAccounts = CorpTwitters['Main'].apply(lambda x: x[1:].lower())
maxtweets = 10000

complaintlist = []
neutrallist = []
for i in range(len(CorpTwitters)):
    maxtweets = 10000
    for accounttype in ['Support','Main']:
        account = CorpTwitters.loc[i,accounttype]
        atuser = '@'+account
        if accounttype=='Support':
            type = 'complaint'
            complaintdict_list,tweetCount = RetrieveSingleAccountTweets(api,atuser,True,maxtweets)
            complaintlist.extend(complaintdict_list)
            maxtweets = tweetCount
            print(account,str(maxtweets))
            
        elif accounttype=='Main':
            print(account,str(maxtweets))
            type='neutral'
            neutraldict_list,tweetCount = RetrieveSingleAccountTweets(api,atuser,False,maxtweets)
            neutrallist.extend(neutraldict_list)
            
complaintframe = pd.DataFrame(complaintlist)
storagefile = 'complaint'+'tweets'+time.strftime("%Y%m%d-%H%M%S")+'.dat'
with open(storagefile,'wb') as picklefile:
    pickle.dump(complaintframe,picklefile)
    
neutralframe = pd.DataFrame(neutrallist)    
storagefile = 'neutral'+'tweets'+time.strftime("%Y%m%d-%H%M%S")+'.dat'
with open(storagefile,'wb') as picklefile:
    pickle.dump(neutralframe,picklefile)

    


            
#for account in ComplaintAccounts[:5]:
#    print(account)
#    type = 'complaint'
#    atuser = '@'+account
#    #import time
#    #retweet_filter='-filter:retweets'
#    #reply_filter = '-filter:replies'
#    #searchQuery = atuser+' AND '+retweet_filter+' AND '+reply_filter# + 'AND until:2018-09-11'
#    #storagefile = type+'tweets'+time.strftime("%Y%m%d-%H%M%S")+'.dat'
#    complaintdict_list,tweetCount = RetrieveSingleAccountTweets(api,atuser,True,maxtweets)
#    complaintlist.extend(complaintdict_list)
#    maxtweets = tweetCount
#    #import shutil
#    #shutil.copy(storagefile,type+'tweets.dat')
#neutrallist = []
#for account in MainAccounts[:5]:
#    print(account)
#    type = 'neutral'
#    atuser = '@'+account
#    #import time
#    #retweet_filter='-filter:retweets'
#    #reply_filter = '-filter:replies'
#    #searchQuery = atuser+' AND '+retweet_filter+' AND '+reply_filter# + 'AND until:2018-09-11'
#    #storagefile = type+'tweets'+time.strftime("%Y%m%d-%H%M%S")+'.dat'
#    neutraldict_list,tweetCount = RetrieveSingleAccountTweets(api,atuser,False,maxtweets)
#    neutrallist.extend(neutraldict_list)
#    #maxtweets = tweetCount
#    #import shutil
#    #shutil.copy(storagefile,type+'tweets.dat')
#    





                