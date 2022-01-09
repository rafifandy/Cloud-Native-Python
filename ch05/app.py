from flask import Flask,jsonify,make_response,request,abort,\
render_template,session,redirect,url_for,flash
from flask_cors import CORS, cross_origin
from time import gmtime,strftime
from pymongo import MongoClient
from flask_pymongo import PyMongo
from flask_mongoalchemy import MongoAlchemy
import json,sqlite3,random,bcrypt

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
CORS(app)
app.secret_key = 'key'

connection = MongoClient('mongodb://localhost:27017/')
app.config['MONGOALCHEMY_DATABASE'] = 'app'
app.config['MONGOALCHEMY_CONNECTION_STRING'] = 'mongodb://localhost:27017/'
app.config["MONGO_URI"] = 'mongodb://localhost:27017/'
mongo=PyMongo(app)

def create_mongodatabase():
	try:
		dbnames = connection.database_names()
		if 'cloud_native' not in dbnames:
			db = connection.cloud_native.users
			db_tweets = connection.cloud_native.tweets
			db_api = connection.cloud_native.apirelease

			db.insert({
			"email": "eric.strom@google.com",
			"id": 33,
			"name": "Eric stromberg",
			"password": "eric@123",
			"username": "eric.strom"
			})
			db_tweets.insert({
			"body": "New blog post,Launch your app with the AWS Startup \
			Kit! #AWS",
			"id": 18,
			"timestamp": "2017-03-11T06:39:40Z",
			"tweetedby": "eric.strom"
			})
			db_api.insert( {
			"buildtime": "2017-01-01 10:00:00",
			"links": "/api/v1/users",
			"methods": "get, post, put, delete",
			"version": "v1"
			})
			db_api.insert( {
			"buildtime": "2017-02-11 10:00:00",
			"links": "api/v2/tweets",
			"methods": "get, post",
			"version": "2017-01-10 10:00:00"
			})
			print ("Database Initialize completed!")
		else:
			print ("Database already Initialized!")
	except:
		print ("Database creation failed!!")

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method=='POST':
        users = connection.cloud_native.users
        api_list=[]
        existing_users = users.find({"username":session['logged_in']})
        for i in existing_users:
            # print (str(i))
            api_list.append(str(i))
        user = {}
        print (api_list)
        if api_list != []:
            print (request.form['email'])
            user['email']=request.form['email']
            user['name']= request.form['name']
            user['password']=request.form['pass']
            users.update({'username':session['logged_in']},{'$set': user} )
        else:
            return 'User not found!'
        return redirect(url_for('index'))
    if request.method=='GET':
        users = connection.cloud_native.users
        user=[]
        #print (session['username'])
        existing_user = users.find({"username":session['logged_in']})
        for i in existing_user:
            user.append(i)
        return render_template('profile.html', name=user[0]['name'], username=user[0]['username'], password=user[0]['password'], email=user[0]['email'])



@app.route("/logout")
def logout():
    session['logged_in'] = False
    return redirect(url_for('home'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method=='POST':
        users = connection.cloud_native.users
        api_list=[]
        existing_user = users.find({'$or':[{"username":request.form['username']} ,{"email":request.form['email']}]})
        for i in existing_user:
            # print (str(i))
            api_list.append(str(i))

        # print (api_list)
        if api_list == []:
            users.insert({
            "email": request.form['email'],
            "id": random.randint(1,1000),
            "name": request.form['name'],
            #"password": bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt()),
            "password": request.form['pass'],
            "username": request.form['username']
            })
            session['username'] = request.form['username']
            return redirect(url_for('home'))

        return 'That user already exists'
    else :
        return render_template('signup.html')

@app.route('/login', methods=['POST'])
def do_admin_login():
	users = connection.cloud_native.users
	api_list=[]
	login_user = users.find({'username': request.form['username']})
	for i in login_user:
		api_list.append(i)
	print (api_list)
	if api_list != []:
		#if api_list[0]['password'].decode('utf-8') == bcrypt.hashpw(request.form['password'].encode('utf-8'), api_list[0]['password']).decode('utf-8'):
		# print (api_list[0]['password'].decode('utf-8'), bcrypt.hashpw(request.form['password'].encode('utf-8'), api_list[0]['password']).decode('utf-8'))
		#if api_list[0]['password'] == bcrypt.hashpw(request.form['password'].encode('utf-8'), api_list[0]['password'].encode('utf-8')).decode('utf-8'):
		if api_list[0]['password'] == request.form['password'] :
			session['logged_in'] = api_list[0]['username']
			return redirect(url_for('index'))
		return 'Invalide username/password!'
	else:
		flash("Invalid Authentication")

	return 'Invalid User!'

@app.route('/')
def home():
	if not session.get('logged_in'):
		return render_template('login.html')
	else:
		return render_template('index.html', session = session['username'])

@app.route('/index')
def index():
	return render_template('index.html')








#cookie = flask.request.cookies.get('my_cookie')
#@app.route('/set_cookie')
def cookie_insertion():
	redirect_to_main = redirect('/')
	response = current_app.make_response(redirect_to_main )
	response.set_cookie('cookie_name',value='values')
	return response

@app.route('/clear')
def clearsession():
	# Clear the session
	session.clear()
	# Redirect the user to the main page
	return redirect(url_for('main'))

@app.route('/addname')
def addname():
	if request.args.get('yourname'):
		session['name'] = request.args.get('yourname')
	# And then redirect the user to the main page
		return redirect(url_for('main'))
	else:
		return render_template('addname.html', session=session)

#@app.route('/')
def main():
	return render_template('main.html')

@app.route('/adduser')
def adduser():
	return render_template('adduser.html')

@app.route('/addtweets')
def addtweetjs():
	return render_template('addtweets.html')

@app.route("/api/v1/info")
def home_index():
    api_list=[]
    db = connection.cloud_native.apirelease
    for row in db.find():
        api_list.append(str(row))
    return jsonify({'api_version': api_list}), 200
	
@app.route('/api/v1/users', methods=['GET'])
def get_users():
	return list_users()
def list_users():
    api_list=[]
    db = connection.cloud_native.users
    for row in db.find():
        api_list.append(str(row))
    # print (api_list)
    return jsonify({'user_list': api_list})

@app.route('/api/v1/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
	return list_user(user_id)
def list_user(user_id):
    print (user_id)
    api_list=[]
    db = connection.cloud_native.users
    for i in db.find({'id':user_id}):
        api_list.append(str(i))

    if api_list == []:
        abort(404)
    return jsonify({'user_details':api_list})	

@app.route('/api/v1/users', methods=['POST'])
def create_user():
	if not request.json or not 'username' in request.json or not \
	'email' in request.json or not 'password' in request.json or not 'name'\
	in request.json:
		abort(400)
	user = {
		'username': request.json['username'],
		'email': request.json['email'],
		'name': request.json.get('name',""),
		'password': request.json['password'],
		'id': random.randint(1,1000)
	}
	return jsonify({'status': add_user(user)}), 201
	
def add_user(new_user):
    api_list=[]
    print (new_user)
    db = connection.cloud_native.users
    user = db.find({'$or':[{"username":new_user['username']} ,{"email":new_user['email']}]})
    for i in user:
        print (str(i))
        api_list.append(str(i))

    # print (api_list)
    if api_list == []:
    #    print(new_user)
       db.insert(new_user)
       return "Success"
    else :
       abort(409)

@app.route('/api/v1/users', methods=['DELETE'])
def delete_user():
	if not request.json or not 'username' in request.json:
		abort(400)
	user=request.json['username']
	return jsonify({'status': del_user(user)}), 200
def del_user(del_user):
    db = connection.cloud_native.users
    api_list=[]
    for i in db.find({'username':del_user}):
        api_list.append(str(i))

    if api_list == []:
        abort(404)
    else:
       db.remove({"username":del_user})
       return "Success"

@app.route('/api/v1/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
	user = {}
	if not request.json:
		abort(400)
	user['id']=user_id
	key_list = request.json.keys()
	for i in key_list:
		user[i] = request.json[i]
	print (user)
	return jsonify({'status': upd_user(user)}), 200
def upd_user(user):
    api_list=[]
    print (user)
    db_user = connection.cloud_native.users
    users = db_user.find_one({"id":user['id']})
    for i in users:
        api_list.append(str(i))
    if api_list == []:
       abort(409)
    else:
        db_user.update({'id':user['id']},{'$set': user}, upsert=False )
        return "Success"

@app.route('/api/v2/tweets', methods=['GET'])
def get_tweets():
	return list_tweets()
def list_tweets():

    api_list=[]
    db = connection.cloud_native.tweets
    for row in db.find():
        api_list.append(str(row))
    # print (api_list)
    return jsonify({'tweets_list': api_list})

@app.route('/api/v2/tweets', methods=['POST'])
def add_tweets():
	user_tweet = {}
	if not request.json or not 'username' in request.json or not \
	'body' in request.json:
		abort(400)
	user_tweet['username'] = request.json['username']
	user_tweet['body'] = request.json['body']
	user_tweet['created_at']=strftime("%Y-%m-%dT%H:%M:%SZ", gmtime())
	user_tweet['id'] = random.randint(1,1000)
	return  jsonify({'status': add_tweet(user_tweet)}), 201
def add_tweet(new_tweet):
    api_list=[]
    print (new_tweet)
    db_user = connection.cloud_native.users
    db_tweet = connection.cloud_native.tweets

    user = db_user.find({"username":new_tweet['username']})
    for i in user:
        api_list.append(str(i))
    if api_list == []:
       abort(404)
    else:
        db_tweet.insert(new_tweet)
        return "Success"

@app.route('/api/v2/tweets/<int:id>', methods=['GET'])
def get_tweet(id):
	return list_tweet(id)
def list_tweet(user_id):
	db = connection.cloud_native.tweets
	api_list=[]
	tweet = db.find({'id':user_id})
	for i in tweet:
		api_list.append(str(i))
	if api_list == []:
		abort(404)
	return jsonify({'tweet': api_list})

@app.errorhandler(UnboundLocalError)
def resource_not_found(error):
	return make_response(jsonify({'error':'Resource not found!'}))

@app.errorhandler(404)
def invalid_request(error):
	return make_response(jsonify({'error': 'Resource not found!'}), 400)

#@app.errorhandler(400)
def invalid_request(error):
	return make_response(jsonify({'error': 'Bad Request'}), 400)

if __name__ == '__main__':
	create_mongodatabase()
	app.run(host='0.0.0.0', port=5000, debug=True)
