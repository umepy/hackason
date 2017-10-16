# coding:utf-8
# 地区別の価格の変化を見るスクリプト

import pandas as pd
import numpy as np
import pickle
import tqdm
import datetime
import copy
import matplotlib.pyplot as plt
import random


# データ読み込み
def read_bukken():
    return pd.read_csv('../data/20170810_1615_output_bukkens.tsv',delimiter='\t')
def read_trans():
    return pd.read_csv('../data/20170810_1615_output_trans.tsv',delimiter='\t',parse_dates=['p_ymd'])

# 金額変化を辞書にしてpickle化
def to_dic_pickle():
    df=read_trans()
    with open('../data/city_dic.pickle','rb') as f:
        city_dic=pickle.load(f)
    out_dic={}
    for i in city_dic.keys():
        out_dic[i]={}
    bukken_ids=pd.unique(df['project_cd'])
    month_default={'first':0}
    for i in ['7','8','9','10','11','12','1','2','3','4','5','6']:
        month_default[i]=0

    for i in tqdm.tqdm(bukken_ids):
        id_df=df[df['project_cd']==i]
        now_value=0
        now_month=0
        bukken_month=copy.deepcopy(month_default)
        for j in id_df.iterrows():
            j=j[1]
            if now_value==0:
                bukken_month['first']=j['kakaku']
                now_value=j['kakaku']
                now_month=j['p_ymd'].month
            if now_month!=j['p_ymd'].month:
                bukken_month[str(now_month)]=now_value
                now_value=j['kakaku']
                now_month = j['p_ymd'].month
        bukken_month[str(now_month)] = now_value

        # 市の特定
        i_city=None
        for city_name,id_list in city_dic.items():
            if i in id_list:
                i_city=city_name
        assert i_city!=None
        out_dic[i_city][i]=bukken_month

    with open('../data/trans_dic.pickle','wb') as f:
        pickle.dump(out_dic,f)

# project_idを市別で辞書化
def city_dictionary():
    df=read_bukken()
    unique_city=pd.unique(df['shikugun_nm'])

    # unique_cityの個数
    print(len(unique_city))

    city_dic={}

    for i in unique_city:
        city_dic[i]=list(df[df['shikugun_nm']==i]['project_cd'])

    with open('../data/city_dic.pickle','wb') as f:
        pickle.dump(city_dic,f)

# 各市に対して時系列変化の平均算出
def cities_time_price_change():
    with open('../data/city_dic.pickle','rb') as f:
        city_dic=pickle.load(f)
    with open('../data/trans_dic.pickle', 'rb') as f:
        trans_dic=pickle.load(f)

    out_dic={}

    for city in city_dic.keys():
        month_score = {}
        for num in ['7', '8', '9', '10', '11', '12', '1', '2', '3', '4', '5', '6']:
            month_score[num] = []
        for id in trans_dic[city].keys():
            pre_value = trans_dic[city][id]['first']
            for month in ['7', '8', '9', '10', '11', '12', '1', '2', '3', '4', '5', '6']:
                if trans_dic[city][id][month]==0:
                    continue
                if pre_value!=trans_dic[city][id][month]:
                    month_score[month].append(trans_dic[city][id][month]/float(pre_value))
                    pre_value=trans_dic[city][id][month]

        # 平均算出
        for month in ['7', '8', '9', '10', '11', '12', '1', '2', '3', '4', '5', '6']:
            if len(month_score[month])==0:
                month_score[month]=0
            month_score[month]=np.mean(month_score[month])
        out_dic[city]=month_score
    with open('../data/cities_time_price_change.pickle', 'wb') as f:
        pickle.dump(out_dic, f)

# 月単位の時系列変化の可視化
def view_cities_change(city_num=None):
    with open('../data/cities_time_price_change.pickle', 'rb') as f:
        data=pickle.load(f)
    if city_num!=None:
        city=list(data.keys())[city_num]
        X=[]
        y=[]
        month_iter=0
        name_iter=[]
        for month in ['7', '8', '9', '10', '11', '12', '1', '2', '3', '4', '5', '6']:
            if data[city][month]!=0:
                X.append(month_iter)
                y.append(data[city][month])
                name_iter.append(month)
            month_iter+=1
        plt.title(city)
        plt.bar(X,y,align='center')
        plt.xticks(X,name_iter)
        plt.show()
    else:
        for city in data.keys():
            if random.random()>0.2:
                continue
            X = []
            y = []
            month_iter = 0
            name_iter=[]
            for month in ['7', '8', '9', '10', '11', '12', '1', '2', '3', '4', '5', '6']:
                if data[city][month] != 0:
                    X.append(month_iter)
                    y.append(data[city][month])
                    name_iter.append(month)
                month_iter += 1
            plt.plot(X, y,label=city)
            plt.xticks(X,name_iter)
        plt.title('各都市の平均不動産価格変化')
        plt.legend()
        plt.show()

# 年で各都市を比較
def view_cities_year_change():
    with open('../data/cities_time_price_change.pickle', 'rb') as f:
        data=pickle.load(f)
    y = []
    name_iter=[]
    for city in data.keys():
        count = 0
        score=1
        for month in ['7', '8', '9', '10', '11', '12', '1', '2', '3', '4', '5', '6']:
            if data[city][month] != 0:
                score*=data[city][month]
                count+=1
        if count>10:
            y.append(score)
            name_iter.append(city)
    # sort
    data = sorted(zip(y,name_iter),key=lambda x:x[0], reverse=True)
    y=[x for x,y in data]
    name_iter=[y for x,y in data]
    plt.title('各都市の年率不動産価格変化')
    plt.bar(range(len(name_iter)), y,align='center', label=city)
    plt.xticks(range(len(name_iter)), name_iter,rotation=30)
    plt.show()

view_cities_year_change()