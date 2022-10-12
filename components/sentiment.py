from kfp.components import InputPath, OutputPath

def run_analysis(
  model_name: str,
  input_data_path: InputPath(str),
  output_data_path: OutputPath(),
):
  # imports
  import pandas as pd
  import numpy as np
  from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer

  # read in tweets
  tweets_df = pd.read_pickle(input_data_path)
  print(f"Tweets: {tweets_df.head()}")

  # Create class for data preparation
  class SimpleDataset:
    def __init__(self, tokenized_texts):
      self.tokenized_texts = tokenized_texts
    
    def __len__(self):
      return len(self.tokenized_texts["input_ids"])
    
    def __getitem__(self, idx):
      return {k: v[idx] for k, v in self.tokenized_texts.items()}

  print("Loading tokenizer and model")
  # Load tokenizer and model, create trainer
  tokenizer = AutoTokenizer.from_pretrained(model_name)
  model = AutoModelForSequenceClassification.from_pretrained(model_name)
  trainer = Trainer(model=model)

  print("Tokenizing tweets")
  # Tokenize texts and create prediction data set
  tokenized_texts = tokenizer(list(tweets_df.text), truncation=True, padding=True)
  pred_dataset = SimpleDataset(tokenized_texts)

  print("Running predictions")
  # Run predictions
  predictions = trainer.predict(pred_dataset)

  # Transform predictions to labels
  preds = predictions.predictions.argmax(-1)
  labels = pd.Series(preds).map(model.config.id2label)
  scores = (np.exp(predictions[0])/np.exp(predictions[0]).sum(-1,keepdims=True)).max(1)

  print("Creating dataframe with predictions")
  # Create DataFrame with texts, predictions, labels, and scores
  df = pd.DataFrame(list(zip(list(tweets_df.text),preds,labels,scores)), columns=['text','pred','label','score'])
  analysis = tweets_df.assign(sent=tweets_df.text.map(dict(df.set_index('text').label)), sent_score=tweets_df.text.map(dict(df.set_index('text').score)))
  print(f"Analysis: {analysis.head()}")
  # return analysis
  print("Writing analysis datafram to csv")
  analysis.to_pickle(output_data_path)
