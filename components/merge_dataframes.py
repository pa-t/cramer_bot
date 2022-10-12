from kfp.components import InputPath, OutputPath

def merge_dataframes(
  input_data_path: InputPath(str),
  input_data_path_two: InputPath(str),
  output_data_path: OutputPath(),
):
  # imports
  import pandas as pd

  # read from pickles
  df = pd.read_pickle(input_data_path)
  df2 = pd.read_pickle(input_data_path_two)

  # fix timestamps from analysis
  df['timestamp'] = df['timestamp'].apply(lambda x: pd.Timestamp(x))

  # merge
  merged_df = pd.merge(df, df2, on=['id', 'timestamp', 'text'])
  merged_df = merged_df.drop(columns=['symbol_y'])
  merged_df = merged_df.rename(columns={"symbol_x": "symbol"})

  # write to file
  merged_df.to_pickle(output_data_path)