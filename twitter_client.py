import os
from dotenv import load_dotenv
import tweepy
from textblob import TextBlob
import re

class TwitterClientV2:
    def __init__(self, query='', retweets_only=False, with_sentiment=False):
        load_dotenv()
        bearer_token = os.getenv('TWITTER_BEARER_TOKEN')

        if not bearer_token:
            raise Exception("Bearer token not found in environment variables")

        self.client = tweepy.Client(bearer_token=bearer_token)
        self.query = query
        self.retweets_only = retweets_only
        self.with_sentiment = with_sentiment
        self.tweet_count_max = 100

    def set_query(self, query=''):
        self.query = query

    def set_retweet_checking(self, retweets_only=False):
        self.retweets_only = retweets_only

    def set_with_sentiment(self, with_sentiment=False):
        self.with_sentiment = with_sentiment

    def clean_tweet(self, tweet):
        return ' '.join(re.sub(r"(@[A-Za-z0-9_]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    def get_tweet_sentiment(self, tweet):
        analysis = TextBlob(self.clean_tweet(tweet))
        if analysis.sentiment.polarity > 0:
            return 'positive'
        elif analysis.sentiment.polarity == 0:
            return 'neutral'
        else:
            return 'negative'

    def get_tweets(self):
        tweets = []
        query = self.query
        if self.retweets_only:
            query += " is:retweet"
        else:
            query += " -is:retweet"

        try:
            # Search recent tweets (last 7 days max)
            response = self.client.search_recent_tweets(
                query=query,
                tweet_fields=['author_id','created_at','public_metrics','lang'],
                max_results=min(self.tweet_count_max, 100)  # max 100 per request
            )

            if not response.data:
                return tweets

            for tweet in response.data:
                # Filter English tweets only (optional)
                if tweet.lang != 'en':
                    continue

                parsed_tweet = {
                    'text': tweet.text,
                    'author_id': tweet.author_id,
                    'retweet_count': tweet.public_metrics.get('retweet_count', 0)
                }

                if self.with_sentiment:
                    parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.text)
                else:
                    parsed_tweet['sentiment'] = 'unavailable'

                tweets.append(parsed_tweet)

            return tweets

        except Exception as e:
            print("Error fetching tweets:", str(e))
            return []
