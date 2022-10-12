from kfp.components import InputPath, OutputPath

def make_pdf(
  screen_name: str,
  input_data_path: InputPath(str),
  output_data_path: OutputPath(),
):
  # imports
  from datetime import datetime, timedelta
  from fpdf import FPDF
  import matplotlib.pyplot as plt
  import pandas as pd

  # read in dataframe
  df = pd.read_pickle(input_data_path)

  # graph stock data
  def graph_stock_data(stock_data, symbol, timestamp, index):
    # plot not resetting inbetween calls, not showing all lines
    symbol = symbol.replace('$', '')
    df_2 = pd.DataFrame([stock_data])
    # get high points
    highs = [
      df_2[f'{symbol}_price_at_tweet'][0],
      df_2[f'{symbol}_seven_day_high'][0],
      df_2[f'{symbol}_one_month_high'][0],
      df_2[f'{symbol}_six_month_high'][0],
    ]
    highs = [i for i in highs if i != 0]
    # get low points
    lows = [
      df_2[f'{symbol}_price_at_tweet'][0],
      df_2[f'{symbol}_seven_day_low'][0],
      df_2[f'{symbol}_one_month_low'][0],
      df_2[f'{symbol}_six_month_low'][0],
    ]
    lows = [i for i in lows if i != 0]
    # get tweet to now
    tweet_to_now = [df_2[f'{symbol}_price_at_tweet'][0], df_2[f'{symbol}_present_price'][0]]
    tweet_to_now_timestamps = [timestamp, datetime.now()]
    # get timestamps
    timestamps = [timestamp]
    if df_2[f'{symbol}_seven_day_high'][0] != 0:
      timestamps.append(timestamp + timedelta(days=7))
    if df_2[f'{symbol}_one_month_high'][0] != 0:
      timestamps.append(timestamp + timedelta(days=31))
    if df_2[f'{symbol}_six_month_low'][0] != 0:
      timestamps.append(timestamp + timedelta(days=181))
    # make plot pf all lines
    plt.plot(timestamps, highs, label = f"{symbol} highs")
    plt.plot(timestamps, lows, label = f"{symbol} lows")
    plt.plot(tweet_to_now_timestamps, tweet_to_now, label = f"{symbol} tweet to now")
    # rotate timestamp x label to not overlap
    plt.xticks(rotation=45)
    # add legend for different lines
    plt.legend()
    # fix label cutoff
    plt.autoscale()
    # save graph file
    plt.savefig(f'graph_{index}_{symbol}.png', bbox_inches="tight")
    # reset
    plt.clf()

  # class for pdf
  class PDF(FPDF):
    def header(self):
      self.set_font('Times', '', 12)
      self.cell(80)
      self.ln(10)
      self.set_text_color(0, 0, 139)
      self.cell(0, 10, f'{screen_name} Report', 1, 0, 'C')
      self.ln(15)

  pdf = PDF()
  pdf.alias_nb_pages()
  pdf.add_page(orientation="")

  # add data to pdf
  for i, row in df.iterrows():
    try:
      symbol = df.at[i, 'symbol']
      timestamp = df.at[i, 'timestamp']
      pdf.set_font('Times', 'b', 12)
      pdf.cell(0, 10, ' '.join(symbol), 0, 1, 'C')
      pdf.set_font('Times', '', 12)
      pdf.cell(0, 10, str(timestamp), 0, 1, 'C', link=f"https://www.twitter.com/jimcramer/status/{df.at[i, 'id']}")
      pdf.multi_cell(0, 5, df.at[i, 'text'].encode('latin-1', 'replace').decode('latin-1'), align='C')
      pdf.ln(5)
      pdf.cell(0, 10, df.at[i, 'sent'] + ", " + str(df.at[i, 'sent_score']), 0, 1, 'C')
      pdf.set_font('Times', 'b', 12)
      pdf.cell(0, 10, 'Price Chart', 0, 1, 'C')
      # make graphs
      for ind, stock_data in enumerate(df.at[i, 'stock_data']):
        graph_stock_data(stock_data, df.at[i, 'symbol'][ind], timestamp, i)
        pdf.image(f'graph_{i}_{symbol}.png', x=55, w=100)
      pdf.add_page(orientation="")
    except Exception as e:
      print(f"error constructing page: {e}")
      pdf.add_page(orientation="")
      pass
  
  pdf.output(output_data_path, 'F')

