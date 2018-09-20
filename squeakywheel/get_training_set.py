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
                if tweetCount//100>tweetProgress:
                    print("Downloaded {0} tweets for {1}".format(tweetCount,accountname))
                    tweetProgress+=1
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
for account in ComplaintAccounts:
    print(account)
    type = 'complaint'
    atuser = '@'+account
    #import time
    #retweet_filter='-filter:retweets'
    #reply_filter = '-filter:replies'
    #searchQuery = atuser+' AND '+retweet_filter+' AND '+reply_filter# + 'AND until:2018-09-11'
    #storagefile = type+'tweets'+time.strftime("%Y%m%d-%H%M%S")+'.dat'
    complaintdict_list,tweetCount = RetrieveSingleAccountTweets(api,atuser,True,maxtweets)
    complaintlist.extend(complaintdict_list)
    maxtweets = tweetCount
    #import shutil
    #shutil.copy(storagefile,type+'tweets.dat')
neutrallist = []
for account in MainAccounts:
    print(account)
    type = 'neutral'
    atuser = '@'+account
    #import time
    #retweet_filter='-filter:retweets'
    #reply_filter = '-filter:replies'
    #searchQuery = atuser+' AND '+retweet_filter+' AND '+reply_filter# + 'AND until:2018-09-11'
    #storagefile = type+'tweets'+time.strftime("%Y%m%d-%H%M%S")+'.dat'
    neutraldict_list,tweetCount = RetrieveSingleAccountTweets(api,atuser,False,maxtweets)
    neutrallist.extend(neutraldict_list)
    #maxtweets = tweetCount
    #import shutil
    #shutil.copy(storagefile,type+'tweets.dat')
    

def clean_text(df,text_field):     
    # taken from 'How to Solve 90% of NLP Problems'      
    df[text_field] = df[text_field].str.replace(r"http\S+", "")
    df[text_field] = df[text_field].str.replace(r"http", "")
    df[text_field] = df[text_field].str.replace(r"@\S+", "")
    df[text_field] = df[text_field].str.replace(r"[^A-Za-z0-9(),!?@\'\`\"\_\n\(\)]", " ")
    df[text_field] = df[text_field].str.replace(r"@", "at")
    df[text_field] = df[text_field].str.lower()
    df = df.fillna('')
    return df

complaintframe = pd.DataFrame(complaintlist)
neutralframe = pd.DataFrame(neutrallist)

  
train_tweets = pd.concat([complaintframe,neutralframe],0)
train_tweets = train_tweets.reset_index(drop=True)
train_tweets = clean_text(train_tweets,'text')
train_tweets = train_tweets.dropna('rows','any')
train_tweets.to_csv('train_tweets.csv')



                