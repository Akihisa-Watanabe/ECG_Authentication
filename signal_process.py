import numpy as np
import pandas as pd
import neurokit2 as nk
import librosa
import statsmodels.api as sm
import json
import matplotlib.pyplot as plt



def preprocessing(ecg, fs, pipline_method="engzeemod2012", graph_show=False):
    #---Signal Filtering and Peak Point Detection ---
    signals, info = nk.ecg_process(ecg, sampling_rate=fs,method=pipline_method) #‘neurokit’ (default), ‘biosppy’, ‘pantompkins1985’, ‘hamilton2002’, ‘elgendi2010’, ‘engzeemod2012’.
    if graph_show==True:
        plot = nk.ecg_plot(signals[:3000], sampling_rate=fs)
        plt.show()

    Rpeaks = info["ECG_R_Peaks"]
    cleaned_ecg = signals["ECG_Clean"]
    return cleaned_ecg, Rpeaks

def get_segmentation(ecg,Rpeaks,fs, graph_show=False):
    #Signal Segmentation
    epochs = nk.ecg_segment(ecg, rpeaks=Rpeaks, sampling_rate=fs, show=graph_show)
    if graph_show==True:
        plt.show()
    return epochs
    
def feature_extraction(user_id,segment_data,fs,QRS_window_size = 0.2,ACCwindow_size=0.4,N_MFCC=20,save=True):
    """
    QRS_window_size: R-Peakを中心とした矩形の窓の大きさ[s].セグメントデータからQRS波を抽出するために使用．P,T波を含めないサイズに指定．
    ACCwindow_size: R-Peakを中心とした矩形の窓の大きさ[s].セグメントデータからMFCCとACCを求める際に使用．P,T波を含めたサイズに指定．

    return
    """
    if (ACCwindow_size < QRS_window_size):
        print("Warning: ACCwindow_size is smaller than QRS_window_size.")
        return 0
    
    sample_segment = segment_data["1"]["Signal"][(segment_data["1"]["Signal"].keys() < ACCwindow_size)& (segment_data["1"]["Signal"].keys() > -ACCwindow_size)]
    lags  = round(len(sample_segment)/2) #自己相関のラグ数
    Features = {str(i):1.0 for i in range(1,len(segment_data))}

    for key in segment_data.keys():
        qrs = np.array(segment_data[key]["Signal"][(segment_data[key]["Signal"].keys() < QRS_window_size)& (segment_data[key]["Signal"].keys() > -QRS_window_size)]) 
        y = np.array(segment_data[key]["Signal"][(segment_data[key]["Signal"].keys() < ACCwindow_size)& (segment_data[key]["Signal"].keys() > -ACCwindow_size)])

        if not np.isfinite(y).all():
            continue

        mfcc = np.squeeze(librosa.feature.mfcc(y=y, sr=fs,n_mfcc=N_MFCC,lifter=0,n_fft=128,n_mels=60))
        acc = np.squeeze(sm.tsa.stattools.acf(y,nlags=lags,fft=False))
        feature = {"User":user_id,"QRS_Signal":qrs.tolist(), "MFCC":mfcc.tolist(), "ACC":acc.tolist()}
        Features[key] = feature
    
    if save==True:
        ECG_Features = pd.Series(Features)
        with open('data/features/features_'+ user_id+'.json', 'w') as fp:
            json.dump(Features, fp)
        return 1
    else:
        return Features