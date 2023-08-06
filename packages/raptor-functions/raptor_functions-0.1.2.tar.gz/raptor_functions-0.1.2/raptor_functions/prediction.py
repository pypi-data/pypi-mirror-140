







def load_ml_model(path_to_model):
  model = pickle.load(open(path_to_model, "rb"))
  return model

def random_sample(df_list,x_columns):
  i = random.randint(0, len(df_list))
  df_temp = df_list[i]
  df_temp = df_temp[x_columns]
  # df_temp = df_temp.iloc[:,[1,2,3,4,5,6,7,8,9,10,11,12]]
  j = random.randint(0, len(df_temp.count()))
  input_data_sample = df_temp.iloc[[j]]
  print(input_data_sample)
  # 
  x = input_data_sample.columns.tolist()
  y = input_data_sample.iloc[0].values.tolist()
  # 
  plt.bar(x, y)
  fig = plt.gcf()
  fig.autofmt_xdate()
  # 
  return input_data_sample

def sample_prediction(input_data_sample, model):
  # 
  print('Prediction: ' + str(model.predict(input_data_sample)))
  print('Prediction Probability: ' + str(model.predict_proba(input_data_sample)))