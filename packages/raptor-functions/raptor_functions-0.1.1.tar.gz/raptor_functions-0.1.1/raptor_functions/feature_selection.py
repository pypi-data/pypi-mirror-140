import random
import numpy as np
import pandas as pd


# all sensors in experiment
SENSORS_FEATURES = ['sensor_1','sensor_2','sensor_3','sensor_4','sensor_5',
 'sensor_6', 'sensor_7', 'sensor_8', 'sensor_9', 'sensor_10', 'sensor_11', 'sensor_12', 'sensor_13',
 'sensor_14', 'sensor_15', 'sensor_16', 'sensor_17', 'sensor_18', 'sensor_19', 'sensor_20', 'sensor_21', 'sensor_22', 'sensor_23', 'sensor_24']

# all stages in experiment
STAGES = ['baseline', 'absorb', 'pause', 'desorb', 'flush']

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



def get_train_features(df, sensor='12', stage='pause', use_average = False):
    
    """Selects the features to be used for model training

    Args:
        df (pandas dataframe): dataframe of cyclic sensor data
        sensor (str, optional): Can take any of ('sensor_1', 'sensor_2', 'sensor_3'.....'sensor_24') as a str or combination as a list. 
                                 Can also take str '24' for all sensors, '12' for 1st 12 sensors, '12r' for last 12 sensors and 'random' for random sensor or sensors. Defaults to '12'.        stage (str, optional): _description_. Defaults to 'pause'.
        stage (str or list, optional): Can take any of ('baseline', 'absorb', 'pause', 'desorb', 'flush') as a str or combination as a list. 
                                        Can also take str 'all' for all stages and 'random' for random stage or stages. Defaults to 'pause'.
        use_average (bool, optional): if True, uses average of stages selected. Defaults to False.


    Returns:
        data(pandas dataframe): _description_
    """

    target_col='result'

    N_SENSORS = random.randint(1,len(SENSORS_FEATURES))
    N_STAGES = random.randint(1,len(STAGES))

    stages_to_use = get_stages(stage, N_STAGES, STAGES)
    sensors_to_use = get_sensors(sensor, N_SENSORS, SENSORS_FEATURES)


    if use_average:
        data = df.groupby(['measurement_stage', 'result', 'exp_unique_id']).mean().loc[stages_to_use].reset_index()[sensors_to_use+[target_col]]
        return data, sensors_to_use, stages_to_use

    else:
        data = df.loc[df['measurement_stage'].isin(stages_to_use)][sensors_to_use+[target_col]]
        return data, sensors_to_use, stages_to_use



          
