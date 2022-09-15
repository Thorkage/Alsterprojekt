#%%
from doctest import testfile
from inspect import FrameInfo
import pandas as pd
import os
from datetime import date, datetime, timedelta
import numpy as np
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Patch

from scipy.interpolate import interp1d
import numpy as np
from scipy.signal import savgol_filter
import math
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
from matplotlib.dates import DateFormatter
#%%
#sns.set_theme(style="darkgrid")

plt.style.use('default')

os.chdir('//wsl.localhost/Ubuntu/home/torka/wissArb_Projektarbeit/Image_Download_Copy/')
print(os.getcwd())
header =['datetime','boats','birds','brightness','flag']
d={}
d_resampled={}
d_box={}
df_box=[]
filelist = os.listdir()
dates=[]
i=0
for element in filelist:
        if 'webcam' and '.csv' not in element:
            filelist[i]=''
        i+=1

while '' in filelist:
    filelist.remove('')
filelist = sorted(filelist)

for element in filelist:
    dates.append(datetime.strptime(str(element[11:-4]),"%Y%m%d"))

print(filelist)
#%%
#legend items

custom_lines = [
    Patch(facecolor='lemonchiffon', edgecolor='black', label='past download'),
    Patch(facecolor='lightcyan', edgecolor='black', label='VDI system'),
    Patch(facecolor='whitesmoke', edgecolor='black', label='no data avaiable'),
    Patch(facecolor='honeydew', edgecolor='black', label='transition phase'),
    Patch(facecolor='lavender', edgecolor='black', label='local system')
]

fig,ax = plt.subplots(dpi=300,figsize=(10,4))
x_data = pd.date_range(start='2022-08-01', periods=4, freq='W-MON')
for element in filelist:
    df_element = pd.read_csv(element, names=header)
    d_box[pd.to_datetime(element[11:19], format='%Y%m%d').date()]=df_element['boats']
    df_element['datetime']= pd.to_datetime(df_element['datetime'], format='%Y%m%d%H%M')
    df_element.drop_duplicates(subset='brightness',keep='first',inplace=True)
    df_element.reset_index(inplace=True)
    for i in range(len(df_element)-4):
        if df_element['datetime'].iloc[i] >= df_element['datetime'].iloc[i+1]:
            df_element = df_element.drop(df_element.index[i+1])
    df_element = df_element.set_index('datetime')
    df_element.drop(columns='index',inplace=True)
    df_element = df_element.resample('10T').mean()  

    df_element['boats_rolled'] = df_element['boats'].rolling(window=20,center=True,min_periods=5).mean()
    df_element['boats_polygon'] = savgol_filter(df_element['boats_rolled'], 25, 3)
    
    d[element] = df_element
    #d_resampled[element] = df_resampled
    #OVERVIEW PLOT OF ALL MEASURING DAYS
    
    ax.set_xticks(x_data)
    ax.tick_params(axis='x', rotation=45, which='both')
    ax.xaxis.set_minor_locator(MultipleLocator(1))
    ax.xaxis.set_minor_formatter(mdates.DateFormatter("%d.%m"))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m"))
    ax.grid(visible=True,which='major',linestyle='solid',zorder=0)
    ax.grid(visible=True,which='minor',linestyle='dotted',zorder=0)
    #fig.suptitle('Gesamte Messphase')
    ax.plot(d[element]['boats_polygon'],color='darkslategrey',zorder=10)

    ax.set_xlabel('datetime')
    ax.set_ylabel('boat_polygon')
    plt.tight_layout()

    #DIFFERENT BACKGROUNDS IN OVERVIEW PLOT:
    #past phase
    ax.axvspan(datetime(2022,8,2,0,0,0),datetime(2022,8,7,0,0,0),color='lemonchiffon')

    #VDI phase
    ax.axvspan(datetime(2022,8,7,0,0,0),datetime(2022,8,16,0,0,0),color='lightcyan',zorder=-1)

    #no data avaible
    ax.axvspan(datetime(2022,8,1,0,0,0),datetime(2022,8,2,0,0,0),color='whitesmoke',zorder=0)
    ax.axvspan(datetime(2022,8,9,0,0,0),datetime(2022,8,11,0,0,0),color='whitesmoke',zorder=0)
    ax.axvspan(datetime(2022,8,14,0,0,0),datetime(2022,8,15,0,0,0),color='whitesmoke',zorder=0)
    ax.axvspan(datetime(2022,8,16,0,0,0),datetime(2022,8,19,0,0,0),color='whitesmoke',zorder=0)
    #transition phase
    ax.axvspan(datetime(2022,8,19,0,0,0),datetime(2022,8,20,0,0,0),color='honeydew',zorder=0)

    #local phase
    ax.axvspan(datetime(2022,8,20,0,0,0),dates[len(dates)-1]+timedelta(days=1),color='lavender',zorder=0)
    
    fig.legend(
        handles=custom_lines,
        loc='lower center', 
        bbox_to_anchor=(0.5,-0.05),
        ncol=5,
        frameon=False)

#%%--------------------------------------------------
#ÜBERSICHT ZUR BEARBEITUNG DER ROHDATEN FUER EINEN TAG
fig,axs = plt.subplots(3,1,dpi=300, sharey=True, sharex=True,figsize=(5,8))
fig.add_subplot(111, frameon=False)
plt.tick_params(labelcolor='none', top=False, bottom=False, left=False, right=False)

filelist_index = 'webcam_data20220811.csv'
title=d[filelist_index].index[0].date()
title=datetime.strftime(title,'%d.%m.%Y')
axs[0].plot(d[filelist_index]['boats'],color='green',label='raw data')
axs[1].plot(d[filelist_index]['boats_rolled'],color='blue',zorder=5,label='moving average')
axs[2].plot(d[filelist_index]['boats_polygon'],color='red',zorder=10,label='Savitzky–Golay filter')
axs[2].xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
axs[2].tick_params(axis='x', rotation=45)

ax.set_xlabel('datetime')
ax.set_ylabel('boat count')
fig.suptitle(title)
axs[0].grid()
axs[1].grid()
axs[2].grid()
axs[0].legend(loc='upper left')
axs[1].legend(loc='upper left')
axs[2].legend(loc='upper left')
plt.ylabel("boat count")
plt.tight_layout()

#%%-------------------
#SHAPE COMPARISON PLOT (Calendar)
for element in filelist:
    df_element = pd.read_csv(element, names=header)
    d_box[pd.to_datetime(element[11:19], format='%Y%m%d').date()]=df_element['boats']
    df_element['datetime']= pd.to_datetime(df_element['datetime'], format='%Y%m%d%H%M')
    df_element.drop_duplicates(subset='brightness',keep='first',inplace=True)
    df_element.reset_index(inplace=True)
    for i in range(len(df_element)-4):
        if df_element['datetime'].iloc[i] >= df_element['datetime'].iloc[i+1]:
            df_element = df_element.drop(df_element.index[i+1])
    df_element.drop(columns='index',inplace=True)

    df_element['boats_rolled'] =df_element['boats'].rolling(window=20,center=True,min_periods=5).mean()
    df_element['boats_polygon'] = savgol_filter(df_element['boats_rolled'], 25, 3)
    
    d[element] = df_element

fig, axs  = plt.subplots(5,7,dpi=300, sharex=True,sharey=True,figsize=(10,6))
dates=[]
k=0
x_data = pd.date_range(start='2020-01-01 07:00:00', periods=3, freq='7H')
# fig.suptitle('Measuring phase - calendar')
for i in range(5):
    for j in range(7):
        dates.append(datetime(2022,8,1,0,0,0)+ k* timedelta(days=1))
        current_date = dates[k].strftime('%Y%m%d')
        title_date = dates[k].strftime('%d.%m.%Y')
        element = 'webcam_data' + current_date + '.csv'
        axs[i,j].title.set_text(title_date)
        # axs[i,j].xaxis.set_visible(False) 
        
        try:
            df = d[element]
            # header_list = list(df.columns)
            # header_list.append('datetime2')
            # df = df.reindex(columns = header_list)                

            for p in range(len(df)):
                try: 
                    df['datetime'][p] = df['datetime'][p].replace(year=2020,month=1,day=1)
                except:
                    pass
            # df= df.set_index(df['datetime'])
            df= df.set_index(pd.DatetimeIndex(df['datetime']))
            df_day = df.between_time('07:00','21:00')
            axs[i,j].plot(df_day['boats_polygon'],color='navy')
            axs[i,j].set_xticks(x_data)
            axs[i,j].xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
            axs[i,j].tick_params(axis='x', rotation=45)
            
        except:
            axs[i,j].patch.set_facecolor('lightgray')
 
        k+=1
fig.supxlabel('time')
fig.supylabel('boats_polygon')
axs[0,0].title.set_text('Monday\n\n'+ "01.08.2022" )
axs[0,1].title.set_text('Tuesday\n\n'+ "02.08.2022" )
axs[0,2].title.set_text('Wednesday\n\n'+ "03.08.2022" )
axs[0,3].title.set_text('Thursday\n\n'+ "04.08.2022" )
axs[0,4].title.set_text('Friday\n\n'+ "05.08.2022" )
axs[0,5].title.set_text('Saturday\n\n'+ "06.08.2022" )
axs[0,6].title.set_text('Sunday\n\n'+ "07.08.2022" )

fig.tight_layout()
#%%------------------
#BOX-AND-WHISKER PLOT
from matplotlib.pyplot import cm

fig,ax = plt.subplots(dpi=300,figsize=(4,10))
x_data = pd.date_range(start='2022-08-01', periods=31, freq='d')
data = pd.DataFrame.from_dict(d_box)
data[data == 0] =np.nan

sns.violinplot(ax=ax,data=data,whis=np.inf,zorder=10,cut=0,scale='count',inner=None, linewidth=0, orient='h')

# ax.set_xticklabels(dates, rotation=45)
#ax.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m"))
#ax.tick_params(axis='x', rotation=90)

ax.get_yticklabels()
texts = [t.get_text()  for t in ax.get_yticklabels()]
texts_dates = [(x[8:10]+'.'+x[5:7])  for x in texts]
ax.set_yticklabels(t for t in texts_dates)

ax.set_ylabel('datetime')
ax.set_xlabel('boat count')

# first = color[6]
# color = np.flipud(color) # palette=color,

# custom_lines = [
#     Patch(facecolor=color[0], label='Tuesday'),
#     Patch(facecolor=color[1], label='Wednesday'),
#     Patch(facecolor=color[2], label='Thursday'),
#     Patch(facecolor=color[3], label='Friday'),
#     Patch(facecolor=color[4], label='Saturday'),
#     Patch(facecolor=color[5], label='Sunday'),
#     Patch(facecolor=color[6], label='Monday')
# ]

ax.xaxis.grid(True)
ax.set_axisbelow(True)

# fig.legend(
#         handles=custom_lines,
#         loc='lower center', 
#         bbox_to_anchor=(0.5,-0.05),
#         ncol=7,
#         frameon=False)

plt.tight_layout()


#%% ---------------------------------------------------
#EXPORT TO .CSV FILES (rounded on 10min intervals!)
os.chdir('C:/Users/torbj/OneDrive/Geo_Oze/4Semester/63-620, WissenschaftlichesArbeiten/Projektarbeit/Image_Download_Copy')
for element in filelist:
    df_export = d[element]
    df_export.to_csv(os.getcwd() + "/resampled/"+element[:-4]+"_resampled.csv",sep=';')
