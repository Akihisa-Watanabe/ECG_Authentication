import glob
import numpy as np
import re
import signal_process
import create_template
import authentication
import pandas as pd


AMP_COEF = 5.0 / 1023 #AD変換係数
Fs = 200  #サンプリング周波数513.367
dt = 1/Fs #サンプリング周期
N_MFCC = 20 #MFCCの次元数
feature_name = "QRS_Signal"

def read_data(filename):
    dat = np.loadtxt(filename)
    dat= dat*AMP_COEF 
    dat = dat[1000:-1000] #波形が安定していないことが多いため，両端のデータは除外する
    return dat


RAW_FILES=glob.glob("data/raw/*.csv")

for file in RAW_FILES:
    data_id = re.findall("data/raw/raw_(.*).csv",file)[0] 
    raw_ecg = read_data(file)
    cleaned_ecg, rpeaks = signal_process.preprocessing(raw_ecg,fs=Fs,pipline_method="elgendi2010",graph_show=False)
    segment_data = signal_process.get_segmentation(cleaned_ecg,rpeaks,fs=Fs,graph_show=False)
    signal_process.feature_extraction(data_id,segment_data,fs=Fs,save=False)

FEATURE_FILES = glob.glob("data/features/*.json")

for file in FEATURE_FILES:
    if re.fullmatch(r"data/features/features_user[0-9]+_0.json",file): #テンプレート用のデータかチェック
        data_id = re.findall("data/features/features_(.*).json",file)[0] 
        features = pd.read_json(file)
        template = create_template.create_template(features,feature_name)
        print(data_id)
        save_file = "data/templates/template_" + data_id + ".csv"
        np.savetxt(save_file, template, delimiter=',',fmt='%.18f')