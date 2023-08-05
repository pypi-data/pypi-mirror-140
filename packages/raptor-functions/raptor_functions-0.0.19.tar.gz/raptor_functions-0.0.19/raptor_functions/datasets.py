import pandas as pd
import subprocess



def load_validated_breath_dataset():


    # s3_url = 's3://raptor-engine/data.csv'
    # filename = './validated_breath_data.csv'
    url = 'https://drive.google.com/file/d/1LUBsw5nIW_VSDGucxeudCrzDy4ntC1gW/view?usp=sharing'
    url='https://drive.google.com/uc?id=' + url.split('/')[-2]


    return pd.read_csv(url, index_col=0)


def get_data(data='validated_breath_data'):


    if data == 'validated_breath_data':

        # s3_url = 's3://raptor-engine/data.csv'
        # filename = './validated_breath_data.csv'
        url = 'https://drive.google.com/file/d/1LUBsw5nIW_VSDGucxeudCrzDy4ntC1gW/view?usp=sharing'
        url='https://drive.google.com/uc?id=' + url.split('/')[-2]


    return pd.read_csv(url, index_col=0)