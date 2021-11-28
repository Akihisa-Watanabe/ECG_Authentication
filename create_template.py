from os import write
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import csv

def create_template(df:pd.DataFrame,feature:str) ->np.ndarray :
    '''
    df:データフレーム
    feature: テンプレートを作る特徴量の名称("QRS_Signal","MFCC","ACC")
    '''
    N =len(df.keys())
    M= len(df[1][feature])#df内のデータは全部同じ長さ
    data =np.zeros((N,M))
    i=0
    #--線形伸縮--
    for key in df.keys():
        data[i,:] = df[key][feature]
        i+=1
    return data.mean(axis=0,dtype = "float64")
