# Module import 
import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_dropzone import Dropzone

# My own modules
#from modules.DataAnalysis import smonAnalysis
from modules.DataAnalysis_Plotly import smonAnalysis

# 自身の名称を app という名前でインスタンス化する
app = Flask( __name__ )

# https://flask-dropzone.readthedocs.io/en/latest/configuration.html
app.config.update(
	DROPZONE_ALLOWED_FILE_CUSTOM = True,
	DROPZONE_ALLOWED_FILE_TYPE = '.tsv, .txt',
	DROPZONE_REDIRECT_VIEW = 'results',
	DROPZONE_MAX_FILE_SIZE = 30, # MB
)

dropzone = Dropzone(app)

#Global Variant
global GRAPH_HTML 

# Port number is required to fetch from env variable
# http://docs.cloudfoundry.org/devguide/deploy-apps/environment-variable.html#PORT
cf_port = os.getenv("PORT")

# Route / & /index ===============================================================
@app.route('/')
@app.route('/index')
def entry_page() -> 'html':
	return render_template('index.html',
							the_title='Drag and Drop file to be analyzed')

# Route /upload ===============================================================
@app.route('/uploads', methods=['GET', 'POST'])
def upload():
	if request.method == 'POST':
		f = request.files.get('file')
		global GRAPH_HTML
		GRAPH_HTML = smonAnalysis( f, False )
		return 'File is uploaded.'

# Route /results ===============================================================
@app.route('/results')
def results():
		global GRAPH_HTML
		return render_template(
								'results.html',
						        fig_1_1 = GRAPH_HTML['fig1'], # CPU User, Box chart
								fig_1_2 = GRAPH_HTML['fig2'], # CPU User, Line chart
								fig_2_1 = GRAPH_HTML['fig3'], # CPU System, Box chart
								fig_2_2 = GRAPH_HTML['fig4'], # CPU System, Line chart
								fig_3 = GRAPH_HTML['fig5'], # Number of Active Work Processes
								fig_4 = GRAPH_HTML['fig6'], # Number of Active Dialog WPs
								fig_5 = GRAPH_HTML['fig7'], # Free DIA WPs for RFCs with normal prio
								fig_6 = GRAPH_HTML['fig8'], # Free DIA WPs for RFC with low priority
								fig_7 = GRAPH_HTML['fig9'], # Free Memory (MB)
								fig_8 = GRAPH_HTML['fig10'], # Allocated Extended Menmory in MB
								fig_9 = GRAPH_HTML['fig11'], # Attached Extended Memory in MB
								fig_10 = GRAPH_HTML['fig12'], # Heap Memory in MB
								fig_11 = GRAPH_HTML['fig13'], # Paging Memory (KB)
								fig_12 = GRAPH_HTML['fig14'], # Private Modes
								fig_13 = GRAPH_HTML['fig15'], # Dialog Queue Length
								fig_14 = GRAPH_HTML['fig16'], # Update Queue Length
								fig_15 = GRAPH_HTML['fig17'], # Enqueue Queue Length
								fig_16 = GRAPH_HTML['fig18'], # Number of logins
							)

# Run the applicaiton ===============================================================
if __name__ == '__main__':
	if cf_port is None:
		app.run( host='0.0.0.0', port=5000, debug=True )
	else:
		app.run( host='0.0.0.0', port=int(cf_port), debug=True )