import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
import io
import base64
import sys
import os.path

# matplotlibでTcl_AsyncDelete: async handler deleted by the wrong threadが出たときのトラブルシューティング
# > https://catdance124.hatenablog.jp/entry/2019/09/20/113202
# > https://stackoverflow.com/questions/27147300/matplotlib-tcl-asyncdelete-async-handler-deleted-by-the-wrong-thread
import matplotlib
#===============================================
# Renderere Filetypes   Description
#-------------------------------------------
# AGG       png         raster grapahics - high quality images using the Anti-Grain Geometry engine
#-------------------------------------------

# If I set "AGG", the figure cannot be interactive. i.e. It is not possible to use mplcursors
#matplotlib.use('Agg')

import mplcursors
from matplotlib import dates as mdates
from datetime import datetime
import plotly.io as pio
import plotly.express as px

global dataFrame

#HTML_TMP = '<img src="data:image/png;base64,{image_bin}">'

def smonAnalysis( tsvfile, isMain ):
    # Reference of pandas.read_csv: https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
    # SMON TSV File: 
    # (First number: 0)
    # > Column Titles: Row 2 (S/4 ver 1808, BASIS 753), Row 1 (S/4 ver 2023, BASIS 758)
    # > Column Starts: Col 1
    # > Total columns number: 31
    # > Data Starts: Row 4
    #df = pd.read_csv(tsvfile, skiprows=1, header=0, usecols=range(1,34), skip_blank_lines=True, sep='\t')
    df = pd.read_csv(tsvfile, skiprows=1, header=0, usecols=lambda c: c is not None, skip_blank_lines=True, sep='\t')
    
    global dataFrame
    dataFrame = df

    print(df.head())
    print(df.info())
    #print(df.describe())
    #print("CPU User Average: ", df['CPU Usr'].mean())
    #print("CPU System Average: ", df['CPU Sys'].mean())

    #df_cpu = pd.DataFrame(data=df, columns=[ df["Time"].name, df["AS Instance"].name, df["CPU Usr"].name, df["CPU Sys"].name ])

    fig = px.line(df, x="Time", y="CPU Usr", color='AS Instance')

    fig.update_layout(
        title=dict(
            text="CPU consumption (%) by Users",
            font=dict(
                size=26,
                color="grey",
            )
        ),
        yaxis_range=[0, 100],
        xaxis_categoryorder='array',
        xaxis_categoryarray=df['Time'],
    )

    #fig.update_yaxes(range=[0, 100])

    #fig.show()
    fig.write_html('first_figure.html', auto_open=True)


#=============================================================================================================
# if __name__=="__main__": が記述ある場合に、「ファイル名.py 」がモジュールとして、他のプログラムから読み込まれ場合に、
# if __name__=="__main__": 配下の処理を実行させないようにするためのif文。
# if __name__ == "__main__": があると、モジュールがPythonスクリプトとして起動された場合
# （＊例えばpython ファイル名.py 等にて実行された場合）のみ、if __name__ == “__main__”: 配下の処理が実行されます。
if __name__ == '__main__':
    argvs = sys.argv
    argc = len(argvs)

    if argc <= 1:
        print('!!! You need to specify the argument (file name) to execute this file !!!')
        sys.exit()
    else:
        anaFile = '../../app/data/' + argvs[1]

        if os.path.isfile( anaFile ):
            smonAnalysis( anaFile, True )
        else:
            print ('!!! Could not find the file: ' + anaFile )
            sys.exit()




