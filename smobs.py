import re
import psycopg2
from flask import Flask, render_template, request, g
from contextlib import closing
from datetime import datetime
import config

app = Flask(__name__)
app.config.from_object('config')

def connect_db():
	return psycopg2.connect(app.config['DATABASE'])

@app.before_request
def before_request():
	g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
	db = getattr(g, 'db', None)
	if db is not None:
		db.close()

@app.route('/submit', methods=['GET', 'POST'])
def submit():
	if request.method == 'GET':
		return render_template('submit.html')
	
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
		return render_template('submit_check.html', smob=smob, items=items, data=data)
	if request.form.get('button') == "submit":
		cur = g.db.cursor()
		
		cur.execute('select smobid from smob where name = %s', (smob,))
		if cur.rowcount is 0:
			cur.execute('insert into smob (name) values (%s) returning smobid', (smob,))
		smobid = cur.fetchone()[0]
		
		timestamp = datetime.now()
		cur.execute('insert into load (smobid, who, date) values (%s, %s, %s) returning loadid', (smobid, 'racsul', timestamp))
		loadid = cur.fetchone()[0]
		
		for item in items:
			cur.execute('select itemid from item where name = %s', (item[0],))
			if cur.rowcount is 0:
				cur.execute('insert into item (name) values (%s) returning itemid', (item[0],))
			itemid = cur.fetchone()[0]
			cur.execute('insert into load_item (loadid, itemid, quantity) values (%s, %s, %s)', (loadid, itemid, item[1]))
		
		g.db.commit()
		
		return render_template('submitted.html')
	return render_template('submit_error.html')

@app.route('/smob/<int:smobid>')
def smob(smobid):
	cur = g.db.cursor()
	cur.execute('select * from smob where smobid = %s', (smobid,))
	smob = cur.fetchone()
	cur.execute('select loadid from load where smobid = %s', (smobid,))
	loads = cur.fetchall()
	kills = len(loads)
	items = {}
	for load in loads:
		cur.execute('select * from load_item where loadid = %s', (load,))
		for row in cur:
			if not items.get(int(row[1])):
				items[int(row[1])] = 1
			else:
				items[int(row[1])] += 1
	
	newitems = {}
	for item in items.items():
		cur.execute('select name from item where itemid = %s', (item[0],))
		row = cur.fetchone()
		newitems[row[0]] = float(item[1]) / float(kills) * 100
		
	return render_template('smob.html', smob=smob, kills=kills, items=newitems.items())

@app.route('/')
def index():
	cur = g.db.cursor()
	cur.execute('select * from smob order by name')
	return render_template('index.html', smobs=cur.fetchall())

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=1234)
