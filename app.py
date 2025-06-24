import os
from flask import Flask, request, render_template, jsonify
from twitter_client import TwitterClientV2

app = Flask(__name__)
api = TwitterClientV2('')  # Initial dummy query

# Helper to safely convert query params to boolean
def strtobool(v):
    return str(v).lower() in ["yes", "true", "t", "1"]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tweets')
def tweets():
    # Get query parameters safely
    retweets_only = request.args.get('retweets_only', 'false')
    with_sentiment = request.args.get('with_sentiment', 'false')
    query = request.args.get('query', '')

    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400

    # Apply parameters to TwitterClient
    api.set_retweet_checking(strtobool(retweets_only))
    api.set_with_sentiment(strtobool(with_sentiment))
    api.set_query(query)

    # Get tweets
    tweets = api.get_tweets()

    return jsonify({'data': tweets, 'count': len(tweets)})

if __name__ == '__main__':
    app.run(debug=True)
