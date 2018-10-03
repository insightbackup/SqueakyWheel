#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 18 10:15:47 2018

@author: rcarns
"""





def GetTestSet(atuser,maxtweets):
    maxtweets = 250
    if not atuser[0]=='@':
        atuser = '@'+ atuser
    import time
    retweet_filter='-filter:retweets'
    reply_filter = '-filter:replies'
    searchQuery = atuser+' AND '+retweet_filter+' AND '+reply_filter+' AND lang:en'# + 'AND until:2018-09-11'
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
                        #user = api.get_user(tweetson['user']['screen_name'])
                        #followers = user.followers_count
                        tweetdict = {}
                        tweetdict['json'] = tweetson
                        tweetdict['id'] = tweetson['id_str']
                        tweetdict['mentions'] = tweetson['entities']['user_mentions']
                        tweetdict['username'] = tweetson['user']['screen_name']
                        tweetdict['created_at'] = tweetson['created_at']
                        tweetdict['text'] = tweetson['full_text']
                        tweetdict['mentions'] = tweetson['entities']['user_mentions']
                        #tweetdict['followers'] = followers
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
    #os.chdir('/home/rcarns/flaskapps/squeakywheel/')
    currentdir = os.getcwd()
    print(currentdir)
    if 'squeakywheel' not in currentdir:
        os.chdir('./squeakywheel')
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

def GetTopics(tweetframe):
    import pandas as pd
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
    from sklearn.decomposition import NMF, LatentDirichletAllocation

    tweetframe = ProcessTweets(tweetframe)
    # NMF is able to use tf-idf
    tfidf_vectorizer = TfidfVectorizer(max_df=0.95, min_df=2)
    #tfidf = tfidf_vectorizer.fit_transform(documents)
    #tfidf_feature_names = tfidf_vectorizer.get_feature_names()

    no_topics = 10

    # Run NMF
    n_docs = 5
    no_top_words = 5
    tweetlist = tweetframe['processed_text'].tolist()
    tfidf_vectorizer.fit(tweetlist)
    tfidf_tweets = tfidf_vectorizer.transform(tweetlist)

    # get list of feature names
    feature_names = tfidf_vectorizer.get_feature_names()
    nmf = NMF(n_components=no_topics, random_state=1, alpha=.1, l1_ratio=.5, init='nndsvd')

    nmf.fit(tfidf_tweets)
    print(tweetframe.columns)
    results = []
    for topic_idx, topic in enumerate(nmf.components_):
        featnames = (" ".join([feature_names[i]
                for i in topic.argsort()[:-no_top_words - 1:-1]]))
        tweet_topics = nmf.transform(tfidf_tweets)
        top_doc_indices = np.argsort( tweet_topics[:,topic_idx] )[::-1][0:n_docs]
        topic_list=[]
        for doc_index in top_doc_indices:
            doc_dict = {}
            #print(doc_index)
            doc_dict['username']=tweetframe['username'].iloc[doc_index]
            doc_dict['id']=tweetframe['id'].iloc[doc_index]
            doc_dict['text'] = tweetframe['text'].iloc[doc_index]
            doc_dict['feature_names'] = featnames
            topic_list.append(doc_dict)
        results.append(topic_list)
    return results

def ProcessTweets(tf):
    import tweepy
    import pandas as pd
    import numpy as np
    import pickle
    from connections import twitterapi, postgresconnect

    import keras
    import nltk
    import pandas as pd
    import numpy as np
    import re
    import codecs
    import textblob

    # Gensim
    import gensim
    import gensim.corpora as corpora
    from gensim.utils import simple_preprocess
    from gensim.models import CoherenceModel

    from nltk.tokenize import RegexpTokenizer

    import re
    cList = {
      "ain't": "am not",
      "aren't": "are not",
      "can't": "cannot",
      "can't've": "cannot have",
      "'cause": "because",
      "could've": "could have",
      "couldn't": "could not",
      "couldn't've": "could not have",
      "didn't": "did not",
      "doesn't": "does not",
      "don't": "do not",
      "hadn't": "had not",
      "hadn't've": "had not have",
      "hasn't": "has not",
      "haven't": "have not",
      "he'd": "he would",
      "he'd've": "he would have",
      "he'll": "he will",
      "he'll've": "he will have",
      "he's": "he is",
      "how'd": "how did",
      "how'd'y": "how do you",
      "how'll": "how will",
      "how's": "how is",
      "I'd": "I would",
      "I'd've": "I would have",
      "I'll": "I will",
      "I'll've": "I will have",
      "I'm": "I am",
      "I've": "I have",
      "isn't": "is not",
      "it'd": "it had",
      "it'd've": "it would have",
      "it'll": "it will",
      "it'll've": "it will have",
      "it's": "it is",
      "let's": "let us",
      "ma'am": "madam",
      "mayn't": "may not",
      "might've": "might have",
      "mightn't": "might not",
      "mightn't've": "might not have",
      "must've": "must have",
      "mustn't": "must not",
      "mustn't've": "must not have",
      "needn't": "need not",
      "needn't've": "need not have",
      "o'clock": "of the clock",
      "oughtn't": "ought not",
      "oughtn't've": "ought not have",
      "shan't": "shall not",
      "sha'n't": "shall not",
      "shan't've": "shall not have",
      "she'd": "she would",
      "she'd've": "she would have",
      "she'll": "she will",
      "she'll've": "she will have",
      "she's": "she is",
      "should've": "should have",
      "shouldn't": "should not",
      "shouldn't've": "should not have",
      "so've": "so have",
      "so's": "so is",
      "that'd": "that would",
      "that'd've": "that would have",
      "that's": "that is",
      "there'd": "there had",
      "there'd've": "there would have",
      "there's": "there is",
      "they'd": "they would",
      "they'd've": "they would have",
      "they'll": "they will",
      "they'll've": "they will have",
      "they're": "they are",
      "they've": "they have",
      "to've": "to have",
      "wasn't": "was not",
      "we'd": "we had",
      "we'd've": "we would have",
      "we'll": "we will",
      "we'll've": "we will have",
      "we're": "we are",
      "we've": "we have",
      "weren't": "were not",
      "what'll": "what will",
      "what'll've": "what will have",
      "what're": "what are",
      "what's": "what is",
      "what've": "what have",
      "when's": "when is",
      "when've": "when have",
      "where'd": "where did",
      "where's": "where is",
      "where've": "where have",
      "who'll": "who will",
      "who'll've": "who will have",
      "who's": "who is",
      "who've": "who have",
      "why's": "why is",
      "why've": "why have",
      "will've": "will have",
      "won't": "will not",
      "won't've": "will not have",
      "would've": "would have",
      "wouldn't": "would not",
      "wouldn't've": "would not have",
      "y'all": "you all",
      "y'alls": "you alls",
      "y'all'd": "you all would",
      "y'all'd've": "you all would have",
      "y'all're": "you all are",
      "y'all've": "you all have",
      "you'd": "you had",
      "you'd've": "you would have",
      "you'll": "you you will",
      "you'll've": "you you will have",
      "you're": "you are",
      "you've": "you have"
    }


    c_re = re.compile('(%s)' % '|'.join(cList.keys()))

    def expandContractions(text, c_re=c_re):
        def replace(match):
            return cList[match.group(0)]
        return c_re.sub(replace, text)


    def clean_text(df,text_field):
        # taken from 'How to Solve 90% of NLP Problems'
        # remove links
        df[text_field] = df[text_field].str.replace(r"http\S+", "")
        df[text_field] = df[text_field].str.replace(r"http", "")
        # remove @ mentions
        df[text_field] = df[text_field].str.replace(r"@\S+", "")
        #remove hashtags
        df[text_field] = df[text_field].str.replace(r"#\S+", "")
        #remove weird characters
        df[text_field] = df[text_field].str.replace(r"[^A-Za-z0-9(),!?@\'\`\"\_\n\(\)]", " ")
        df[text_field] = df[text_field].str.replace(r"@", "at")
        df[text_field] = df[text_field].str.replace(r"amp", "and")


        df[text_field] = df[text_field].str.lower()
        df[text_field] = df[text_field].apply(lambda x: expandContractions(x))
        df = df.fillna('')
        return df

    tf = clean_text(tf,'text')
    tf = (tf.drop_duplicates(subset='text'))
    tokenizer = RegexpTokenizer(r'\w+')
    tf.loc[:,"tokens"] = tf.loc[:,"text"].apply(tokenizer.tokenize)

    data_words = tf['tokens'][:]


    # Build the bigram and trigram models
    bigram = gensim.models.Phrases(data_words, min_count=5, threshold=5) # higher threshold fewer phrases.
    trigram = gensim.models.Phrases(bigram[data_words], threshold=5)

    # Faster way to get a sentence clubbed as a trigram/bigram
    bigram_mod = gensim.models.phrases.Phraser(bigram)
    trigram_mod = gensim.models.phrases.Phraser(trigram)

    # See trigram example
    print(trigram_mod[bigram_mod[data_words[0:10]]])

    def make_bigrams(texts):
        return [bigram_mod[doc] for doc in texts]

    def make_trigrams(texts):
        return [trigram_mod[bigram_mod[doc]] for doc in texts]

    #tf['tokens'] = trigram_mod[bigram_mod[tf['tokens']]]

    tf['tokens'] = bigram_mod[tf['tokens']]

    tf['processed_text'] = tf['tokens'].apply(' '.join)


    # Import stopwords with scikit-learn
    from sklearn.feature_extraction import text
    stop = text.ENGLISH_STOP_WORDS.union(['amp','via','i_m','it_s'])
    tf['processed_text'] = tf['processed_text'].apply(lambda x: ' '.join([word for word in x.split() if word not in (stop)]))
    tf = (tf.drop_duplicates(subset='processed_text'))

    return tf
