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

def postgresconnect(db_name):
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
    return engine, con
        