import random
import numpy as np
import pandas as pd


def aslist(x):
    if isinstance(x, list):
        return x
    else:
        return [x]


def specificity(actual, pred, pos_label=0):
    return recall_score(actual, pred, pos_label=pos_label)


def get_stages(stages='pause', N_STAGES=None, STAGES=None):

    if stages== 'pause':
        return aslist('pause')
    elif stages == 'all':
        return aslist(STAGES)
    elif stages=='random':
        return np.random.choice(STAGES, N_STAGES, False).tolist()
    else:
        return stages


def get_sensor_cols(sensors='12', N_SENSORS=None, SENSORS_ALL=None):
    if sensors=='24':
        return SENSORS_ALL
    elif sensors=='12':
        return SENSORS_ALL[:12]
    elif sensors=='12r':
        return SENSORS_ALL[-12:]
    elif sensors=='random':
        return np.random.choice(SENSORS_ALL, N_SENSORS, False).tolist()
    else:
        return sensors

def get_train_features(df, sensor='12', stage='pause', use_average = False):

    SENSORS_ALL = df.columns.tolist()[3:27]
    STAGES = df['measurement_stage'].unique().tolist()
    TARGET_COL = 'result'

    N_SENSORS = random.randint(1,len(SENSORS_ALL))
    N_STAGES = random.randint(1,len(STAGES))

    stages_to_use = get_stages(stage, N_STAGES, STAGES)
    col_to_use = get_sensor_cols(sensor, N_SENSORS, SENSORS_ALL)


    if use_average:
        data = df.groupby(['measurement_stage', 'unique_id', 'result']).mean().reset_index()[col_to_use+[TARGET_COL]]
        return data, col_to_use, stages_to_use

    else:
        data = df.loc[df['measurement_stage'].isin(stages_to_use)][col_to_use+[TARGET_COL]]
        return data, col_to_use, stages_to_use



          
