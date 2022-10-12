from kfp.components import InputPath, OutputPath

def get_stock_data(
  input_data_path: InputPath(str),
  output_data_path: OutputPath(),
):
  # imports
  import pandas as pd
  from datetime import datetime, timedelta

  # read in tweets
  tweets_df = pd.read_pickle(input_data_path)
  print(f"Tweets: {tweets_df.head()}")

  # convert timestamps from strings
  tweets_df['timestamp'] = tweets_df['timestamp'].apply(lambda x: pd.Timestamp(x))

  # define function to get stock information
  def get_stock_prices(ticker, tweet_time):
    import yfinance as yf
    # get price at tweet
    price_history = yf.Ticker(ticker).history(
      start=tweet_time.date().strftime("%Y-%m-%d"),
      end=(tweet_time + timedelta(days=1)).date().strftime("%Y-%m-%d")
    )
    # check to use open or close
    price_at_tweet = price_history['Open'].max()
    if tweet_time.hour > 16:
      price_at_tweet = price_history['Close'].max()

    # get price 7 days after
    seven_day_high = 0
    seven_day_low = 0
    # check if we are 7 days out
    if (tweet_time + timedelta(days=7)).date() < datetime.now().date():
      price_history = yf.Ticker(ticker).history(
        start=tweet_time.date().strftime("%Y-%m-%d"),
        end=(tweet_time + timedelta(days=8)).date().strftime("%Y-%m-%d")
      )
      seven_day_high = price_history.High.max()
      seven_day_low = price_history.Low.min()
    
    
    # get price 1 month after
    one_month_high = 0
    one_month_low = 0
    # check if we are 1 month out
    if (tweet_time + timedelta(days=30)).date() < datetime.now().date():
      price_history = yf.Ticker(ticker).history(
        start=tweet_time.date().strftime("%Y-%m-%d"),
        end=(tweet_time + timedelta(days=31)).date().strftime("%Y-%m-%d")
      )
      one_month_high = price_history.High.max()
      one_month_low = price_history.Low.min()

    # get price 6 months after
    six_month_high = 0
    six_month_low = 0
    # check if we are 6 months out
    if (tweet_time + timedelta(days=180)).date() < datetime.now().date():
      price_history = yf.Ticker(ticker).history(
        start=tweet_time.date().strftime("%Y-%m-%d"),
        end=(tweet_time + timedelta(days=181)).date().strftime("%Y-%m-%d")
      )
      six_month_high = price_history.High.max()
      six_month_low = price_history.Low.min()
    
    # get present price
    price_history = yf.Ticker(ticker).history(
      start=datetime.now().strftime("%Y-%m-%d"),
      end=(datetime.now() + timedelta(days=1)).date().strftime("%Y-%m-%d")
    )
    present_price = price_history['Close'].max()

    return {
      f'{ticker}_price_at_tweet': price_at_tweet,
      f'{ticker}_present_price': present_price,
      f'{ticker}_seven_day_high': seven_day_high,
      f'{ticker}_seven_day_low': seven_day_low,
      f'{ticker}_one_month_high': one_month_high,
      f'{ticker}_one_month_low': one_month_low,
      f'{ticker}_six_month_high': six_month_high,
      f'{ticker}_six_month_low': six_month_low,
    }


  # get all symbols to 
  # symbols = [symbol for symbol_list in tweets_df.symbol for symbol in symbol_list]

  # get stock price at tweet time, 7 day min and max, 6 month min and max, present price
  for index, row in tweets_df.iterrows():
    try:
      stock_data = [
        get_stock_prices(symbol.replace('$', ''), row['timestamp'])
        for symbol in row['symbol']
      ]
      tweets_df.at[index, 'stock_data'] = stock_data
    except Exception as e:
      print(f"Error getting price data: {e}")
  
  # write df
  tweets_df.to_pickle(output_data_path)