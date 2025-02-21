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
import mpld3

# Constants
SMON_1ST_COL_NAME = "Date"
HANA_RESOURCE_1ST_COL_NAME = "SNAPSHOT_TIME"

global dataFrame

#HTML_TMP = '<img src="data:image/png;base64,{image_bin}">'

def DataAnalysis( tsvfile, isMain ):
    # Reference of pandas.read_csv: https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
    # SMON TSV File: 
    # (First number: 0)
    # > Column Titles: Row 2 (S/4 ver 1808, BASIS 753), Row 1 (S/4 ver 2023, BASIS 758)
    # > Column Starts: Col 1
    # > Total columns number: 31
    # > Data Starts: Row 4
    #df = pd.read_csv(tsvfile, skiprows=1, header=0, usecols=range(1,34), skip_blank_lines=True, sep='\t')
    # "header" = header row number
    # "skiprow=1" is necessary to handle old SMON data, because it has a text ("Monitoring Data") at the row 0.
    df = pd.read_csv(tsvfile, skiprows=1, header=0, usecols=lambda c: c is not None, skip_blank_lines=True, sep='\t')
    
    if df.columns[1] == SMON_1ST_COL_NAME:
        SMON_Analysis( df, isMain )
    elif df.columns[1] == HANA_RESOURCE_1ST_COL_NAME:
        HANA_Analysis( df, isMain )


def SMON_Analysis( df, isMain ):
    for i, time in enumerate(df['Time']):
        #df['Time'][i] = datetime.strptime(time, '%H:%M:%S')
        df.loc[i, 'Time'] = datetime.strptime(time, '%H:%M:%S')

    global dataFrame
    dataFrame = df

    print(df.head())
    print(df.info())
    #print(df.describe())
    #print("CPU User Average: ", df['CPU Usr'].mean())
    #print("CPU System Average: ", df['CPU Sys'].mean())

    #df_cpu = pd.DataFrame(data=df, columns=[ df["Time"].name, df["AS Instance"].name, df["CPU Usr"].name, df["CPU Sys"].name ])

    # To show some graphs(axes) in a figure
    # (In this case, Rows:2, Cols: 2)
    fig = plt.figure(facecolor="white", tight_layout=True)
    fig.set_size_inches(16, 9)
    gs = fig.add_gridspec(2, 3)

    plt.rcParams["font.size"] = 8

    # Graph (Axes) definitions
    ax_r1_box = fig.add_subplot(gs[0, 0], facecolor="white")
    ax_r1_line = fig.add_subplot(gs[0, 1:3], facecolor="white")
    ax_r2_box = fig.add_subplot(gs[1, 0], facecolor="white")
    ax_r2_line = fig.add_subplot(gs[1, 1:3], facecolor="white")

    #----------------------------------------
    # Boxplot
    #----------------------------------------
    sns.boxplot( data=df, x="AS Instance", y="CPU Usr", ax=ax_r1_box )
    sns.boxplot( data=df, x="AS Instance", y="CPU Sys", ax=ax_r2_box )

    # Changing the angle of X label
    #plt.setp( plt.gca().get_xticklabels(), rotation=90 )
    ax_r1_box.set_xticklabels(ax_r1_box.get_xticklabels(), rotation=90)
    ax_r2_box.set_xticklabels(ax_r1_box.get_xticklabels(), rotation=90)

    #----------------------------------------
    # Lineplot
    #----------------------------------------
    sns.lineplot( data=df, x="Time", y="CPU Usr", hue="AS Instance", ax=ax_r1_line )
    sns.lineplot( data=df, x="Time", y="CPU Sys", hue="AS Instance", ax=ax_r2_line )

    # Setting the distance of lable in X-Axis
    #plt.gca().xaxis.set_major_locator( ticker.MultipleLocator(10) )
    #ax_r1_line.xaxis.set_major_locator( ticker.MultipleLocator(25) )
    #ax_r2_line.xaxis.set_major_locator( ticker.MultipleLocator(25) )

    ax_r1_line.xaxis.set_major_formatter( mdates.DateFormatter('%H:%M:%S') )

    #plt.setp( plt.gca().get_xticklabels(), rotation=90 )
    ax_r1_line.set_xticklabels( ax_r1_line.get_xticklabels(), rotation=45, fontname='72 Monospace', fontsize=9 )
    ax_r2_line.set_xticklabels( ax_r1_line.get_xticklabels(), rotation=45, fontname='72 Monospace', fontsize=9 )

    ax_r1_line.legend( bbox_to_anchor=(1.0, 1.0), loc='upper left', borderaxespad=0, fontsize=8 )
    ax_r2_line.legend( bbox_to_anchor=(1.0, 1.0), loc='upper left', borderaxespad=0, fontsize=8 )

    # I don't know why "plt.ylim([0, 100])" does not affect all axes (only affects line charts)
    # so I've set it in the following FOR LOOP.
    for ax in fig.axes:
        ax.set_ylim([0, 100])


    # Plots created using seaborn need to be displayed like ordinary matplotlib plots. 
    #plt.show()

    #mplcursors.cursor( ax_r1_line, hover=True )
    cursor = mplcursors.cursor( hover=True )
    #cursor.connect( 'add', lambda sel: sel.annotation.set_text( df.loc[ sel.index, ["Time", "CPU Usr", "AS Instance"] ].to_string() ) )
    cursor.connect( 'add', show_annotation )

    if isMain:
        plt.show()
        plt.close()
    else:
        graphImage = img2html( fig )
        plt.close()
        return graphImage


def HANA_Analysis( df, isMain ):
    print('TEST')


def img2html( fig ):
    sio = io.BytesIO()
    fig.savefig( sio, format='png' )
    image_bin = base64.b64encode( sio.getvalue() )
    #return HTML_TMP.format( image_bin = str( image_bin )[2:-1] )
    return str( image_bin )[2:-1] 


def show_annotation( sel ):
    xi, yi = sel.target
    #xi = int( round( xi ) )
    #sel.annotation.set_text(f'{dataFrame['Time'][xi]}\nValue:{yi:.2f}')
    #sel.annotation.set_text(f'{mdates.DateFormatter('%H:%M:%S')(xi)}\nValue:{yi:.2f}\nInstance: {dataFrame['AS Instance'][int(round(sel.index))]}')
    sel.annotation.set_text(f'{mdates.DateFormatter('%H:%M:%S')(xi)}\nValue:{yi:.2f}')


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
            DataAnalysis( anaFile, True )
        else:
            print ('!!! Could not find the file: ' + anaFile )
            sys.exit()




