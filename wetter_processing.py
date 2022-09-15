#%%

#from inspect import formatannotationrelativeto
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta

#%%
#WETTERMAST
directory = os.getcwd() + "/Wettermast/Kagel3/"
data_interval = '202207010000-202208312350' #used to specify filename

time_delta = timedelta(minutes=10)
start_time = datetime(2022,7,1,0,0)
timesteps = []
for i in range(8928):
    timesteps.append(start_time + i*time_delta)
df = pd.DataFrame(timesteps,columns=['timesteps'])

file_pres = ['TT002_M10_','FF010_M10_','RR_M10_','RDM_M10_','NC_M10_', 'GSM_M10_','TG002_M10_']
names = ['temperature','wind','precipitation_amount','precipitation_duration','cloud_cover','sunshine_duration', 'apparent_temperature']
units = ['°C','m/s','mm','min','1/8','min','°C']

for i in range(len(file_pres)):
    file = file_pres[i] + data_interval + '.txt'
    import_df = pd.read_csv(directory+file,names=[names[i]],encoding='latin8')
    df = pd.concat([df, import_df], axis=1)

#df = df.set_index('timesteps')
df = df.replace(99999,np.nan)

#%%
#STADTHAUSBRÜCKE
directory = os.getcwd() + "/Stadthausbrücke/Kagel4/"
data_interval = '202207010000-202208312350' #used to specify filename

time_delta = timedelta(minutes=10)
start_time = datetime(2022,7,1,0,0)
timesteps = []
for i in range(8928):
    timesteps.append(start_time + i*time_delta)
df = pd.DataFrame(timesteps,columns=['timesteps'])

file_pres = ['IHM_TT_M10_','IHM_RH_M10_','IHM_RRG_M10_','IHM_FF_M10_', 'IHM_G_M10_']
names = ['temperature','relative_humidity','precipitation_amount','wind', 'global_radiation']
units = ['°C','%','mm','m/s','W/m²']

for i in range(len(file_pres)):
    file = file_pres[i] + data_interval + '.txt'
    import_df = pd.read_csv(directory+file,names=[names[i]],encoding='latin8')
    df = pd.concat([df, import_df], axis=1)

#df = df.set_index('timesteps')
df = df.replace(99999,np.nan)

#%%
#export to another .csv
start_date = datetime(2022,8,1,0,0,0)
end_date = datetime(2022,8,31,23,50,0)
date_mask = (df['timesteps'] > start_date) & (df['timesteps'] <= end_date)
df_excerpt = df.loc[date_mask]
df_excerpt = df_excerpt.set_index('timesteps')
df_excerpt.to_csv(directory + "wettermast_export_dataframe.csv",sep=';')
