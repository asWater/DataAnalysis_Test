# Module import 
import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_dropzone import Dropzone
# For logging of Flask
import logging
from logging.handlers import TimedRotatingFileHandler

# My own modules
#from modules.DataAnalysis import smonAnalysis
#from modules.DataAnalysis_Plotly import DataAnalysis
#from modules.DataAnalysis_Plotly import SMON_Analysis
import modules.DataAnalysis_Plotly as data_ana

# 自身の名称を app という名前でインスタンス化する
app = Flask( __name__ )

# Constants
DROP_MAX_FILE_SIZE = 30
LOG_FIKE = 'logs/app.log'

# Create a timed rotating file handler to manage log files
handler = TimedRotatingFileHandler( LOG_FIKE, when='D', interval=1, backupCount=7 )
handler.setLevel( logging.INFO )

# Create a formatter and add it to the handler
formatter = logging.Formatter( '%(asctime)s - %(levelname)s - %(message)s' )
handler.setFormatter( formatter )

# Add the handler to the root logger
logging.getLogger().addHandler( handler )

# Dropzone settings
# https://flask-dropzone.readthedocs.io/en/latest/configuration.html
app.config.update(
	DROPZONE_ALLOWED_FILE_CUSTOM = True,
	DROPZONE_ALLOWED_FILE_TYPE = '.tsv, .txt',
	DROPZONE_REDIRECT_VIEW = 'results',
	DROPZONE_MAX_FILE_SIZE = DROP_MAX_FILE_SIZE, # MB
	DROPZONE_MAX_FILES = 1,
	DROPZONE_DEFAULT_MESSAGE = f"Drop an output file of /SDF/SMON (Local file > Text with Tab)<br>or<br>The output of SQL: HANA_Resources_CPUAndMemory (Local file > Text with Tab)<br><br><br>File must be separated by TAB (TSV file). File Extention is OK even if it is 'txt'.<br><br><br>Max File Size = {DROP_MAX_FILE_SIZE} MB.",
)

dropzone = Dropzone(app)

#Global Variant
#global GRAPH_HTML
SMON_FILE = "SMON"
HANA_RESOURCE_FILE = "HANA_RESOURCE"
GRAPH_HTML = {}
FILE_TYPE = None

# Port number is required to fetch from env variable
# http://docs.cloudfoundry.org/devguide/deploy-apps/environment-variable.html#PORT
cf_port = os.getenv("PORT")

# Route / & /index ===============================================================
@app.route('/')
@app.route('/index')
def entry_page() -> 'html':
	return render_template('index.html',
							page_title='SMON Data Graph Creator')

# Route /upload ===============================================================
@app.route('/uploads', methods=['GET', 'POST'])
def upload():
	if request.method == 'POST':
		app.logger.info( f'>>> Uploaded from {request.remote_addr}' )
		f = request.files.get('file')

		global FILE_TYPE, GRAPH_HTML
		FILE_TYPE, GRAPH_HTML = data_ana.AnalyzeFile( f, False )
		
	return 'File is uploaded'


# Route /results ===============================================================
@app.route('/results')

def results():
	global FILE_TYPE, GRAPH_HTML

	'''
	figDict_01 = {
		"sec_1_desc": GRAPH_HTML['section_1_desc'],
		"fig_1_1": GRAPH_HTML['fig1'], # CPU User, Box chart
		"fig_1_2": GRAPH_HTML['fig2'], # CPU User, Line chart
		"fig_2_1": GRAPH_HTML['fig3'], # CPU System, Box chart
		"fig_2_2": GRAPH_HTML['fig4'], # CPU System, Line chart
	}

	figDict_02 = {}
	for idx, key, val in enumerate( GRAPH_HTML.items() ):
		if idx >= 5:
			if key.startswith( "section" ):
				figDict_02[f"sec_{idx -3}_desc"] = val
			elif key.startswith( "fig" ):
				figDict_02[f"fig_{idx}"] = val

	return render_template( 'results.html',
							figDict_01 = figDict_01,
							figDict_02 = figDict_02
					)
	'''
	if FILE_TYPE == SMON_FILE:
		return render_template( 'results_SMON.html',
								title = GRAPH_HTML["title"],

								sec_1_desc = GRAPH_HTML['section_1_desc'],
								fig_1_1 = GRAPH_HTML['fig1'], # CPU User, Box chart
								fig_1_2 = GRAPH_HTML['fig2'], # CPU User, Line chart
								fig_2_1 = GRAPH_HTML['fig3'], # CPU System, Box chart
								fig_2_2 = GRAPH_HTML['fig4'], # CPU System, Line chart
								
								sec_2_desc = GRAPH_HTML['section_2_desc'],
								fig_3 = GRAPH_HTML['fig5'], # CPU User + System
								
								sec_3_desc = GRAPH_HTML['section_3_desc'],
								fig_4 = GRAPH_HTML['fig6'], # Number of Active Work Processes
								
								sec_4_desc = GRAPH_HTML['section_4_desc'],
								fig_5 = GRAPH_HTML['fig7'], # Number of Active Dialog WPs
								
								sec_5_desc = GRAPH_HTML['section_5_desc'],
								fig_6 = GRAPH_HTML['fig8'], # Free DIA WPs for RFCs with normal prio
								
								sec_6_desc = GRAPH_HTML['section_6_desc'],
								fig_7 = GRAPH_HTML['fig9'], # Free DIA WPs for RFC with low priority
								
								sec_7_desc = GRAPH_HTML['section_7_desc'],
								fig_8 = GRAPH_HTML['fig10'], # Free Memory (MB)
								
								sec_8_desc = GRAPH_HTML['section_8_desc'],
								fig_9 = GRAPH_HTML['fig11'], # Allocated Extended Menmory in MB
								
								sec_9_desc = GRAPH_HTML['section_9_desc'],
								fig_10 = GRAPH_HTML['fig12'], # Attached Extended Memory in MB
								
								sec_10_desc = GRAPH_HTML['section_10_desc'],
								fig_11 = GRAPH_HTML['fig13'], # Heap Memory in MB
								
								sec_11_desc = GRAPH_HTML['section_11_desc'],
								fig_12 = GRAPH_HTML['fig14'], # Paging Memory (KB)
								
								sec_12_desc = GRAPH_HTML['section_12_desc'],
								fig_13 = GRAPH_HTML['fig15'], # Private Modes
								
								sec_13_desc = GRAPH_HTML['section_13_desc'],
								fig_14 = GRAPH_HTML['fig16'], # Dialog Queue Length
								
								sec_14_desc = GRAPH_HTML['section_14_desc'],
								fig_15 = GRAPH_HTML['fig17'], # Update Queue Length
								
								sec_15_desc = GRAPH_HTML['section_15_desc'],
								fig_16 = GRAPH_HTML['fig18'], # Enqueue Queue Length
								
								sec_16_desc = GRAPH_HTML['section_16_desc'],
								fig_17 = GRAPH_HTML['fig19'], # Number of logins
						)
	
	elif FILE_TYPE == HANA_RESOURCE_FILE:
		return render_template( 'results_HANA.html', 
						 		title=GRAPH_HTML["title"],
								sec_1_desc = GRAPH_HTML['section_1_desc'],
								fig_1 = GRAPH_HTML['fig1'], # CPU User + System
								sec_2_desc = GRAPH_HTML['section_2_desc'],
								fig_2 = GRAPH_HTML['fig2'], # HANA Memory
				)
	else:
		return "Uploaded file type is unknown!<br>File must be TSV (Tab Separated Value) file.<br>Allowed file extentions are .tsv or txt."

# Run the applicaiton ===============================================================
if __name__ == '__main__':
	if cf_port is None:
		app.run( host='0.0.0.0', port=5000, debug=True )
	else:
		app.run( host='0.0.0.0', port=int(cf_port), debug=True )