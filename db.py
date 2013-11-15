# Copyright (C) 2013 Ray Schulz <rascul3@gmail.com>
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING file for more details.

import re
import psycopg2
from flask import Flask, render_template, request, g, redirect
#from contextlib import closing
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

@app.route('/smobs/submit', methods=['GET', 'POST'])
def submit():
	if request.method == 'GET':
		return render_template('submit.html')
	
	data = request.form.get('smob')
	if not data:
		return render_template('submit_error.html')
	
	smob = ""
	items = []
	r = re.compile("^(smob: (.*)|((You get|.* gets) (.*) from (the corpse of |)(.*)\.)|(You get|.* gets) (.*)\.)$")
	
	for line in data.split('\n'):
		m = r.match(line.strip())
		if m:
			if not smob and m.group(2):
				smob = m.group(2)
			elif not smob and m.group(7):
				smob = m.group(7)
			
			match = False
			i = 0
			itemmatch = m.group(5) or m.group(9)
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

@app.route('/smobs/edit/submit', methods=['POST'])
def smob_edit_submit():
	cur = g.db.cursor()
	smobid = request.form.get('smobid')
	
	cur.execute('select smobid, name, stab, channel, shortname, location, pick, search from smob where smobid = %s', (smobid,))
	oldsmob = cur.fetchone()
	
	stab = oldsmob[2]
	channel = oldsmob[3]
	shortname = oldsmob[4]
	location = oldsmob[5]
	pick = oldsmob[6]
	search = oldsmob[7]
	
	if request.form.get('stab') == 'yes':
		stab = True
	elif request.form.get('stab') == 'no':
		stab = False
	elif request.form.get('stab') == 'unknown':
		stab = None
	
	if request.form.get('channel') is not oldsmob[3]:
		channel = request.form.get('channel')
	if request.form.get('shortname') is not oldsmob[4]:
		shortname = request.form.get('shortname')
	if request.form.get('location') is not oldsmob[5]:
		location = request.form.get('location')
	if request.form.get('pick') is not oldsmob[6]:
		pick = request.form.get('pick').rstrip('%')
	if request.form.get('search') is not oldsmob[7]:
		search = request.form.get('search').rstrip('%')
	
	if pick == '':
		pick = None
	if search == '':
		search = None
	
	cur.execute('update smob set stab = %s, channel = %s, shortname = %s, location = %s, pick = %s, search = %s where smobid = %s', (stab, channel, shortname, location, pick, search, smobid))
	
	g.db.commit()
	
	return redirect('/smobs/' + smobid)

@app.route('/smobs/edit/<int:smobid>')
def smob_edit(smobid):
	cur = g.db.cursor()
	cur.execute('select * from smob where smobid = %s', (smobid,))
	smob = cur.fetchone()
	cur.execute('select loadid from load where smobid = %s', (smobid,))
	loads = cur.fetchall()
	
	title = smob[1]
	if smob[4]:
		title += " (" + smob[4] + ")"
	return render_template('smob_edit.html', title=title, smob=smob)

@app.route('/smobs/<int:smobid>')
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
	
	title = smob[1]
	if smob[4]:
		title += " (" + smob[4] + ")"
	return render_template('smob.html', title=title, smob=smob, kills=kills, items=newitems.items(), smobid=smobid)

@app.route('/smobs')
def smobs():
	cur = g.db.cursor()
	cur.execute('select * from smob order by name')
	smobs = cur.fetchall()
	kills = {}
	for smob in smobs:
		cur.execute('select * from load where smobid = %s', (smob[0],))
		kills[smob[0]] = len(cur.fetchall())
	return render_template('smobs.html', smobs=smobs, kills=kills, title='smobs')

@app.route('/eq/<int:eqid>')
def eq_item(eqid):
	cur = g.db.cursor()
	cur.execute('select type from item where itemid = %s', (eqid,))
	itemtype = cur.fetchone()[0]
	query = ''
	if itemtype == 'armor':
		query = 'select name, itemid, type, db, pb, moves, abs, weight, rent, sheath from armor where itemid = %s'
	elif itemtype == 'weapon':
		query = 'select name, itemid, type, ob, pb, weight, hands, rent from weapon where itemid = %s'
	elif itemtype == 'trink':
		query = 'select name, itemid, type, db, pb, moves, weight, rent, sheath from trink where itemid = %s'
	cur.execute(query, (eqid,))
	item = cur.fetchone()
	desc = cur.description
	
	cur.execute('select distinct smob.smobid, smob.name from smob, load, load_item where smob.smobid = load.smobid and load.loadid = load_item.loadid and itemid = %s', (eqid,))
	smobs = cur.fetchall()
	
	return render_template('eq_item.html', title=item[0], item=item, desc=desc, smobs=smobs)

@app.route('/eq/<eqtype>/<eqsubtype>')
def eq_type_subtype(eqtype, eqsubtype):
	cur = g.db.cursor()
	query = ''
	if eqtype == 'armor':
		query = 'select name, itemid, type, db, pb, moves, abs, weight, rent, sheath from armor where type = %s'
	elif eqtype == 'weapon':
		query = 'select name, itemid, type, ob, pb, weight, hands, rent from weapon where type = %s'
	elif eqtype == 'trink':
		query = 'select name, itemid, type, db, pb, moves, weight, rent, sheath from trink where type = %s'
	else:
		return render_template('eq_unknown.html')
	cur.execute(query, (eqsubtype,))
	items = cur.fetchall()
	descs = cur.description
	return render_template('eq.html', title=eqtype, items=items, descs=descs)

@app.route('/eq/<eqtype>')
def eq_type(eqtype):
	cur = g.db.cursor()
	query = ''
	if eqtype == 'armor':
		query = 'select name, itemid, type, db, pb, moves, abs, weight, rent, sheath from armor'
	elif eqtype == 'weapon':
		query = 'select name, itemid, type, ob, pb, weight, hands, rent from weapon'
	elif eqtype == 'trink':
		query = 'select name, itemid, type, db, pb, moves, weight, rent, sheath from trink'
	else:
		return render_template('eq_unknown.html')
	cur.execute(query)
	items = cur.fetchall()
	descs = cur.description
	return render_template('eq.html', title=eqtype, items=items, descs=descs)

@app.route('/eq')
def eq():
	cur = g.db.cursor()
	cur.execute('select name, itemid, type from item')
	items = cur.fetchall()
	descs = cur.description
	return render_template('eq.html', title='equipment', items=items, descs=descs)

@app.route('/quests')
def quests():
	cur = g.db.cursor()
	cur.execute('select distinct locationid, location from quest_location')
	locations = cur.fetchall()
	return render_template('quests.html', title='quests', locations=locations)

@app.route('/')
def index():
	return render_template('index.html', title='wotmud db')

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=1234)
