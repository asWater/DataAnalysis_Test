import pandas as pd

import sys
import os.path

import plotly.io as pio
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from jinja2 import Template
import webbrowser

global dataFrame

#HTML_TMP = '<img src="data:image/png;base64,{image_bin}">'


class SmonDataAnalysis():

    def __init__( self, tsvfile ):
        # Reference of pandas.read_csv: https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
        # SMON TSV File: 
        # (First number: 0)
        # > Column Titles: Row 2 (S/4 ver 1808, BASIS 753), Row 1 (S/4 ver 2023, BASIS 758)
        # > Column Starts: Col 1
        # > Total columns number: 31
        # > Data Starts: Row 4
        #df = pd.read_csv(tsvfile, skiprows=1, header=0, usecols=range(1,34), skip_blank_lines=True, sep='\t')
        self.df = pd.read_csv(tsvfile, skiprows=1, header=0, usecols=lambda c: c is not None, skip_blank_lines=True, sep='\t')

        #------------------------------------
        # Pre processing for the data frame
        #------------------------------------
        # Eliminating preceding and scceeding spaces from clumn names
        self.df.rename( columns=lambda c: c.strip(), inplace=True )
        # Changing the duplicated column name (Last column name. i.e. "Time")
        self.df.columns = [*self.df.columns[:-1], 'new_name']

        global dataFrame
        dataFrame = self.df

        print(self.df.head())
        print(self.df.info())
        #print(df.describe())
        #print("CPU User Average: ", df['CPU Usr'].mean())
        #print("CPU System Average: ", df['CPU Sys'].mean())
    
    def create_box_fig( self, x_col, y_col ):
        fig = px.box(self.df, x=x_col, y=y_col)
        fig.update_layout(
            title=dict(
                text=f"{x_col} / {y_col}",
                font=dict(
                    size=15,
                    color="grey",
                )
            ),
            yaxis_range=[0, 100],
        )
        #fig.update_yaxes(range=[0, 100])

        return fig
    
    def create_line_fig( self, options):
        fig = px.line(self.df, x=options['x_col'], y=options['y_col'], color=options['color'])
        fig.update_layout(
            title=dict(
                text=options['desc'],
                font=dict(
                    size=15,
                    color="grey",
                )
            ),
            yaxis_range=options['y_range'],
            yaxis_categoryorder=options['y_categoryOrder'],
            xaxis_categoryorder='array',
            xaxis_categoryarray=self.df['Time'],
        )

        return fig



def smonAnalysis( tsvfile, isMain ):


    #fig.show()
    #fig1.write_html('first_figure.html', auto_open=True)
    #fig2.write_html('first_figure.html', auto_open=True)

    ana = SmonDataAnalysis( tsvfile )

    graphOptions = {}

    # Creating graphs
    graphOptions = {
        "x_col": "Time",
        "y_col": "CPU Usr",
        "color": "AS Instance",
        "y_range": [0, 100],
        "y_categoryOrder": "category ascending",
        "desc": "Test Graph" 
    }

    graphOptions['y_range'] = None
    graphOptions['y_col'] = "Dia."
    fig = ana.create_line_fig( graphOptions ) 
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




