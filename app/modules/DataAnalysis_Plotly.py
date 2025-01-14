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

#Constants
NEW_VERSION_COLNUM = 35

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
        startTime = time.time() #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
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
        endTime = time.time() #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        print(f">>> [Elapsed Time (sec) for reading a tsv file] { endTime - startTime }")

        #------------------------------------
        # Pre processing for the data frame
        #------------------------------------
        startTime = time.time() #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Eliminating preceding and scceeding spaces from clumn names
        self.df.rename( columns=lambda c: c.strip(), inplace=True )
        # Changing the duplicated column name (Last column name. i.e. "Time")
        self.df.columns = [*self.df.columns[:-1], 'Time2']

        # Converting Datetime (datetime64) to String.
        # Otherwise the process of rendering graph (to_html) takes very long time (aprox 10x times)
        self.df['DateTime'] = self.df['DateTime'].dt.strftime('%Y/%m/%d %H:%M:%S')

        endTime = time.time() #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        print(f">>> [Elapsed Time (sec) for pre-proc of a tsv file] { endTime - startTime }")

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
        if col == NEW_VERSION_COLNUM:
            isNewVersion = True
        else:
            isNewVersion = False
    
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
    
    def create_line_fig( self, options ):
        fig = px.line(self.df, x=options['x_col'], y=options['y_col'], color=options['color'], render_mode="svg")

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

        return fig



def smonAnalysis( tsvfile, isMain ):

    #fig.show()
    #fig1.write_html('first_figure.html', auto_open=True)
    #fig2.write_html('first_figure.html', auto_open=True)

    ana = SmonDataAnalysis( tsvfile )

    graphOptions = {}

    startTime = time.time() #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Creating graphs
    # fig1
    fig1 = ana.create_box_fig( 'AS Instance', 'CPU Usr' )

    # fig2
    graphOptions = {
        "x_col": "DateTime",
        "y_col": "CPU Usr",
        "color": "AS Instance",
        "y_range": [0, 100],
        "y_categoryOrder": "category ascending",
        "desc": "CPU Utilization (User)" 
    } 
    fig2 = ana.create_line_fig( graphOptions )

    # fig3
    fig3 = ana.create_box_fig( 'AS Instance', 'CPU Sys' )
    
    # fig4
    graphOptions['y_col'] = "CPU Sys"
    graphOptions['desc'] = "CPU Utilization (System)"
    fig4 = ana.create_line_fig( graphOptions )

    # fig5
    graphOptions['y_col'] = "Act. WPs"
    graphOptions['y_range'] = None
    graphOptions['desc'] = "Number of Active Work Processes"
    fig5 = ana.create_line_fig( graphOptions )

    # fig6
    graphOptions['y_col'] = "Dia.WPs"
    graphOptions['desc'] = "Number of Active Dialog WPs"
    fig6 = ana.create_line_fig( graphOptions )  

    # fig7
    graphOptions['y_col'] = "RFC Normal"
    graphOptions['desc'] = "Free DIA WPs for RFCs with normal prio"
    fig7 = ana.create_line_fig( graphOptions ) 

    # fig8
    graphOptions['y_col'] = "RFC Low"
    graphOptions['desc'] = "Free DIA WPs for RFC with low priority"
    fig8 = ana.create_line_fig( graphOptions )  

    # fig9
    graphOptions['y_col'] = "FreeMem"
    graphOptions['desc'] = "Free Memory (MB)"
    fig9 = ana.create_line_fig( graphOptions ) 

    # fig10
    graphOptions['y_col'] = "EM alloc."
    graphOptions['desc'] = "Allocated Extended Menmory in MB"
    fig10 = ana.create_line_fig( graphOptions ) 

    # fig11
    graphOptions['y_col'] = "EM attach."
    graphOptions['desc'] = "Attached Extended Memory in MB"
    fig11 = ana.create_line_fig( graphOptions )

    # fig12
    graphOptions['y_col'] = "Heap Memor"
    graphOptions['desc'] = "Heap Memory in MB"
    fig12 = ana.create_line_fig( graphOptions ) 

    # fig13
    # !!! Column "Pagin Mem" is only existing on the new version (at least since ST-PI 740 SP25)
    if isNewVersion: # New version has 34 columns and the column "Paging Mem" is existing as far as I know.
        graphOptions['y_col'] = "Paging Mem"
        graphOptions['desc'] = "Paging Memory (KB)"
        fig13 = ana.create_line_fig( graphOptions )
    else:
        fig13 = None

    # fig14
    graphOptions['y_col'] = "Pri."
    graphOptions['desc'] = "Private Modes"
    fig14 = ana.create_line_fig( graphOptions ) 

    # fig15
    graphOptions['y_col'] = "Dia."
    graphOptions['desc'] = "Dialog Queue Length"
    fig15 = ana.create_line_fig( graphOptions ) 

    # fig16
    graphOptions['y_col'] = "Upd."
    graphOptions['desc'] = "Update Queue Length"
    fig16 = ana.create_line_fig( graphOptions ) 

    # fig17
    graphOptions['y_col'] = "Enq."
    graphOptions['desc'] = "Enqueue Queue Length"
    fig17 = ana.create_line_fig( graphOptions ) 

    # fig18
    graphOptions['y_col'] = "Logins"
    graphOptions['desc'] = "Number of logins"
    fig18 = ana.create_line_fig( graphOptions ) 

    endTime = time.time() #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    print(f">>> [Elapsed Time (sec) for creating 18 graphs] { endTime - startTime }")

    # Setting graph data to a dictionary
    figDict = {}

    startTime = time.time() #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    figDict['fig1'] = fig1.to_html( full_html=False )
    figDict['fig2'] = fig2.to_html( full_html=False )
    figDict['fig3'] = fig3.to_html( full_html=False )
    figDict['fig4'] = fig4.to_html( full_html=False )
    figDict['fig5'] = fig5.to_html( full_html=False )
    figDict['fig6'] = fig6.to_html( full_html=False )
    figDict['fig7'] = fig7.to_html( full_html=False )
    figDict['fig8'] = fig8.to_html( full_html=False )
    figDict['fig9'] = fig9.to_html( full_html=False )
    figDict['fig10'] = fig10.to_html( full_html=False )
    figDict['fig11'] = fig11.to_html( full_html=False )
    figDict['fig12'] = fig12.to_html( full_html=False )
    if isNewVersion:
        figDict['fig13'] = fig13.to_html( full_html=False )
    else:
        figDict['fig13'] = None
    figDict['fig14'] = fig14.to_html( full_html=False )
    figDict['fig15'] = fig15.to_html( full_html=False )
    figDict['fig16'] = fig16.to_html( full_html=False )
    figDict['fig17'] = fig17.to_html( full_html=False )
    figDict['fig18'] = fig18.to_html( full_html=False )
    endTime = time.time() #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    print(f">>> [Elapsed Time (sec) for rendering 18 graphs (to_html)] { endTime - startTime }")

    if isMain is True:
        output_html_path=r"test_result_graphs.html"
        input_template_path=r"../../app/templates/test_results.html"

        plotly_jinja_data = { 
                                "fig_1_1": figDict['fig1'], 
                                "fig_1_2": figDict['fig2'],
                                "fig_2_1": figDict['fig3'],
                                "fig_2_2": figDict['fig4'],
                                "fig_3": figDict['fig5'],
                                "fig_4": figDict['fig6'],
                                "fig_5": figDict['fig7'],
                                "fig_6": figDict['fig8'],
                                "fig_7": figDict['fig9'],
                                "fig_8": figDict['fig10'],
                                "fig_9": figDict['fig11'],
                                "fig_10": figDict['fig12'],
                                "fig_11": figDict['fig13'],
                                "fig_12": figDict['fig14'],
                                "fig_13": figDict['fig15'],
                                "fig_14": figDict['fig16'],
                                "fig_15": figDict['fig17'],
                                "fig_16": figDict['fig18'],
                            }

        with open(output_html_path, "w", encoding="utf-8") as output_file:
            with open(input_template_path) as template_file:
                j2_template = Template(template_file.read())
                output_file.write(j2_template.render(plotly_jinja_data))
        
        fileUrl = 'file:///'+ os.getcwd() + '/' + output_html_path
        webbrowser.open_new_tab(fileUrl)

    else:
        return figDict



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




