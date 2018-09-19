#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 17 16:17:01 2018

@author: rcarns
"""
'''retrieve tweets from a given twitter account or list of twitter accounts and 
 store them in the SQL database
 '''
import tweepy
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import psycopg2
import pandas as pd
from psycopg2.extras import Json


consumer_key = 'sP6xdQz6sf6W2EfFGoZ7dbH5C'
consumer_secret = 't1AVU02CGlJCf1g0KnR9LMJT0LR8Ak5gVI5gWjAeWcqODag5eJ'

access_token = '1039249629362118657-3oqguUqZ0L4mH6HGZ6Yy5HNjGaPDKR'
access_token_secret = 'p2LYHujRz2GOwaUiOCXt4zkcPPYf3FE8GOX8l2mRduf50'

auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)
#auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth,wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
auth.secure = True

username = 'postgres'
password = 'fish'     # change this
host     = 'localhost'
port     = '5432'            # default port that postgres listens on
db_name  = 'tweetdata'

engine = create_engine( 'postgresql://{}:{}@{}:{}/{}'.format(username, password, host, port, db_name) )
print(engine.url)

if not database_exists(engine.url):
    create_database(engine.url)
print(database_exists(engine.url))

con = None
con = psycopg2.connect(database = db_name, user = username, host=host,password=password)

retweet_filter='-filter:retweets'
reply_filter = '-filter:replies'
atuser = '@Starbucks'
tweetsPerQry = 100
searchQuery = atuser+' AND '+retweet_filter+' AND '+reply_filter
test_tweets = api.search(q=searchQuery, count=tweetsPerQry, tweet_mode='extended')
tweetframe = pd.DataFrame(columns=['tweet_id','tweet_json'],index=range(len(test_tweets)))
i=0
if i<10:
    for tweet in test_tweets:
        #print(tweet.id)
        tweetframe.loc[i]['tweet_id'] = tweet.id
        tweetframe.loc[i]['tweet_json'] = Json(tweet._json)
        i+=1

    
tablename = 'test_tweets'
cur = con.cursor()

tweetframe.to_sql(tablename,engine,if_exists='replace')
#if not engine.dialect.has_table(engine,tablename):
#    command = """
#        CREATE TABLE test_tweets(
#        tweet_id int,
#        tweet_json varchar(10000)
#        PRIMARY KEY (tweet_id)
#        )
#        """
#    cur.execute(command)
#    cur.close()
#    print('added_table')
#if engine.dialect.has_table(engine,tablename):
#    print('table exists')
#    cur.close()
#    
#comment = """
#    INSERT INTO test_tweets(tweet_id,tweet_json)
#        VALUES
            



