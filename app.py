from flask import Flask, render_template

app = Flask(__name__)

@app.route('/', methods=['GET'])
def my_route_page_function():
	return render_template('home.html')
