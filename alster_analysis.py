#%%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import seaborn as sns
import os
import scipy 
import matplotlib.dates as mdates

from matplotlib.dates import DateFormatter


#%%
df_boats = pd.read_csv('C:/Users/torbj/OneDrive/Geo_Oze/4Semester/63-620, WissenschaftlichesArbeiten/Projektarbeit/Image_Download_Copy/resampled/webcam_data20220823_resampled.csv',sep=';')
df_boats['datetime'] = pd.to_datetime(df_boats['datetime'])
df_boats= df_boats.set_index('datetime')

df_wetter = pd.read_csv('C:/Users/torbj/OneDrive/Geo_Oze/4Semester/63-620, WissenschaftlichesArbeiten/Projektarbeit/Daten_UniHH/Wettermast/Kagel3/wettermast_export_dataframe.csv',sep=';')
df_wetter['timesteps'] = pd.to_datetime(df_wetter['timesteps'])
start_date = datetime(2022,8,23,0,0,0)
end_date = datetime(2022,8,23,23,50,0)
date_mask = (df_wetter['timesteps'] >= start_date) & (df_wetter['timesteps'] <= end_date)
df_wetter = df_wetter.loc[date_mask]
df_wetter.astype({'sunshine_duration': 'float64'}).dtypes
df_wetter = df_wetter.set_index('timesteps')
sns.regplot(x=df_wetter['sunshine_duration'], y=df_boats["boats_polygon"]) 
# plt.plot(df_wetter['temperature'])
# plt.plot(df_boats['boats_polygon'])
#%%
#Boats daily means:
os.chdir('C:/Users/torbj/OneDrive/Geo_Oze/4Semester/63-620, WissenschaftlichesArbeiten/Projektarbeit/Image_Download_Copy/resampled')
filelist = os.listdir()
boats_means = []
boats_max =[]
start_date_list =[]
format = '%Y-%m-%d %H:%M:%S'

for element in filelist:
    df_boats = pd.read_csv(element,sep=';')

    df_boats['datetime'] =pd.to_datetime(df_boats['datetime'],format=format)
    start_date_list.append(df_boats['datetime'][0].date())
    if start_date_list[len(start_date_list)-1] > datetime(2022,8,31,0,0,0).date():
        break
    df_boats= df_boats.set_index(pd.DatetimeIndex(df_boats['datetime']))
    df_boats_day = df_boats.between_time('08:00','21:00')
    boats_means.append(df_boats_day['boats'].mean())
    boats_max.append(max(df_boats_day['boats']))


#Weather daily means

#!! sunshine duration aufsummieren und gegen plote plotten

df_wetter = pd.read_csv('C:/Users/torbj/OneDrive/Geo_Oze/4Semester/63-620, WissenschaftlichesArbeiten/Projektarbeit/Daten_UniHH/Wettermast/Kagel3/wettermast_export_dataframe.csv',sep=';')
df_wetter['timesteps'] = pd.to_datetime(df_wetter['timesteps'])

weather_means = []
weather_max =[]
weather_sums = []
end_date_list = []    
start_time = datetime.strptime('0700','%H%M').time()
weather_key = 'sunshine_duration'

for i in range(len(start_date_list)-1):
    start_date_list[i] = datetime.combine(start_date_list[i], start_time)
    end_date_list.append(start_date_list[i] + timedelta(hours=14))
    date_mask = (df_wetter['timesteps'] >= start_date_list[i]) & (df_wetter['timesteps'] <= end_date_list[i])
    df_wetter_date = df_wetter.loc[date_mask]
    weather_means.append(df_wetter_date[weather_key].mean())
    weather_max.append(max(df_wetter_date[weather_key]))

    weather_sums.append(np.sum(df_wetter_date[weather_key]))

# plt.plot(boats_means)

# plt.plot(weather_means)

#manuelle datums-selektion

#!! Listen nochmal überarbeiten, mit neuem Kalendarplot
peak_days = (0,6,7,14,15,16,20,21,22)
plateau_days = (3,4,5,9,11,18,19)

weather_list = []
boats_list =[]
weather_list.append([weather_sums[i] for i in peak_days])
boats_list.append([boats_means[i] for i in peak_days])
weather_list = weather_list[0]
boats_list = boats_list[0]
r_square, p = scipy.stats.pearsonr(weather_list, boats_list)
 
fig, ax = plt.subplots(dpi=200)
ax.set_xlim(np.floor(min(weather_list)),np.ceil(max(weather_list)))
ax.set_ylim(0,20)
ax.set_yticks(range(0,21,2))

ax = sns.regplot(x=weather_list, y=boats_list,marker="x",color='black',line_kws={"color":"r","alpha":0.7,"lw":3},truncate=False) 
# fig.suptitle("Peakdays",fontsize=14)
ax.set_xlabel("daily total sunshine duration [min]")
ax.set_ylabel('daily boat means')
ax.text(0.05,0.9,"R²="+"{:.3f}".format(r_square),fontsize=14,ha='left',va='center',transform = ax.transAxes)
ax.grid()
# plt.tight_layout()
plt.show()

#%% 
#Wetterstationen Vergleich

df_wettermast = pd.read_csv('C:/Users/torbj/OneDrive/Geo_Oze/4Semester/63-620, WissenschaftlichesArbeiten/Projektarbeit/Daten_UniHH/Wettermast/Kagel3/wettermast_export_dataframe.csv',sep=';')
df_wettermast['timesteps'] = pd.to_datetime(df_wetter['timesteps'])

df_stadthaus = pd.read_csv('C:/Users/torbj/OneDrive/Geo_Oze/4Semester/63-620, WissenschaftlichesArbeiten/Projektarbeit/Daten_UniHH/Stadthausbrücke/Kagel4/wettermast_export_dataframe.csv',sep=';')
df_stadthaus['timesteps'] = pd.to_datetime(df_wetter['timesteps'])

start_date = datetime(2022,8,4,0,0,0)
end_date = datetime(2022,8,7,0,0,0)
weather_key = 'wind'
date_mask = (df_wettermast['timesteps'] >= start_date) & (df_wettermast['timesteps'] <= end_date)
df_wettermast = df_wettermast.loc[date_mask]
date_mask = (df_stadthaus['timesteps'] >= start_date) & (df_stadthaus['timesteps'] <= end_date)
df_stadthaus = df_stadthaus.loc[date_mask]
df_stadthaus = df_stadthaus.set_index('timesteps')
df_wettermast = df_wettermast.set_index('timesteps')
r_square, p = scipy.stats.pearsonr(df_wettermast[weather_key], df_stadthaus[weather_key])


fig,ax = plt.subplots(dpi=200)
# ax = sns.regplot(x=df_wettermast[weather_key], y=df_stadthaus[weather_key], scatter_kws = {"color": "gray", "alpha": 0.2},line_kws={"color":"r","alpha":0.7,"lw":3},truncate=False) 
# ax.text(0.05,0.9,"R²="+"{:.3f}".format(r_square),fontsize=14,ha='left',va='center',transform = ax.transAxes)

ax.plot(df_wettermast['precipitation_amount'],color='darkcyan',label='Wettermast')
ax.plot(df_stadthaus['precipitation_amount'],color='coral',label='Stadthausbrücke')
ax.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m\n%H:%M"))
ax.grid()
ax.set_xlabel('Wettermast, wind [m/s]')
ax.set_ylabel('Stadthausbrücke, wind [m/s]')
plt.legend()
plt.show()