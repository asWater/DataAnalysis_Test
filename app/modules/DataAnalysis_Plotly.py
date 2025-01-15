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
    
    def create_box_fig( self, x_col, y_col, desc ):
        fig = px.box(self.df, x=x_col, y=y_col)
        fig.update_layout(
            title=dict(
                text=desc,
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
        )

        return fig



def smonAnalysis( tsvfile, isMain ):

    #fig.show()
    #fig1.write_html('first_figure.html', auto_open=True)
    #fig2.write_html('first_figure.html', auto_open=True)

    ana = SmonDataAnalysis( tsvfile )

    graphOptions = {}
    # Setting graph data to a dictionary
    figDict = {}

    # Common texts
    COL_NAME_PAGINGMEM = "Paging Mem"

    startTime = time.time() #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Creating graphs
    # fig1
    figDict['section_1_desc'] = "CPU Utilization"
    fig = ana.create_box_fig( 'AS Instance', 'CPU Usr', 'CPU Utilization by Users' )
    figDict['fig1'] = fig.to_html( full_html=False )

    # fig2
    graphOptions = {
        "x_col": "DateTime",
        "y_col": "CPU Usr",
        "color": "AS Instance",
        "y_range": [0, 100],
        "y_categoryOrder": "category ascending",
        "desc": "CPU Utilization (User)" 
    } 
    fig = ana.create_line_fig( graphOptions )
    figDict['fig2'] = fig.to_html( full_html=False )

    # fig3
    fig = ana.create_box_fig( 'AS Instance', 'CPU Sys', 'CPU Utilization by System' )
    figDict['fig3'] = fig.to_html( full_html=False )
    
    # fig4
    graphOptions['y_col'] = "CPU Sys"
    graphOptions['desc'] = "CPU Utilization (System)"
    fig = ana.create_line_fig( graphOptions )
    figDict['fig4'] = fig.to_html( full_html=False )

    smonDataInfo = {
        "smonCols": [
            {
                "col_name": "Act. WPs",
                "col_desc": "Number of Active Work Processes"
            },
            {
                "col_name": "Dia.WPs",
                "col_desc": "Number of Active Dialog WPs"
            },
            {
                "col_name": "RFC Normal",
                "col_desc": "Free DIA WPs for RFCs with normal prio"
            },
            {
                "col_name": "RFC Low",
                "col_desc": "Free DIA WPs for RFC with low priority"
            },
            {
                "col_name": "FreeMem",
                "col_desc": "Free Memory (MB)"
            },
            {
                "col_name": "EM alloc.",
                "col_desc": "Allocated Extended Menmory in MB"
            },
            {
                "col_name": "EM attach.",
                "col_desc": "Attached Extended Memory in MB"
            },
            {
                "col_name": "Heap Memor",
                "col_desc": "Heap Memory in MB"
            },
            {
                "col_name": COL_NAME_PAGINGMEM,
                "col_desc": "Paging Memory (KB)"
            },
            {
                "col_name": "Pri.",
                "col_desc": "Private Modes"
            },
            {
                "col_name": "Dia.",
                "col_desc": "Dialog Queue Length"
            },
            {
                "col_name": "Upd.",
                "col_desc": "Update Queue Length"
            },
            {
                "col_name": "Enq.",
                "col_desc": "Enqueue Queue Length"
            },
            {
                "col_name": "Logins",
                "col_desc": "Number of logins"
            },
        ]
    }

    graphOptions['y_range'] = None

    # Creating other graphs
    for i, key in enumerate(smonDataInfo['smonCols']):
        # New version has 34 columns and the column "Paging Mem" is existing as far as I know.  
        # Column "Pagin Mem" is only existing in the new version (at least since ST-PI 740 SP25)  
        if not isNewVersion and key['col_name'] == COL_NAME_PAGINGMEM:
            figDict[f'fig{i+5}'] = None
            figDict[f'section_{i+2}_desc'] = None
        else:
            graphOptions['y_col'] = key['col_name']
            graphOptions['desc'] = key['col_desc']
            fig = ana.create_line_fig( graphOptions )
            figDict[f'fig{i+5}'] = fig.to_html( full_html=False )
            figDict[f'section_{i+2}_desc'] = key['col_desc']
                

    endTime = time.time() #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    print(f">>> [Elapsed Time (sec) for creating/rendering graphs] { endTime - startTime }")

    
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
                                "sec_1_desc": figDict['section_1_desc'],
                                "sec_2_desc": figDict['section_2_desc'],
                                "sec_3_desc": figDict['section_3_desc'],
                                "sec_4_desc": figDict['section_4_desc'],
                                "sec_5_desc": figDict['section_5_desc'],
                                "sec_6_desc": figDict['section_6_desc'],
                                "sec_7_desc": figDict['section_7_desc'],
                                "sec_8_desc": figDict['section_8_desc'],
                                "sec_9_desc": figDict['section_9_desc'],
                                "sec_10_desc": figDict['section_10_desc'],
                                "sec_11_desc": figDict['section_11_desc'],
                                "sec_12_desc": figDict['section_12_desc'],
                                "sec_13_desc": figDict['section_13_desc'],
                                "sec_14_desc": figDict['section_14_desc'],
                                "sec_15_desc": figDict['section_15_desc'],
                            }
        startTime = time.time() #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        with open(output_html_path, "w", encoding="utf-8") as output_file:
            with open(input_template_path) as template_file:
                j2_template = Template(template_file.read())
                output_file.write(j2_template.render(plotly_jinja_data))
        
        fileUrl = 'file:///'+ os.getcwd() + '/' + output_html_path
        webbrowser.open_new_tab(fileUrl)
        endTime = time.time() #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        print(f">>> [Elapsed Time (sec) for opening a html file] { endTime - startTime }")

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




