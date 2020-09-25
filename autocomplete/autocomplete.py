#downloaded libc++-7-dev, libc++-dev, libc++abi-7-dev
#already had libc++1, libc++1-7
#pip install wheel
from tree_sitter import Language, Parser
from helper import *
from lookup import *
import sys

#build the language library
Language.build_library(
 	'build/my-languages.so',
 	[
 		'vendor/tree-sitter-python'
 	]
)

PY_LANGUAGE = Language('build/my-languages.so', 'python')

#build the parser for python
parser = Parser()
parser.set_language(PY_LANGUAGE)

#global variables
INPUT_FILE = ""
INPUT_INDEX = -1
SYNTAX_TREE = None

if __name__ == "__main__":
	#validate input as correctInput
	INPUT_FILE, INPUT_INDEX = validateInput()

	#add placeholder so parser doesn't throw an error and
	#correctly parses the tree
	filestr =""
	file = open(INPUT_FILE, "r")
	filestr = file.read()
	filestr = filestr[:INPUT_INDEX] + "placeholder" + filestr[INPUT_INDEX:]
	file.close()
	#print(filestr)
	
	#use the parser to parse the file into a syntax tree
	filebyte = bytes(filestr, "utf8")
	SYNTAX_TREE = parser.parse(filebyte)
	root = SYNTAX_TREE.root_node
	
	#find the missing variable node and return a cursor pointing to it
	cursor = findSpot(SYNTAX_TREE, INPUT_INDEX)	
	
	#store the identifier associated with the missing variable node
	word = (filebyte[cursor.node.start_byte:cursor.node.end_byte]).decode("utf-8")
	
	#check if the missing variable is a special case
	special_case = findSpecialCase(cursor, INPUT_INDEX)
	#print(special_case)
	
	#for each special case, call a special lookup function
	#return the list of possible identifiers
	words = []
	if(special_case == "attr"):
		words = attrLookUp(root, INPUT_INDEX, filebyte)
	elif(special_case == "for"):
		words = forLookUp(root, INPUT_INDEX, filebyte)
	elif(special_case == "sub"):
		words = subLookUp(root, INPUT_INDEX, filebyte)
	elif(special_case == "dict"):
		words = dictLookUp(root, INPUT_INDEX, filebyte)
	elif(special_case == "set"):
		words = setLookUp(root, INPUT_INDEX, filebyte)
	else:
		words = normalLookUp(root, INPUT_INDEX, filebyte)
	
	#remove placeholder from the missing variable identider
	# so we can get the original word that was part of the identifier
	word = word.replace('placeholder', '')
	
	#for each identifier in the list, if there was part of the
	#missing variable given, only print identifiers that start with the same
	#words as the missing variable. If there is no part of the missing variable
	#given, print the entire list
	for w in words:
		if(word != ''):
			if w.startswith(word):
				print(w)
		else:
			print(w) 