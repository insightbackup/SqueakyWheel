import tweepy
import pandas as pd
import numpy as np
import pickle
from connections import twitterapi, postgresconnect
from sqlalchemy import *

import keras
import nltk
import pandas as pd
import numpy as np
import re

CorpTwitters = pd.read_csv('CorpTwittersAll.txt',names=['Main','Support','Sector'])
ComplaintAccounts = CorpTwitters['Support'].apply(lambda x: x[1:].lower())
MainAccounts = CorpTwitters['Main'].apply(lambda x: x[1:].lower())

db_name = 'tweetdata'
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

#engine,con = postgresconnect('tweetdata')


# open file with stored tweets and read into dataframe
complaintpickle = open('complainttweets20180927-145603.dat','rb')
complaintweets = pickle.load(complaintpickle)
complaintweets.columns
complaintpickle.close()
complainttrim = complaintweets.drop(['mentions','json'],axis=1)
complainttrim.to_sql('training_tweets',engine,if_exists='append')


complainfilename = 'complaintweets.txt'
columns=['id','text','username','created_at','source','choose_one','class_label']
complaintframe = pd.DataFrame(columns=columns,index=range(len(complaintweets)))
i = 0
#with open(complainfilename,'w') as complainfile:
tweetdict_list = []
for tweet in complaintweets:
    tweetson = tweet
    tweetdict = {}

    tweetdict['id'] = tweetson['id_str']
    #tweetdict['mentions'] = tweetson['entities']['user_mentions']
    tweetdict['username'] = tweetson['user']['screen_name']
    tweetdict['created_at'] = tweetson['created_at']
    tweetdict['text'] = tweetson['full_text']
    tweetdict['mentions'] = tweetson['entities']['user_mentions']
    for mention in tweetdict['mentions']:
        if mention['screen_name'].lower() in MainAccounts:
            tweetdict['source'] = mention
    #tweetdict['followers'] = followers
    #tweetdict['source'] = accountname
    tweetdict['choose_one']='complaint'
    tweetdict['class_label'] = 1

    tweetdict_list.append(tweetdict)
    i+=1

complaintframe = pd.DataFrame(tweetdict_list)
complainttrim = complaintframe.drop(['mentions'],axis=1)
complainttrim.to_sql('training_tweets',engine,if_exists='append')

neutralpickle = open('neutraltweets20180927-145604.dat','rb')
neutraltweets = pickle.load(neutralpickle)
neutralpickle.close()
#neutralfilename = 'neutraltweets.txt'
#columns=['id','text','username','created_at','source','choose_one','class_label']

#neutralframe = pd.DataFrame(columns=columns,index=range(len(neutraltweets)))

neutraltrim = neutraltweets.drop(['mentions','json'],axis=1)
neutraltrim.to_sql('training_tweets',engine,if_exists='append')


tweetdict_list = []
i=0
#with open(neutralfilename,'w') as neutralfile:
for tweet in neutraltweets:
        tweetson=tweet
        isComplaint=False
        for mention in tweet['entities']['user_mentions']:
            if mention['screen_name'].lower() in ComplaintAccounts:
                isComplaint=True
        if isComplaint==False:
            tweetdict = {}
            #tweetdict['json'] = tweetson
            tweetdict['id'] = tweetson['id_str']
            #tweetdict['mentions'] = tweetson['entities']['user_mentions']
            tweetdict['username'] = tweetson['user']['screen_name']
            tweetdict['created_at'] = tweetson['created_at']
            tweetdict['text'] = tweetson['full_text']
            tweetdict['mentions'] = tweetson['entities']['user_mentions']

            #tweetdict['followers'] = followers
            for mention in tweetdict['mentions']:
                if mention['screen_name'].lower() in MainAccounts:
                    tweetdict['source'] = mention

            #print(MainAccounts)

            tweetdict['choose_one']='neutral'
            tweetdict['class_label'] = 0
            tweetdict_list.append(tweetdict)

            i+=1


neutralframe = pd.DataFrame(tweetdict_list)
complaintframe.to_sql(engine,'training_tweets',if_exists='append')
neutraltrim = neutralframe.drop(['mentions'],axis=1)
neutraltrim.to_sql('training_tweets',engine,if_exists='append')


foo = engine.execute('SELECT * FROM pg_catalog.pg_tables')
tables = foo.fetchall
print(tables)
print(engine.table_names)
metadata = MetaData()
print(metadata.tables.keys())
metadata.reflect(engine)
