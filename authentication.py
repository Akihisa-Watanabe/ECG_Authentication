import numpy as np
import pandas as pd
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw


def get_DTW(frame:pd.DataFrame ,template:np.ndarray,feature:str)->float:
    DTW=[]
    sample = frame[frame.keys()[0]][feature]
    for key in frame.keys():
        y = frame[key][feature]
        distance, path = fastdtw(template, y, dist=euclidean)
        DTW.append(distance)

    DTW_mean = sum(DTW)/len(DTW)
    if(len(sample)>len(template)):
        return round((1-DTW_mean/len(y))*100,2)
    else:
        return round((1-DTW_mean/len(template))*100,2)
