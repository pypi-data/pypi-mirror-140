
from sklearn.metrics import accuracy_score, recall_score, precision_score
import matplotlib.pyplot as plt



def eval_metrics(actual, pred):
    """evaluates model performance

    Args:
        actual (numpy array): true labels
        pred (numpy array): predicited labels

    Returns:
        tuple: returns a tuple of accuracy, sensitivity, specificity, precision
    """
    
    accuracy = accuracy_score(actual, pred)
    sensitivity = recall_score(actual, pred)
    specificity = recall_score(actual, pred, pos_label=0)
    precision = precision_score(actual, pred)

    return accuracy, sensitivity, specificity, precision






def make_plots():
  plot_confusion_matrix(clf, X_test, y_test)  
  skplt.metrics.plot_roc_curve(y_true, y_probas)
  plt.show()




cmap = plt.cm.Blues

def confusion_matrix_plot(model,X_test,X_train, y_train, y_test):
  # 
  y_pred = model.predict(X_test)
  print("Accuracy: %.2f%%" % (accuracy_score(y_test, y_pred) * 100))
  print("Recall: %.2f%%" % (recall_score(y_test, y_pred, average="binary", pos_label='Covid') * 100.0))
  print("Precision: %.2f%%" % (precision_score(y_test, y_pred, average="binary", pos_label='Covid') * 100.0))

  plot_confusion_matrix(model, X_test, y_test,
                            display_labels=['Covid', 'Non-Covid'], cmap=cmap)
  plt.savefig('confusion_matrix.eps')

  fea_imp = pd.DataFrame({'imp': model.feature_importances_, 'col': X_train.columns})
  fea_imp = fea_imp.sort_values(['imp', 'col'], ascending=[True, False]).iloc[-30:]
  fea_imp.plot(kind='barh', x='col', y='imp', figsize=(10, 7), legend=None)
  plt.title('XGBoost - Feature Importance')
  plt.ylabel('Features')
  plt.xlabel('Importance')
  plt.savefig('feature_importance.eps')

  disp = plot_precision_recall_curve(model, X_test, y_test)
  disp.ax_.set_title('Binary class Precision-Recall curve')
  plt.savefig('precision_recall_curve.eps')




def model_explanation(model,X,X_test):
  # 
  explainer = shap.TreeExplainer(model)
  shap_values = explainer.shap_values(X_test) 
  # shap.initjs()
  # 
  # Summary plot
  shap.summary_plot(shap_values, X_test)
  # 
  for name in X.columns:
    shap.dependence_plot(name, shap_values, X_test, display_features = X)


def random_prediction(X_test,y_test,model):
  explainer = shap.TreeExplainer(model)
  shap_values = explainer(X_test)
  i = random.randint(0, len(X_test))
  shap.plots.waterfall(shap_values[i])
  print('Category: ' + str(y_test.values[i][0]))
  print('Prediction: ' + str(model.predict(X_test.iloc[[i]])[0]))
  print('Prediction Probability: ' + str(model.predict_proba(X_test.iloc[[i]])[0]))









def calculate_prediction_and_probability(list_files, df_list, x_columns, model):
  # 
  prediction = []
  probability = []
  for i in range(len(list_files)):
    df_temp = df_list[i]
    df_temp = df_temp[x_columns]
    prediction.append([])
    probability.append([])
    for j in range(df_temp.count()[0]):
      input_data_sample = df_temp.iloc[[j]]
      prediction_temp =  int(model.predict(input_data_sample))
      prediction[i].append(prediction_temp)
      probability_temp =  model.predict_proba(input_data_sample)
      probability_temp = float(probability_temp[0][1])
      probability[i].append(probability_temp)
  
  return prediction, probability

def calculate_mean_probability(list_files, probability):
  # 
  mean_probability = []
  std_probability = []
  for i in range(len(list_files)):
    probability_array = np.array(probability[i])
    # 
    mean_probability_temp = np.mean(probability_array)
    mean_probability.append(mean_probability_temp)
    # 
    std_probability_temp = np.std(probability_array)
    std_probability.append(std_probability_temp)
  # 
  return mean_probability, std_probability

def plot_histogram_probabilities(mean_probability):
  # 
  plt.hist(mean_probability, 30) 
  plt.title("histogram") 
  plt.show()

def plot_probability_over_time(date_time_list,mean_probability):
  # 
  plt.style.use('seaborn-colorblind')
  plt.scatter(date_time_list,mean_probability)
  degrees = 70
  plt.axhline(y=0.5, color='r', linestyle='--', linewidth = '1')
  plt.xticks(rotation=degrees)
  plt.xlabel('Time')
  plt.ylabel('Probability of Covid')
  plt.ylim([0,1])
  plt.title('Probability of COVID vs. Time')
  time_now = str(datetime.now())
  plt.savefig('Plot'+time_now +'.png', dpi = 200, bbox_inches='tight')






def plot_algorithm_performance(names, results, metrics, savefig=False, ylim=False):

    fig = plt.figure(figsize=(16,6))
    fig.suptitle('Comparison of algorithm performance')
    ax = fig.add_subplot(111)
    plt.boxplot(results)
    ax.set_xticklabels(names)
    plt.ylabel(metrics)
    plt.xlabel('models')

    if savefig:
        fig.savefig(f'{metrics}.jpeg', transparent = False)
    
    if ylim:
        plt.ylim([0,1])
        
    plt.show()



def run_models_cv(models, X_train, y_train, scoring='accuracy'):
    results = []
    names = []

    if scoring == 'specificity':
        scoring = make_scorer(recall_score, pos_label=0)
    else:
        for name, model in models:
            kfold = model_selection.KFold(n_splits=10, random_state=seed, shuffle=True)
            cv_results = model_selection.cross_val_score(model, X_train, y_train, cv=kfold, scoring=scoring)
            results.append(cv_results)
            names.append(name)
      
    return names, results, scoring



