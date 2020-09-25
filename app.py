from flask import Flask, render_template
import os

app = Flask(__name__)

@app.route('/', methods=['GET'])
def my_route_page_function():
	os.system('cmd /c "ls"')
	return render_template('home.html')
