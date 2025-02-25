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
import modules.DataAnalysis_Test as data_ana
import time


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
	DROPZONE_DEFAULT_MESSAGE = f"Drop an output file of /SDF/SMON (Local file > Text with Tab)<br>Max File Size = {DROP_MAX_FILE_SIZE} MB.",
)

dropzone = Dropzone(app)

#Global Variant
GRAPH_HTML = {}
#GRAPH_HTML = None 

# Port number is required to fetch from env variable
# http://docs.cloudfoundry.org/devguide/deploy-apps/environment-variable.html#PORT
cf_port = os.getenv("PORT")

# Route / & /index ===============================================================
@app.route('/')
@app.route('/index')
def entry_page() -> 'html':
	return render_template('index.html',
							page_title='Flask Behavior Test')

# Route /upload ===============================================================
@app.route('/uploads', methods=['GET', 'POST'])
def upload():
	if request.method == 'POST':
		app.logger.info( f'>>> Uploaded from {request.remote_addr}' )
		f = request.files.get('file')

		#!!!
		# 1 function should check the file and execute the analsys without calling the following func 
		# to check the file type ???
		#!!!
		global GRAPH_HTML
		GRAPH_HTML = data_ana.AnalyzeFile( f, False )
		
	return 'File is uploaded'


# Route /results ===============================================================
@app.route('/results')
def results():
	global GRAPH_HTML
	return render_template( 'results.html', title=GRAPH_HTML["title"] )

# Run the applicaiton ===============================================================
if __name__ == '__main__':
	if cf_port is None:
		app.run( host='0.0.0.0', port=5000, debug=True )
	else:
		app.run( host='0.0.0.0', port=int(cf_port), debug=True )