from flask import render_template
from flask import request
from flask import Flask, redirect, url_for, request
from squeakywheel import app
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import pandas as pd
import psycopg2
import connections
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
	user= {'nickname':'Jane'} #fake user
	return render_template("index.html",
		title='Home',
		user=user)

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
	#if request.method=='POST':
	#	return redirect(url_for('topics',twitter_account = twitter_account))
	api = connections.twitterapi()
	pyapi = connections.pythontwitterapi()
	tweetcount = 1000
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
	results = connections.GetTopics(tf[tf['predictions']==1])

	return render_template("squeakyoutput.html", numcomplaints = numcomplaints,tweettext=tweetjson,tweetcount=tweetcount,results=results)

@app.route('/topics/<twitter_account>')
def squeaky_topics(twitter_account):
	#twitter_account = request.args.get('twitter_account')
	sql_query="SELECT * FROM "+twitter_account+"demo_tweets"
	tf=pd.read_sql_query(sql_query,con)
	return render_template("squeakytopics.html", numcomplaints = numcomplaints,tweettext=tweetjson,tweetcount=tweetcount)
