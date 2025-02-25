import pandas as pd

import sys
import os.path
import time

import plotly.io as pio
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from jinja2 import Template
import webbrowser

global dataFrame
global isNewVersion

# Constants
NEW_VERSION_COLNUM = 35
SMON_1ST_COL_NAME = "Date"
HANA_RESOURCE_1ST_COL_NAME = "SNAPSHOT_TIME"
CPU_SYS_USR_COL_NAME = 'CPU_Sys_User'
GRAPH_LABEL_COLOR = "rgba(200,200,200,1)"
GRAPH_PAPER_BGCOLOR = "rgba(36,36,36,1)"
GRAPH_PLOT_BGCOLOR = "rgba(197,212,235,1)"
SMON_FILE = "SMON"
HANA_RESOURCE_FILE = "HANA_RESOURCE"

#HTML_TMP = '<img src="data:image/png;base64,{image_bin}">'


#>>> START of CLASS: SmonDataAnalysis >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
class SmonDataAnalysis():

    def __init__( self, df ):
        self.df = df

        #------------------------------------
        # Pre processing for the data frame
        #------------------------------------
        # Eliminating preceding and scceeding spaces from clumn names
        self.df.rename( columns=lambda c: c.strip(), inplace=True )
        # Changing the duplicated column name (Last column name. i.e. "Time")
        self.df.columns = [*self.df.columns[:-1], 'Time2']

        self.df["DateTime"] = self.df["Date"] + " " + self.df["Time"]
        self.df["DateTime"] = pd.to_datetime(self.df["DateTime"], format='%Y/%m/%d %H:%M:%S')
        # Converting Datetime (datetime64) to String.
        # Otherwise the process of rendering graph (to_html) takes very long time (aprox 10x times)
        #self.df['DateTime'] = self.df['DateTime'].dt.strftime('%Y/%m/%d %H:%M:%S')

        # Adding a new column "CPU_Sys_User" with adding CPU Sys to CPU Usr
        self.df[CPU_SYS_USR_COL_NAME] = self.df['CPU Sys'] + self.df['CPU Usr']

        global dataFrame
        dataFrame = self.df

        # Getting Dataframe Information After Pre-Processing to Dataframe
        print(self.df.head())
        print(self.df.info())
        #print(df.describe())
        #print("CPU User Average: ", df['CPU Usr'].mean())
        #print("CPU System Average: ", df['CPU Sys'].mean())

        # Taking the number of row & col in order to know new version of SMON or not
        # (Only checking the column number)
        row, col = self.df.shape
        global isNewVersion
        if col >= NEW_VERSION_COLNUM:
            isNewVersion = True
        else:
            isNewVersion = False

        print(f">>> IsNewVersion: {isNewVersion}")
    
    def create_box_fig( self, x_col, y_col, desc ):
        fig = px.box(self.df, x=x_col, y=y_col)
        fig.update_layout(
            title=dict(
                text=desc,
                font=dict(
                    size=15,
                    color=GRAPH_LABEL_COLOR,
                )
            ),
            yaxis_range=[0, 100],
            paper_bgcolor=GRAPH_PAPER_BGCOLOR,
            plot_bgcolor=GRAPH_PLOT_BGCOLOR,
            font_color=GRAPH_LABEL_COLOR,
        )
        #fig.update_yaxes(range=[0, 100])

        return fig
    
    def create_line_fig( self, options ):
        fig = px.line(self.df, x=options['x_col'], y=options['y_col'], color=options['color'], render_mode="svg")

        fig.update_layout(
            title=dict(
                #text=options['desc'],
                font=dict(
                    size=15,
                    color="grey",
                )
            ),
            yaxis_range=options['y_range'],
            yaxis_categoryorder=options['y_categoryOrder'],
            xaxis_categoryorder='array',
            xaxis_categoryarray=self.df[options['x_col']],
            xaxis_dtick=350,
            paper_bgcolor=GRAPH_PAPER_BGCOLOR,
            plot_bgcolor=GRAPH_PLOT_BGCOLOR,
            font_color=GRAPH_LABEL_COLOR,
        )

        return fig
#<<< END of CLASS: SmonDataAnalysis <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


def SMON_Analysis( df, isMain ):

    #fig.show()
    #fig1.write_html('first_figure.html', auto_open=True)
    #fig2.write_html('first_figure.html', auto_open=True)

    ana = SmonDataAnalysis( df )

    graphOptions = {}
    # Setting graph data to a dictionary
    figDict = { "title": "SMON Analysis is finished" }

    
    if isMain is True:
        print("This is not implemented to execute directly")
    else:
        return figDict


def HANA_Resource_Analysis( df, isMain ):
    #df = pd.read_csv(tsvfile, skiprows=1, header=0, usecols=lambda c: c is not None, skip_blank_lines=True, sep='\t')
    figDict = { "title": "HANA Resource Analysis is finished" }
    if isMain is True:
        print(figDict)
    else:
        return figDict


def DataFileCheck( anaFile ):
    # "header" = header row number
    # "skiprow=1" is necessary to handle old SMON data, because it has a text ("Monitoring Data") at the row 0.
    df = pd.read_csv(anaFile, skiprows=1, header=0, usecols=lambda c: c is not None, skip_blank_lines=True, sep='\t')

    if df.columns[1] == SMON_1ST_COL_NAME:
        dataFileType = SMON_FILE
    elif df.columns[1] == HANA_RESOURCE_1ST_COL_NAME:
        dataFileType = HANA_RESOURCE_FILE
    
    return dataFileType, df

def AnalyzeFile( tsvfile, isMain ):
    fileType, df = DataFileCheck( tsvfile )
    
    #with open( tsvfile ) as f:
    #    next(f)
    #    second_line = f.readline()

    
    if fileType == SMON_FILE:
        figDict = SMON_Analysis( df, False )
    elif fileType == HANA_RESOURCE_FILE:
        figDict = HANA_Resource_Analysis( df, False )
    else:
        figDict = None
    
    return figDict

#============================================================:=================================================
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
            fileType = DataFileCheck( anaFile )
            if fileType == "SMON":
                SMON_Analysis( anaFile, True )
            elif fileType == "HANA_RESOURCE":
                HANA_Resource_Analysis( anaFile, True )
            else:
                print ('!!! This file cannot be analyzed by this program !!!' )
                sys.exit()
        else:
            print ('!!! Could not find the file: ' + anaFile )
            sys.exit()




