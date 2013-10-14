from flask import Flask, render_template, request

SMOB_FILE = 'static/smobs.txt'

DEBUG = False

app = Flask(__name__)
app.config.from_object(__name__)

@app.route("/", methods=['POST', 'GET'])
def index():
	template = 'index.html'
	if request.method == 'POST' and request.form['smob']:
		with open(SMOB_FILE, 'a') as f:
			f.write(request.form['smob'] + '\n\n')
		template = 'submitted.html'		
	return render_template(template)

if __name__ == '__main__':
	app.run(host='0.0.0.0', port='1234')
