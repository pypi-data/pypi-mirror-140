# Importing the Packages:
import optuna
import argparse
import joblib
import pandas as pd
from sklearn import linear_model
from sklearn import datasets
from sklearn import model_selection
import sklearn.ensemble as ensemble
import mlflow
import random
from pycaret.classification import *
# import sktime
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, recall_score, precision_score
from sklearn.metrics import recall_score
# from raptor_functions.feature_selection import get_train_features
from sklearn.pipeline import Pipeline
# from sktime.classification.compose import ColumnEnsembleClassifier
# from sktime.classification.interval_based import TimeSeriesForestClassifier
# from sktime.classification.dictionary_based import BOSSEnsemble
# # from sktime.classification.shapelet_based import MrSEQLClassifier
# from sktime.transformations.panel.compose import ColumnConcatenator
from sklearn.model_selection import train_test_split
# from sktime.datatypes._panel._convert import (
#     from_multi_index_to_nested,
#     from_nested_to_multi_index,
# )

# from raptor_functions.raptor_data import load_validated_breath_dataset

# df = load_validated_breath_dataset()



SENSORS_FEATURES = ['sensor_1','sensor_2','sensor_3','sensor_4','sensor_5',
 'sensor_6', 'sensor_7', 'sensor_8', 'sensor_9', 'sensor_10', 'sensor_11', 'sensor_12', 'sensor_13',
 'sensor_14', 'sensor_15', 'sensor_16', 'sensor_17', 'sensor_18', 'sensor_19', 'sensor_20', 'sensor_21', 'sensor_22', 'sensor_23', 'sensor_24']

STAGES = ['baseline', 'absorb', 'pause', 'desorb', 'flush']
TARGET_COL = 'result'



def aslist(x):
    """Checks and ensures variable is a list

    Args:
        x (str or list): 

    Returns:
        list: 
    """

    if isinstance(x, list):
        return x
    else:
        return [x]





def get_stages(stages='pause', N_STAGES=None):
    """get the stages of experiment to be used for model training

    Args:
        stages (str or list, optional): Can take any of ('baseline', 'absorb', 'pause', 'desorb', 'flush') as a str or combination as a list. 
                                        Can also take str 'all' for all stages and 'random' for random stage or stages. Defaults to 'pause'.
        N_STAGES (int, optional): if 'random' is chosen for stages, the number of stages to use. Defaults to None.

    Returns:
        list: a list of stages to be used for training
    """

    if stages== 'pause':
        return aslist('pause')
    elif stages == 'all':
        return aslist(STAGES)
    elif stages=='random':
        return np.random.choice(STAGES, N_STAGES, False).tolist()
    else:
        return stages




def get_sensors(sensors='12', N_SENSORS=None):
    """_summary_

    Args:
        sensors (str, optional): Can take any of ('sensor_1', 'sensor_2', 'sensor_3'.....'sensor_24') as a str or combination as a list. 
                                        Can also take str '24' for all sensors, '12' for 1st 12 sensors, '12r' for last 12 sensors and 'random' for random sensor or sensors. Defaults to '12'.
        N_SENSORS (_type_, optional): if 'random' is chosen for sensors, the number of sensors to use. Defaults to None.

    Returns:
        list: a list of sensors to be used for training
    """

    if sensors=='24':
        return SENSORS_FEATURES
    elif sensors=='12':
        return SENSORS_FEATURES[:12]
    elif sensors=='12r':
        return SENSORS_FEATURES[-12:]
    elif sensors=='random':
        return np.random.choice(SENSORS_FEATURES, N_SENSORS, False).tolist()
    else:
        return sensors



def specificity(actual, pred, pos_label=0):
    return recall_score(actual, pred, pos_label=pos_label)


def objective(trial, df, stage, sensor, use_average, model_mode, suggest):

    # mlflow.set_experiment('raptor_experiment')

    # with mlflow.start_run():
        if suggest:
            stage = trial.suggest_categorical("stages", ["pause", "all", 'random'])
            sensor = trial.suggest_categorical("sensor", ["24", "12", '12r','random'])
            use_average = trial.suggest_categorical("use_average", [True, False])
            model_mode = trial.suggest_categorical("model_mode", ["random", "compare"])


        data, sensors_to_use, stages_to_use = get_train_features(df, sensor=sensor, stage=stage, use_average=use_average)


        clf = setup(data, target = 'result', silent=True, log_experiment=True, log_plots=True, experiment_name='raptor', preprocess=False)
        
        add_metric('specificity', 'Specificity', specificity)
        remove_metric('MCC')
        remove_metric('Kappa')


        if model_mode == 'random':

            MODELS = models().index.tolist()
            model_name = trial.suggest_categorical("model", MODELS)
            model = create_model(model_name)
            metrics = pull().sort_values(by=['Accuracy', 'Recall']).loc['Mean']
            plot_model(model, plot = 'auc', save=True)
            plot_model(model, plot = 'confusion_matrix', save=True)



        else:

            model = compare_models()
            model_name = pull().sort_values(by=['Accuracy', 'Recall', 'Specificity'], ascending=False).iloc[0][0]
            metrics = pull().sort_values(by=['Accuracy', 'Recall']).iloc[0][1:-1]
            plot_model(model, plot = 'auc', save=True)
            plot_model(model, plot = 'confusion_matrix', save=True)


            # plot_model(best_model, plot = 'feature')


        
        print(mlflow.get_artifact_uri())
        print(mlflow.get_tracking_uri())

        mlflow.log_metrics(metrics)

        mlflow.set_tag('sensor_cols', sensors_to_use)
        mlflow.set_tag('stage', stages_to_use)
        mlflow.set_tag('model_name', model_name)
        mlflow.set_tag('use_average', use_average)
        mlflow.set_tag('model_mode', model_mode)
        mlflow.set_tag('suggest', suggest)

        mlflow.log_artifact('AUC.png')#, artifact_path=None)

        # mlflow.log_model(model, "model")
        
        # return mlflow.get_artifact_uri(), mlflow.get_tracking_uri()



def train_experiments(df, study_name='raptor', direction='maximize', stage='pause', sensor='12', use_average=False, model_mode='random', n_trials=5, suggest=False):
    """trains several models during different trials and logs them. Experiemnt can be tracked on "http://ec2-3-10-175-206.eu-west-2.compute.amazonaws.com:5000/"


    Args:
        df (pandas dataframe): dataframe of cyclic sensor data to be used for training
        study_name (str, optional): optuna study name to use. Defaults to 'raptor'.
        direction (str, optional): dirtection of objective. Defaults to 'maximize'.
        stage (str or list, optional): Can take any of ('baseline', 'absorb', 'pause', 'desorb', 'flush') as a str or combination as a list. 
                                        Can also take str 'all' for all stages and 'random' for random stage or stages. Defaults to 'pause'.        sensor (str, optional): _description_. Defaults to '12'.
        use_average (bool, optional): if True, uses average of stages selected. Defaults to False.
        model_mode (str, optional): _description_. Defaults to 'random'.
        n_trials (int, optional): number of times to run experiments. Defaults to 5.
        suggest (bool, optional): if True, suggest features, stage, model mode to use for training. Defaults to False.
    """    

    mlflow.set_tracking_uri(
    # "http://ec2-13-40-214-238.eu-west-2.compute.amazonaws.com:5000/"
    # "http://ec2-13-40-86-186.eu-west-2.compute.amazonaws.com:5000/"
    "http://ec2-3-10-175-206.eu-west-2.compute.amazonaws.com:5000/"
    )
    # Initialize client
    # client = MlflowClient()

    # print(mlflow.get_artifact_uri())
    # print(mlflow.get_tracking_uri())

    study = optuna.create_study(study_name=study_name, direction=direction)
    study.optimize(lambda trial: objective(trial, df, stage, sensor, use_average, model_mode, suggest), n_trials=n_trials)

    # return mlflow.get_artifact_uri(), mlflow.get_tracking_uri()
        


# if __name__ == '__main__':

#     args = argparse.ArgumentParser()


#     # stage = trial.suggest_categorical("stages", ["pause", "all", 'random'])
#     # sensor = trial.suggest_categorical("sensor", ["24", "12", '12r','random'])
#     # use_average = trial.suggest_categorical("use_average", [True, False])
#     # model_mode = trial.suggest_categorical("model_mode", ["random", "compare"])

#     # default_config_path = os.path.join("config", "params.yaml")
#     args.add_argument("--stage", default='pause')
#     args.add_argument("--sensor", default='12')

#     args.add_argument("--use-average", default=True)
#     args.add_argument("--model-mode", default='random')
#     args.add_argument("--suggest", default=False)
#     args.add_argument("--n_trials", default=5)


#     parsed_args = args.parse_args()

#     stage = parsed_args.stage
#     sensor = parsed_args.sensor
#     use_average = parsed_args.use_average
#     model_mode = parsed_args.model_mode
#     suggest = parsed_args.suggest
#     n_trials = int(parsed_args.n_trials)


    # study = optuna.create_study(study_name='raptor', direction="maximize")
    # study.optimize(lambda trial: objective(trial, stage, sensor, use_average, model_mode, suggest), n_trials=n_trials)
