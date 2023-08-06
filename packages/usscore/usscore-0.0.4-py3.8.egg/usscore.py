import requests,re
import pandas as pd
import subprocess as sp
import sys,os
if os.path.exists('us-states.csv'):
 d=pd.read_csv('us-states.csv')
else:
 sp.call("wget https://github.com/nytimes/covid-19-data/raw/master/live/us-states.csv",shell=True)
 d=pd.read_csv('us-states.csv')
if os.path.exists('PopulationReport.csv'):
 p=pd.read_csv('PopulationReport.csv')
else:
 sp.call("wget https://github.com/ytakefuji/scoreUS/raw/main/PopulationReport.csv",shell=True)
 p=pd.read_csv('PopulationReport.csv')
pp=p.set_index('Name').drop(['United States'])
pp=pp.reset_index()
dd=d.set_index('state').drop(['American Samoa','Guam','Northern Mariana Islands','Puerto Rico','Virgin Islands'])
dd=dd.reset_index()
names=dd.state
L=len(names)
score=pd.DataFrame(
  {
   "state": names,
   "deaths": dd.deaths,
   "population": range(L),
   "score": range(L),
  })
for i in names:
 score.loc[score.state==i, 'population']=round(int(str(pp.loc[pp.Name==i,'Pop. 2020'].tolist().pop()).replace(',',''))/1000000,3)
 score.loc[score.state==i,'score']=int(score.loc[score.state==i,'deaths']/score.loc[score.state==i,'population'])
score=score.sort_values(by=['score'])
score.to_csv('result.csv',index=False)
def main():
 score=pd.read_csv('result.csv')
 print(score)
if __name__ == "__main__":
 main()
