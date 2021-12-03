import glob
import numpy as np
import re
import signal_process
import create_template
import authentication
import pandas as pd
import json


AMP_COEF = 5.0 / 1024 #AD変換係数
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
    raw_ecg -= np.mean(raw_ecg)
    cleaned_ecg, rpeaks = signal_process.preprocessing(raw_ecg,fs=Fs,pipline_method="elgendi2010",graph_show=False)
    segment_data = signal_process.get_segmentation(cleaned_ecg,rpeaks,fs=Fs,graph_show=False)
    signal_process.feature_extraction(data_id,segment_data,fs=Fs,save=False)

FEATURE_FILES = glob.glob("data/features/*.json")

for file in FEATURE_FILES:
    if re.fullmatch(r"data/features/features_user[0-9]+_0.json",file): #テンプレート用のデータかチェック
        data_id = re.findall("data/features/features_(.*).json",file)[0] 
        features = pd.read_json(file)
        template = create_template.create_template(features,feature_name)
        save_file = "data/templates/template_" + data_id + ".csv"
        np.savetxt(save_file, template, delimiter=',',fmt='%.18f')


TEMPLATE_FILES = glob.glob("data/templates/*.csv")
AUTH_FILES = glob.glob("data/features/*_[!0].json")
result={}

for template_file in TEMPLATE_FILES:
    template = np.loadtxt(template_file)
    template_id = re.findall("data/templates/template_(.*).csv",template_file)[0]
    scores={}
    for auth_file in AUTH_FILES:
        auth_id = re.findall("data/features/features_(.*).json",auth_file)[0] 
        df_auth = pd.read_json(auth_file)
        score = authentication.get_DTW(df_auth,template,feature_name)
        scores[auth_id] = score
    scores=sorted(scores.items(), key=lambda x: x[1],reverse=True)
    result[template_id] = scores

for template in result.keys():
    template_user = re.findall("(.*)_0",template)[0] 
    print("template : {0}\n".format(template_user))
    print("test user : score")
    for user_score in result[template]:
        test_user = re.findall("(.*)_[1-9]+",user_score[0])[0] 
        score = user_score[1]
        print("{0} : {1} [%]".format(test_user,score))
    print("-------------------")

result_path ="data/result/result.json"
with open(result_path, 'w') as fp:
    json.dump(result, fp)