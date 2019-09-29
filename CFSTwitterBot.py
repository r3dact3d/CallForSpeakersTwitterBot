import tweepy
import os
import boto3

### Global Vars
techWords = ['redhat', 'red hat', 'kubernetes', 'ansible', 'tech', 'hacker', 'opensource', 'data science', 'pipeline', 'sysops', 'devops', 'automation']
query = '"call for speakers" OR "submit your talk" -filter:retweets'

# Set up OAuth and integrate with API
accessToken = os.getenv("ACCESS_TOKEN")
accessTokenSecret = os.getenv("ACCESS_TOKEN_SECRET")
consumerKey = os.getenv("CONSUMER_KEY")
consumerSecret = os.getenv("CONSUMER_SECRET")
oauthParams = [accessToken, accessTokenSecret, consumerKey, consumerSecret]

ssm = boto3.client('ssm')
result = ssm.get_parameters(Names=oauthParams, WithDecryption=True)

if result['InvalidParameters']:
    raise RuntimeError('Could not find OAuth params containing Twitter API Keys: {}'.format(oauthParams))
param_lookup = {param['Name']: param['Value'] for param in result['Parameters']}   

auth = tweepy.OAuthHandler(param_lookup[consumerKey], param_lookup[consumerSecret])
auth.set_access_token(param_lookup[accessToken], param_lookup[accessTokenSecret])
api = tweepy.API(auth)

def findTweet(techWords, query, api):
#    for tweet in tweepy.Cursor(api.search, q=query, lang='en', geocode='32.7078750,-96.9209130,100km').items(10):
    for tweet in tweepy.Cursor(api.search, q=query, lang='en', tweet_mode='extended').items(10):
        try:
            text = tweet.retweeted_status.full_text.lower()
        except:
            text = tweet.full_text.lower()
        for word in techWords:
            if word in text:
                if not tweet.retweeted:
                    try:
                        tweet.retweet()
                        print("\tRetweeted" + text)
                    except tweepy.TweepError as e:
                        print("\tAlready Retweeted" + text)

def lambda_handler(event, context):
    findTweet(techWords, query, api)

