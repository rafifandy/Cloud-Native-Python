from flask import Flask
from flask import jsonify
import json
import sqlite3
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
@app.route("/api/v1/info")
def home_index():
	conn = sqlite3.connect('mydb.db')
	print ("Opened database successfully");
	api_list=[]
	cursor = conn.execute("SELECT buildtime, version, methods, links from apirelease")
	for row in cursor:
		a_dict = {}
		a_dict['version'] = row[0]
		a_dict['buildtime'] = row[1]
		a_dict['methods'] = row[2]
		a_dict['links'] = row[3]
		api_list.append(a_dict)
	conn.close()
	return jsonify({'api_version': api_list}), 200
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=5000, debug=True)
