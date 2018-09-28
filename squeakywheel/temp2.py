#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 27 15:59:27 2018

@author: rcarns
"""
import connections
import pandas as pd
#get Twitter account to categorize
twitter_account = 'starbucks'#request.args.get('twitter_account')
api = connections.twitterapi()
pyapi = connections.pythontwitterapi()
tweetcount = 300
tweetlist, tweetcount = connections.RetrieveSingleAccountTweetsWithJson(api,twitter_account,False,tweetcount)
tf = pd.DataFrame(tweetlist)
 #print('columns'+tf.columns)
predictions = connections.RunModel(tf)
tf['predictions'] = predictions
numcomplaints = tf[tf['predictions']==1]['predictions'].count()
tweetjson = tf[tf['predictions']==1]['json'].tolist()
engine,con = connections.postgresconnect('tweetdata')
#sql_query="SELECT * FROM test_tweets"
tablename = twitter_account+'demo_tweets'
  #foo=pd.read_sql_query(sql_query,con)
tf_trim = tf.drop(['json','mentions'],axis=1)
tf_trim.to_sql(name=tablename,con=engine,if_exists='replace')