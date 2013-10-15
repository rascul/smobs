import re
import sqlite3
from flask import Flask, render_template, request, g
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

@app.before_request
def before_request():
	g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
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
	
	smob = ""
	items = []
	r = re.compile("^(smob: (.*)|(You get (.*) from (the corpse of |)(.*)\.)|You get (.*)\.)$")
	
	for line in data.split('\n'):
		m = r.match(line.strip())
		if m:
			if not smob and m.group(2):
				smob = m.group(2)
			elif not smob and m.group(6):
				smob = m.group(6)
			
			match = False
			i = 0
			itemmatch = m.group(4) or m.group(7)
			for item in items:
				if item[0] == itemmatch:
					items[i] = item[0], item[1] + 1
					match = True
				i += 1
			if not match and itemmatch:
				items.append((itemmatch, 1))
	
	if request.form.get('button') == "recheck":
		return render_template('submit.html', smob=smob, items=items, data=data)
	if request.form.get('button') == "submit":
		return render_template('submitted.html')
	return render_template('submit_error.html')

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=1234)
