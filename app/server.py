# Module import 
import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_dropzone import Dropzone

# My own modules
from modules.DataAnalysis import smonAnalysis

# 自身の名称を app という名前でインスタンス化する
app = Flask( __name__ )

# https://flask-dropzone.readthedocs.io/en/latest/configuration.html
app.config.update(
	DROPZONE_ALLOWED_FILE_CUSTOM = True,
	DROPZONE_ALLOWED_FILE_TYPE = '.tsv, .txt',
	DROPZONE_REDIRECT_VIEW = 'results' 
)

dropzone = Dropzone(app)

#Global Variant
global IMAGE_HTML 

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
		global IMAGE_HTML
		IMAGE_HTML = smonAnalysis( f, False )
		return 'File is uploaded.'

# Route /results ===============================================================
@app.route('/results')
def results():
		global IMAGE_HTML
		return render_template('results.html',
						        fig_image = IMAGE_HTML )

# Run the applicaiton ===============================================================
if __name__ == '__main__':
	if cf_port is None:
		app.run( host='0.0.0.0', port=5000, debug=True )
	else:
		app.run( host='0.0.0.0', port=int(cf_port), debug=True )