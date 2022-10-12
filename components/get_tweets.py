from kfp.components import InputPath, OutputPath

def download_tweets(
  config_dict: dict,
  input_data_path: InputPath(str),
  data_path: OutputPath()
):
  import pandas as pd
  import twitter
  # read sumbols from df pickle
  symbols_df = pd.read_pickle(input_data_path)
  symbols = list(symbols_df.symbol)
  print(f"Symbols: {symbols}")
  # create twitter api
  api = twitter.Api(
    consumer_key=config_dict['API_KEY'],
    consumer_secret=config_dict['API_KEY_SECRET'],
    access_token_key=config_dict['ACCESS_TOKEN'],
    access_token_secret=config_dict['ACCESS_TOKEN_SECRET']
  )
  print("twitter API set up")
  timeline = []
  tweets = api.GetUserTimeline(screen_name=config_dict['screen_name'], count=200)
  earliest_tweet = min(tweets, key=lambda x: x.id).id
  while True:
    for tweet in tweets:
      # check for any mention of a symbol, add tweet to list with list of matching symbols
      # basic check with a lot of false positives/misses
      matched_symbols = [word for word in tweet.text.split() if word in symbols or word.split("$")[-1] in symbols]
      if matched_symbols:
        timeline.append({'id': tweet.id, 'timestamp': tweet.created_at, 'text': tweet.text, 'symbol': list(set(matched_symbols))})
    
    tweets = api.GetUserTimeline(
      screen_name=config_dict['screen_name'], max_id=earliest_tweet, count=200,
    )
    new_earliest = min(tweets, key=lambda x: x.id).id
    if not tweets or new_earliest == earliest_tweet:
      break
    else:
      earliest_tweet = new_earliest
  print(f"Found {len(timeline)} tweets")
  print(f"Tweets: {timeline}")
  tweets_df = pd.DataFrame(timeline)
  tweets_df.to_pickle(data_path)