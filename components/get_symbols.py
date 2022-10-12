from kfp.components import InputPath, OutputPath


def download_symbols(data_url, data_path: OutputPath()):
  import requests
  import json
  import pandas as pd
  # spoof browser
  headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"
  }
  r = requests.get(data_url, headers=headers)
  if r.status_code == 200:
    d = json.loads(r.text)
    df = pd.DataFrame(d['data']['rows'])
    print(f"Found {len(list(df.symbol))} symbols")
    print(f"Symbols {list(df.symbol)}")
    df.to_pickle(data_path)
  else:
    df = pd.DataFrame({'symbol': 'none found'})
    df.to_pickle(data_path)