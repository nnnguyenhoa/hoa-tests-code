import sys

#validate that the input so that it fits the requirements
#of the program: needs a file to input and the index of
def validateInput():

	if(len(sys.argv) < 2):
		sys.exit("Need file and index in file to complete")
	if(not sys.argv[1] or type(sys.argv[1]) != str):
		sys.exit("Need name of file to complete")
	else:
		INPUT_FILE = sys.argv[1]
	if(not sys.argv[2] or sys.argv[2].isdigit() != True):
		sys.exit("Need a number index in file of where to complete")
	else:
		INPUT_INDEX = int(sys.argv[2])
	return [INPUT_FILE, INPUT_INDEX]

#function to find the spot where the missing variable is
#return the cursor to that spot
def findSpot(tree, input_index):
	cursor = tree.walk()
	
	#iterate through the tree while the cursor
	#isn't False
	while cursor != False:
		start = cursor.node.start_byte
		end = cursor.node.end_byte

		#if the current node is a lead and its position scope
		#is in between the index of the input, then the
		#node is found
		if(len(cursor.node.children) == 0 and
			start <= input_index < end):
			break
		
		#if the input index is within the current node's
		#position scope, then the current node is a parent
		#of the missing variable node so go to the child of
		#that node
		if(start <= input_index < end):
			cursor.goto_first_child()

		#if the end position scope is smaller than the input
		#index, then move onto the next node because the missing
		#variable node can not exist in the subtree of the current
		#this node
		elif(input_index >= end):
			cursor.goto_next_sibling()
	return cursor

#a function that traverses down the tree of the current spot
#and sees if there is a special case within the subtrees
def lookDownSpecial(cursor, input_index):
	start_node = cursor.node
	
	#using breadth first search to traverse through the tree
	queue = []
	queue.append(start_node)
	while(len(queue) > 0):
		curr_children = start_node.children
		
		#iterate through the children of each node to see if
		#the subscript special case exists
		for child in curr_children:
			curr_type = child.type
			if curr_type == "subscript":
				return "sub"
			queue.append(child)
		start_node = queue.pop(0)
	return False

#function to find is the missing variable requires
#a special lookup function
def findSpecialCase(cursor, input_index):
	
	#look at the parents of the missing variable node
	#for a special case
	cursor.goto_parent()

	if(cursor.node.type == "parenthesized_expression"
		or cursor.node.type == "expression_list"):
		cursor.goto_parent()
	
	parent_type = cursor.node.type

	if(parent_type == "attribute"):
		return "attr"
	elif(parent_type == "for_statement"):
		return "for"
	elif(parent_type == "subscript"):
		return "sub"
	elif(parent_type == "set"):
		return "set"
	elif(parent_type == "pair"):
		return "dict"
	else:

		#look into the tree for a special case
		findSpot(cursor.node, input_index)
		return lookDownSpecial(cursor, input_index)