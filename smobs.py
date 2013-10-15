import re
import sqlite3
from flask import Flask, render_template, request
from contextlib import closing

DATABASE = 'smobs.db'
DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
	return sqlite3.connect(app.config['DATABASE'])

def init_db():
	with closing(connect_db()) as db:
		with app.open_resource('schema.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()

@app.before_request():
def before_request():
	g.db = connect_db()

@app.teardown_request():
def teardown_request():
	db = getattr(g, 'db', None)
	if db is not None:
		db.close()

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
	data = request.form.get('smob')
	if not data:
		return render_template('submit_error.html')
	
	location = ""
	out = "<pre>"
	r = re.compile("^You get (.*) from the corpse of (.*)\.$")
	for line in data.split('\n'):
		m = re.match("You get (.*) from the corpse of (.*)\.", line.strip())
		if m:
			out += "smob: " + m.group(2) + " item: " + m.group(1) + "\n"
		out += line + "\n"
		
		
	
	out += "</pre>"
	return out
	
	#return request.form['smob']
	

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=1234)
