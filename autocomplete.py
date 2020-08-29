#downloaded libc++-7-dev, libc++-dev, libc++abi-7-dev
#already had libc++1, libc++1-7
#pip install wheel
from flask import Flask
from tree_sitter import Language, Parser

app = Flask(__name__)

#Language.build_library(
# 	'build/my-languages.so',
# 	[
# 		'vendor/tree-sitter-python'
# 	]
#)

# PY_LANGUAGE = Language('build/my-languages.so', 'python')
# parser = Parser()
# parser.set_language(PY_LANGUAGE)

@app.route("/")
def hello():
	return "Hello World!"
