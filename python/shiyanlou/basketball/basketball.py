import pandas as pd
import math
import csv
import random
import numpy as np
from sklearn import linear_model
from sklearn.model_selection import cross_val_predict

#base elo 1600
base_elo=1600
team_elos={}
team_stats={}
x=[]
y=[]
folder='BasketballData'

def initialize_data(Mstat,Ostat,Tstat):
    new_Mstat=Mstat.drop(['Rk','Arena'],axis=1)
    new_Ostat=Ostat.drop(['Rk','G','MP'],axis=1)
    new_Tstat=Tstat.drop(['Rk','G','MP'],axis=1)
    team_state1=pd.merge(new_Mstat,new_Ostat,how='left',on='Team')
    team_state1=pd.merge(team_state1,new_Tstat,how='left',on='Team')
    return team_state1.set_index('Team',inplace=False,drop=True)

def get_elo(team):
    try:
        return team_elos[team]
    except:
        team_elos[team]=base_elo
        return team_elos[team]

def calc_elo(wteam,lteam):
    winner_rank=get_elo(wteam)
    loser_rank=get_elo(lteam)
    rank_diff=winner_rank-loser_rank
    exp=(rank_diff*-1)/400
    odd=1/(1+math.pow(10,exp))
    #计算K值
    if winner_rank<2100:
        k=32
    elif winner_rank<2400:
        k=24
    else:
        k=16
    new_winner_rank=round(winner_rank+(k*(1-odd)))
    new_rank_diff=new_winner_rank-winner_rank
    new_loser_rank=loser_rank-new_rank_diff
    return new_winner_rank,new_loser_rank

def build_dataset(data):
    print("Building data set...")
    X=[]
    skip=0
    for index,row in data.iterrows():
        Wteam=row['WTeam']
        Lteam=row['LTeam']

        team1_elo=get_elo(Wteam)
        team2_elo=get_elo(Lteam)
        #主场球队加100elo值（主场优势）
        if row['WLoc']=='H':
            team1_elo+=100
        else:
            team2_elo+=200
        team1_feather=[team1_elo]
        team2_feather=[team2_elo]

        for key,value in team_stats.loc[Wteam].items():
            team1_feather.append(value)
        for key,value in team_stats.loc[Lteam].items():
            team2_feather.append(value)
        #将队伍的特征值随机分配在比赛数据的左右两侧
        if random.random()>0.5:
            X.append(team1_feather+team2_feather)
            y.append(0)
        else:
            X.append(team2_feather+team1_feather)
            y.append(1)
        
        if skip==0:
            print(X)
            skip=1
        
        new_winner_rank,new_loser_rank=calc_elo(Wteam,Lteam)
        team_elos[Wteam]=new_winner_rank
        team_elos[Lteam]=new_loser_rank
    return np.nan_to_num(X),y

def predict_winner(team_1,team_2,model):
    feathers=[]
    #team1,客场队伍
    feathers.append(get_elo(team_1))
    for key,value in team_stats.loc[team_1].items():
        feathers.append(value)

    #team2,主场队伍
    feathers.append(get_elo(team_2)+100)
    for key,value in team_stats.loc[team_2].items():
        feathers.append(value)

    feathers=np.nan_to_num(feathers)
    return model.predict_proba([feathers])

if __name__=="__main__":
    Mstat=pd.read_csv(folder+'/15-16Miscellaneous_Stat.csv')
    Ostat=pd.read_csv(folder+'/15-16Opponent_Per_Game_Stat.csv')
    Tstat=pd.read_csv(folder+'/15-16Team_Per_Game_Stat.csv')

    team_stats=initialize_data(Mstat,Ostat,Tstat)

    result_data=pd.read_csv(folder+'/2015-2016_result.csv')
    X,y=build_dataset(result_data)

    print("Fitting on %d game samples..."%len(X))
    model=linear_model.LogisticRegression()
    model.fit(X,y)
    #10折交叉验证正确率
    print("Doing cross-validation..")
    print(cross_val_predict(model,X,y,cv=10,scoring='accuracy',n_jobs=-1).mean())

    #预测
    print("Predicting on new schedule..")
    schedule1617=pd.read_csv(folder+'/16-17Schedule.csv')
    result=[]
    for index,row in schedule1617.iterrows():
        team1=row['Vteam']
        team2=row['Hteam']
        pred=predict_winner(team1,team2,model)
        prob=pred[0][0]
        if prob>0.5:
            winner=team1
            loser=team2
            result.append([winner,loser,prob])
        else:
            winner=team2
            loser=team1
            result.append([winner,loser,1-prob])
        with open(folder+'/16-17Result.csv') as f:
            writer=csv.writer(f)
            writer.writerow(['win','lose','probability'])
            writer.writerows(result)
     