import kfp
from kfp import dsl
from kfp.components import func_to_container_op
from decouple import config

from components.get_symbols import download_symbols
from components.get_tweets import download_tweets
from components.sentiment import run_analysis
from components.get_stock_price_data import get_stock_data
from components.merge_dataframes import merge_dataframes
from components.make_pdf import make_pdf


# create function to container component
download_symbols_op = func_to_container_op(
    download_symbols,
    base_image="python:3.9.2",
    packages_to_install=["pandas==1.4.3", "requests==2.28."],
)

download_tweets_op = func_to_container_op(
  download_tweets,
  base_image="python:3.9.2",
  packages_to_install=["pandas==1.4.3", "python-decouple==3.6", "python-twitter==3.5"],
)

run_analysis_op = func_to_container_op(
  run_analysis,
  base_image="python:3.9.2",
  packages_to_install=["pandas==1.4.3", "numpy==1.23.2", "transformers==4.21.1", "torch==1.12.1"],
)

get_stock_data_op = func_to_container_op(
    get_stock_data,
    base_image="python:3.9.2",
    packages_to_install=["pandas==1.4.3", "yfinance==0.1.74"],
)

merge_dataframes_op = func_to_container_op(
    merge_dataframes,
    base_image="python:3.9.2",
    packages_to_install=["pandas==1.4.3"],
)

make_pdf_op = func_to_container_op(
    make_pdf,
    base_image="python:3.9.2",
    packages_to_install=["pandas==1.4.3", "fpdf==1.7.2", "matplotlib==3.6.0"],
)

@dsl.pipeline(
   name='tweet_pipeline',
   description='test pipeline to download tweets as dfs'
)
def tweet_pipeline():
  # set values
  SYMBOLS_URL = 'https://api.nasdaq.com/api/screener/stocks?tableonly=true&download=true'
  MODEL_NAME = 'siebert/sentiment-roberta-large-english'
  config_dict: dict = {
    'screen_name': 'jimcramer',
    'API_KEY': config('API_KEY'),
    'API_KEY_SECRET': config('API_KEY_SECRET'),
    'ACCESS_TOKEN': config('ACCESS_TOKEN'),
    'ACCESS_TOKEN_SECRET': config('ACCESS_TOKEN_SECRET'),
  }
  # construct pipeline
  download_symbols_task = download_symbols_op(SYMBOLS_URL)
  download_tweets_task = download_tweets_op(config_dict, download_symbols_task.output).after(download_symbols_task)
  run_analysis_task = run_analysis_op(MODEL_NAME, download_tweets_task.output).after(download_tweets_task)
  get_stock_data_task = get_stock_data_op(download_tweets_task.output).after(download_tweets_task)
  merge_df_task = merge_dataframes_op(run_analysis_task.output, get_stock_data_task.output).after(run_analysis_task, get_stock_data_task)
  make_pdf_op(config_dict['screen_name'], merge_df_task.output).after(merge_df_task)


client = kfp.Client(host='http://localhost:3000')
pipeline_run = client.create_run_from_pipeline_func(
  tweet_pipeline,
  arguments={},
  experiment_name='tweet_pipeline'
)

print(f"Run {pipeline_run.run_id} started...")
client.wait_for_run_completion(pipeline_run.run_id, timeout=3600)
complete_run = client.get_run(pipeline_run.run_id)
print(f"Run {pipeline_run.run_id} state: {complete_run.run.status}")


# client.runs.terminate_run('c264ecf2-637d-4a71-b251-0c1e218c5fd3')