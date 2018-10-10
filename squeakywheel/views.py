from flask import render_template
from flask import request
from flask import Flask, redirect, url_for, request
from squeakywheel import app
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import pandas as pd
import psycopg2
import importlib
import keys
import connections; importlib.reload(connections)
import twitter
#from connections import RetrieveSingleAccountTweetsWithJson,twitterapi
#from a_Model import ModelIt

user='postgres'
host = 'localhost'
dbname = 'textdata'
password = 'fish'
db = create_engine('postgres://%s%s/%s'%(user,host,dbname))
con = None
con = psycopg2.connect(database=dbname, user=user, host = host, password = password)
@app.route('/')
@app.route('/index')
def index():
    return render_template("squeakyinput.html")

@app.route('/db')
def info_stats():
    sql_query = """
				SELECT * FROM clean_questions WHERE choose_one='complaint';
				"""
    query_results = pd.read_sql_query(sql_query,con)
    complaints = ""
    for i in range(0,10):
        complaints += query_results.iloc[i]['tokens']
        complaints += "<br>"
    return complaints

@app.route('/db_fancy')
def cesareans_page_fancy():
    sql_query = """
               SELECT index, attendant, birth_month FROM birth_data_table WHERE delivery_method='Cesarean';
                """
    query_results=pd.read_sql_query(sql_query,con)
    births = []
    for i in range(0,query_results.shape[0]):
        births.append(dict(index=query_results.iloc[i]['index'], attendant=query_results.iloc[i]['attendant'], birth_month=query_results.iloc[i]['birth_month']))
    return render_template('cesareans.html',births=births)

@app.route('/input')
def squeaky_input():
    return render_template("squeakyinput.html")

@app.route('/output')
def squeaky_output():
	#get Twitter account to categorize
	twitter_account = request.args.get('twitter_account')

	#connect to SQL database
	engine,con = keys.postgresconnect('tweetdata')

	runlocal = False
	#if running locally, get tweets from SQL; otherwise get from Internet
	if runlocal==True:
		tf = pd.read_sql('united_demo_tweets',engine)
		tf = tf.drop_duplicates()
	else:
		api = keys.twitterapi()
		pyapi = keys.pythontwitterapi()
		tweetcount = 500
		tweetlist, tweetcount = connections.RetrieveSingleAccountTweetsWithJson(api,twitter_account,False,tweetcount)
		tf = pd.DataFrame(tweetlist)
	#print('columns'+tf.columns)
	# number of tweets to return
	n=20
	predictions,probabilities = connections.RunModel(tf)
	tf['predictions'] = predictions
	tf['probabilities'] = probabilities[:,1]
	numcomplaints = tf[tf['predictions']==1]['predictions'].count()


	toptweets = tf.sort_values(by=['probabilities'],ascending=False)[:n]
	toptweets['followers'] = 0
	#tweetelements = toptweets.to_dict('records')

	tweetjson = []

	#print(toptweets.loc['probabilities',2])
	for index,row in toptweets.iterrows():
	    newdict = {}
	    newdict['json'] = row['json']
	    newdict['probabilities'] = '%.2f' % (row['probabilities'])
	    user = api.get_user(row['username'])
	    newdict['followers'] = user.followers_count
	    tweetjson.append(newdict)

	#tweetjson = toptweets[toptweets['predictions']==1]['json'].tolist()

	tablename = twitter_account+'_demo_tweets'
	tf_trim = tf.drop(['json','mentions'],axis=1)
	#tf_trim.to_sql(name=tablename,con=engine,if_exists='append')
	results = connections.GetTopics(tf[tf['predictions']==1])

	return render_template("squeakyoutput.html", numcomplaints = numcomplaints,
							tweettext=tweetjson,tweetcount=tweetcount,
							results=results)

@app.route('/topics/<twitter_account>')
def squeaky_topics(twitter_account):
	#twitter_account = request.args.get('twitter_account')
	sql_query="SELECT * FROM "+twitter_account+"demo_tweets"
	tf=pd.read_sql_query(sql_query,con)
	return render_template("squeakytopics.html", numcomplaints = numcomplaints,tweettext=tweetjson,tweetcount=tweetcount)
