#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 18 10:15:47 2018

@author: rcarns
"""


def twitterapi():
    import tweepy
    consumer_key = 'sP6xdQz6sf6W2EfFGoZ7dbH5C'
    consumer_secret = 't1AVU02CGlJCf1g0KnR9LMJT0LR8Ak5gVI5gWjAeWcqODag5eJ'

    access_token = '1039249629362118657-3oqguUqZ0L4mH6HGZ6Yy5HNjGaPDKR'
    access_token_secret = 'p2LYHujRz2GOwaUiOCXt4zkcPPYf3FE8GOX8l2mRduf50'

    auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)
    #auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth,wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    auth.secure = True
    return api

def pythontwitterapi():
    import twitter
    consumer_key = 'sP6xdQz6sf6W2EfFGoZ7dbH5C'
    consumer_secret = 't1AVU02CGlJCf1g0KnR9LMJT0LR8Ak5gVI5gWjAeWcqODag5eJ'

    access_token = '1039249629362118657-3oqguUqZ0L4mH6HGZ6Yy5HNjGaPDKR'
    access_token_secret = 'p2LYHujRz2GOwaUiOCXt4zkcPPYf3FE8GOX8l2mRduf50'
    api = twitter.Api(consumer_key=consumer_key,
                      consumer_secret=consumer_secret,
                      access_token_key=access_token,
                      access_token_secret=access_token_secret)
    return api

def postgresconnect(db_name):
    from sqlalchemy import create_engine
    from sqlalchemy_utils import database_exists, create_database
    import psycopg2
    import pandas as pd
    username = 'postgres'
    password = 'fish'     # change this
    host     = 'localhost'
    port     = '5432'            # default port that postgres listens on
    #db_name  = 'tweetdata'

    engine = create_engine( 'postgresql://{}:{}@{}:{}/{}'.format(username, password, host, port, db_name) )
    print(engine.url)

    if not database_exists(engine.url):
        create_database(engine.url)
    print(database_exists(engine.url))

    con = None
    con = psycopg2.connect(database = db_name, user = username, host=host,password=password)
    return engine, con


def GetTestSet(atuser,maxtweets):
    maxtweets = 250
    if not atuser[0]=='@':
        atuser = '@'+ atuser
    import time
    retweet_filter='-filter:retweets'
    reply_filter = '-filter:replies'
    searchQuery = atuser+' AND '+retweet_filter+' AND '+reply_filter# + 'AND until:2018-09-11'
    print(searchQuery)
    #storagefile = type+'tweets'+time.strftime("%Y%m%d-%H%M%S")+'.dat'
    storagefile = 'testtweetfile.dat'
    tweetCount = RetrieveTweets(searchQuery,storagefile,maxtweets)
    maxtweets = tweetCount
    #import shutil
    #shutil.copy(storagefile,type+'tweets.dat')

    testpickle = open('testtweetfile.dat','rb')
    testtweets = pickle.load(testpickle)
    testpickle.close()
    testfilename = 'test_tweets.txt'
    columns=['text','mentions','choose_one','class_label']
    testframe = pd.DataFrame(columns=columns,index=range(len(testtweets)))
    i = 0

    for tweet in testtweets:
        tweettext = tweet['full_text']
        testframe.at[i,'text']=tweettext
        testframe.at[i,'id'] = tweet['id_str']
        testframe.at[i,'mentions'] = tweet['entities']['user_mentions']
        testframe.at[i,'username'] = tweet['user']['screen_name']
        testframe.at[i,'created_at'] = tweet['created_at']
        testframe.at[i,'choose_one']=''
        testframe.at[i,'class_label']=2
        i+=1
    csv_name = 'test_tweets.csv'
    testframe.to_csv(csv_name)
    return csv_name


def RetrieveTweets(searchQuery,storagefile,maxTweets=10000):
    # the below code draws from
    # https://stackoverflow.com/questions/38555191/get-all-twitter-mentions-using-tweepy-for-users-with-millions-of-followers

    import tweepy
    import pandas as pd
    import numpy as np
    import pickle
    from connections import twitterapi

    tweetsPerQry = 100
    sinceId = None



    max_id = -1

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
                    list_of_tweets.append(tweet._json)
                tweetCount += len(new_tweets)
                if tweetCount//1000>tweetProgress:
                    print("Downloaded {0} tweets".format(tweetCount))
                    tweetProgress+=1
                max_id = new_tweets[-1].id
            except tweepy.TweepError as e:
                # Just exit if any error
                print("some error : " + str(e))
                break

    picklefile = open(storagefile,'wb')
    pickle.dump(list_of_tweets,picklefile)
    picklefile.close()
    return tweetCount

def RetrieveSingleAccountTweetsWithJson(api,accountname,isSupport,maxTweets=10000):
        # the below code draws from
        # https://stackoverflow.com/questions/38555191/get-all-twitter-mentions-using-tweepy-for-users-with-millions-of-followers

        import tweepy
        import pandas as pd
        import numpy as np
        import pickle
        from connections import twitterapi

        tweetsPerQry = 100
        sinceId = None
        atuser = '@'+accountname

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
                        tweetdict['json'] = tweetson
                        tweetdict['id'] = tweetson['id_str']
                        tweetdict['mentions'] = tweetson['entities']['user_mentions']
                        tweetdict['username'] = tweetson['user']['screen_name']
                        tweetdict['created_at'] = tweetson['created_at']
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

def RunModel(tweetframe):
    import pickle
    import os
    os.chdir('/home/rcarns/flaskapps/squeakywheel/')
    modelpickle = open('model.pkl','rb')
    [myclf,vectorizer] = pickle.load(modelpickle)
    list_corpus = tweetframe['text'].tolist()
    list_vectors = vectorizer.transform(list_corpus)
    predictions = myclf.predict(list_vectors)
    return predictions

def ExplainTweet(tweet):
    import pickle
    import os
    from lime import lime_text
    from sklearn.pipeline import make_pipeline
    os.chdir('/home/rcarns/flaskapps/squeakywheel/')
    class_names = ['complaint','neutral']
    modelpickle = open('model.pkl','rb')
    [myclf,vectorizer] = pickle.load(modelpickle)
    c = make_pipeline(vectorizer, myclf)
    from lime.lime_text import LimeTextExplainer
    explainer = LimeTextExplainer(class_names=class_names)
    exp = explainer.explain_instance(tweet, c.predict_proba, num_features=6)
    print(exp.as_list())
    return exp


