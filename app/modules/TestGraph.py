import pandas as pd

import sys
import os.path
import time

import plotly.express as px
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
        self.df = pd.read_csv(
                tsvfile, 
                skiprows=1, 
                header=0, 
                usecols=lambda c: c is not None, 
                skip_blank_lines=True, 
                sep='\t',
                parse_dates={'DateTime': ['Date', 'Time']},
                keep_date_col=True,
            )

        #------------------------------------
        # Pre processing for the data frame
        #------------------------------------
        # Eliminating preceding and scceeding spaces from clumn names
        self.df.rename( columns=lambda c: c.strip(), inplace=True )
        # Changing the duplicated column name (Last column name. i.e. "Time")
        self.df.columns = [*self.df.columns[:-1], 'new_name']

        # Converting Datetime (datetime64) to String.
        # Otherwise the process of rendering graph (write_html) takes very long time (aprox 10x times)
        self.df['DateTime'] = self.df['DateTime'].dt.strftime('%Y/%m/%d %H:%M:%S')

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
        startTime = time.time()
        fig = px.line(self.df, x=options['x_col'], y=options['y_col'], color=options['color'], render_mode="svg")
        endTime = time.time()
        print(f">>> [Elapsed Time for px.line ({ options['desc'] })] { endTime - startTime }")
        
        startTime = time.time()
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
            xaxis_categoryarray=self.df[options['x_col']],
            xaxis_dtick=350,
        )
        endTime = time.time()
        print(f">>> [Elapsed Time for update_layout ({ options['desc'] })] { endTime - startTime }")

        return fig



def smonAnalysis( tsvfile, isMain ):
    '''
    << Performance Indicators >>

    x_col = DateTime, update_layout xaxis_categoryorder & xaxis_categoryarray
    >>> [Elapsed Time for px.line] 0.5901980400085449
    >>> [Elapsed Time for update_layout] 0.031058788299560547
    >>> [Elapsed Time for write_html] 22.648017168045044

    x_col = DateTime, w/o update xaxis
    >>> [Elapsed Time for px.line] 0.5911874771118164
    >>> [Elapsed Time for update_layout] 0.004826545715332031
    >>> [Elapsed Time for write_html] 11.200293779373169

    x_col= Time, update_layout xaxis_categoryorder & xaxis_categoryarray
    >>> [Elapsed Time for px.line] 0.5231802463531494
    >>> [Elapsed Time for update_layout] 0.010878324508666992
    >>> [Elapsed Time for write_html] 1.1043014526367188
    '''

    #fig.show()
    #fig1.write_html('first_figure.html', auto_open=True)
    #fig2.write_html('first_figure.html', auto_open=True)

    ana = SmonDataAnalysis( tsvfile )

    graphOptions = {}

    # Creating graphs
    graphOptions = {
        "x_col": "DateTime",
        "y_col": "CPU Usr",
        "color": "AS Instance",
        "y_range": [0, 100],
        "y_categoryOrder": "category ascending",
        "desc": "Test Graph" 
    }

    #graphOptions['y_range'] = None
    #graphOptions['y_col'] = "Dia."
    fig = ana.create_line_fig( graphOptions )

    startTime = time.time()
    fig.write_html('test_figure.html', auto_open=True)
    endTime = time.time()
    print(f">>> [Elapsed Time for write_html] { endTime - startTime }")






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




