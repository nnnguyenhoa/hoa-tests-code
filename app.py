from flask import Flask, render_template, request
import subprocess
app = Flask(__name__)

@app.route('/', methods=['post', 'get'])
def home():
	if request.method == 'POST':
		program = request.form.get('program')
		index = request.form.get('index')
		with open('input.py', 'w+') as f:
			f.write(program)
			f.close()
		result = subprocess.run(['python', 'autocomplete/autocomplete.py', 'input.py', index], stdout=subprocess.PIPE)
		result_string = (result.stdout).decode('utf8')
		identifiers = result_string.split("\n")
		identifiers.remove("")
		return render_template('home.html', list=identifiers)
	return render_template('home.html')
