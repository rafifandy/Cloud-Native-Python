from flask import Flask
from flask import jsonify
from flask import make_response
import json
import sqlite3
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

@app.errorhandler(UnboundLocalError)
def resource_not_found(error):
	return make_response(jsonify({'error':'Resource not found!'}),  404)

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
	
@app.route('/api/v1/users', methods=['GET'])
def get_users():
	return list_users()
def list_users():
	conn = sqlite3.connect('mydb.db')
	print ("Opened database successfully");
	api_list=[]
	cursor = conn.execute("SELECT username, name, email, password, id from users")
	for row in cursor:
		a_dict = {}
		a_dict['username'] = row[0]
		a_dict['name'] = row[1]
		a_dict['email'] = row[2]
		a_dict['password'] = row[3]
		a_dict['id'] = row[4]
		api_list.append(a_dict)
	conn.close()
	return jsonify({'user_list': api_list})

@app.route('/api/v1/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
	return list_user(user_id)
def list_user(user_id):
	conn = sqlite3.connect('mydb.db')
	print ("Opened database successfully");
	api_list=[]
	cursor=conn.cursor()
	cursor.execute("SELECT * from users where id=?",(user_id,))
	data = cursor.fetchall()
	if len(data) != 0:
		user = {}
		user['username'] = data[0][0]
		user['name'] = data[0][1]
		user['email'] = data[0][2]
		user['password'] = data[0][3]
		user['id'] = data[0][4]
	conn.close()
	return jsonify(user)	
	
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=5000, debug=True)
