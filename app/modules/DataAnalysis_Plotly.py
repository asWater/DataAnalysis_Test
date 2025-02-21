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
        # "header" = header row number
        # "skiprow=1" is necessary to handle old SMON data, because it has a text ("Monitoring Data") at the row 0.
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

        # Adding a new column "CPU_Sys_User" with adding CPU Sys to CPU Usr
        self.df[CPU_SYS_USR_COL_NAME] = self.df['CPU Sys'] + self.df['CPU Usr']

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



def SMON_Analysis( tsvfile, isMain ):

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
                "col_name": CPU_SYS_USR_COL_NAME,
                "col_desc": "CPU Utilization (User + System)"
            },
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
                                "sec_1_desc": figDict['section_1_desc'],
                                "fig_1_1": figDict['fig1'], # CPU User, Box chart
                                "fig_1_2": figDict['fig2'], # CPU User, Line chart
                                "fig_2_1": figDict['fig3'], # CPU System, Box chart
                                "fig_2_2": figDict['fig4'], # CPU System, Line chart
                                
                                "sec_2_desc": figDict['section_2_desc'],
                                "fig_3": figDict['fig5'], # CPU User + System
                                
                                "sec_3_desc": figDict['section_3_desc'],
                                "fig_4": figDict['fig6'], # Number of Active Work Processes
                                
                                "sec_4_desc": figDict['section_4_desc'],
                                "fig_5": figDict['fig7'], # Number of Active Dialog WPs
                                
                                "sec_5_desc": figDict['section_5_desc'],
                                "fig_6": figDict['fig8'], # Free DIA WPs for RFCs with normal prio
                                
                                "sec_6_desc": figDict['section_6_desc'],
                                "fig_7": figDict['fig9'], # Free DIA WPs for RFC with low priority
                                
                                "sec_7_desc": figDict['section_7_desc'],
                                "fig_8": figDict['fig10'], # Free Memory (MB)
                                
                                "sec_8_desc": figDict['section_8_desc'],
                                "fig_9": figDict['fig11'], # Allocated Extended Menmory in MB
                                
                                "sec_9_desc": figDict['section_9_desc'],
                                "fig_10": figDict['fig12'], # Attached Extended Memory in MB
                                
                                "sec_10_desc": figDict['section_10_desc'],
                                "fig_11": figDict['fig13'], # Heap Memory in MB
                                
                                "sec_11_desc": figDict['section_11_desc'],
                                "fig_12": figDict['fig14'], # Paging Memory (KB)
                                
                                "sec_12_desc": figDict['section_12_desc'],
                                "fig_13": figDict['fig15'], # Private Modes
                                
                                "sec_13_desc": figDict['section_13_desc'],
                                "fig_14": figDict['fig16'], # Dialog Queue Length
                                
                                "sec_14_desc": figDict['section_14_desc'],
                                "fig_15": figDict['fig17'], # Update Queue Length
                                
                                "sec_15_desc": figDict['section_15_desc'],
                                "fig_16": figDict['fig18'], # Enqueue Queue Length
                                
                                "sec_16_desc": figDict['section_16_desc'],
                                "fig_17": figDict['fig19'], # Number of logins
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


def HANA_Resource_Analysis( tsvfile, isMain ):
    figDict = "Not yet implemented for HANA Resource Analysis"
    if isMain is True:
        print(figDict)
    else:
        return figDict


def DataFileCheck( anaFile ):
    # "header" = header row number
    # "skiprow=1" is necessary to handle old SMON data, because it has a text ("Monitoring Data") at the row 0.
    df = pd.read_csv(anaFile, skiprows=1, header=0, usecols=lambda c: c is not None, skip_blank_lines=True, sep='\t')

    if df.columns[1] == SMON_1ST_COL_NAME:
        dataFileType = "SMON"
    elif df.columns[1] == HANA_RESOURCE_1ST_COL_NAME:
        dataFileType = "HANA_RESOURCE"
    
    return dataFileType



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




