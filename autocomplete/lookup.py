from helper import *

# no special case lookup
def normalLookUp(node, input_index, filebyte):
	words = set()
	queue = []

	#special case identifiers and scope to ignore
	#you dont need to look for identifiers outside 
	#of the scope of where the missing variable is
	special_cases = {"class_definition", "function_definition", "keyword_argument", "attribute", "call", "import_statement", "import_from_statement", "block"}
	
	#find all identifiers using breadth first search
	#to traverse the trees
	queue.append(node)
	curr_node = node
	while(len(queue) != 0):
		for child in curr_node.children:

			#break at leaf whose scope contains input index
			if (len(child.children) == 0 and
			child.start_byte <= input_index < child.end_byte):
				return words

			#if there is an identifier before the input index
			#add that identifier
			if(child.start_byte < input_index):
				if(child.type == "identifier"):
					word = (filebyte[child.start_byte:child.end_byte]).decode("utf-8")
					words.add(word)

				#if the node type is a special case and the scope is
				#outside of input index, only add function and class
				#definition identifiers. Skip adding the subtree itself
				#into the search queue
				if(child.end_byte < input_index and 
					child.type in special_cases):
					if(child.type == "function_definition" or child.type == "class_definition"):
						for child_node in child.children:
							if(child_node.type == "identifier"):
								word = (filebyte[child_node.start_byte:child_node.end_byte]).decode("utf-8")
								if(word != "__init__"):
									words.add(word)
					continue	
				queue.append(child)
		curr_node = queue.pop(0)
	return words

# look for objects of an attribute variable
# can be an import, class identifier, or self
# self is only an option if the input index
# exists within the scope of a class definition
def objectSearch(node, input_index, filebyte):

	#finding all import variables
	imports = set()
	for child in node.children:
		if(child.type == "import_statement" or child.type == "import_from_statement"):
			for index in range(len(child.children)):
				granchild = child.children[index]
				if(granchild.type == "dotted_name" 
					and index == len(child.children) - 1):
					word = (filebyte[granchild.start_byte:granchild.end_byte]).decode("utf-8")
					imports.add(word)

	#using breadth first search to traverse the trees	
	words = set()
	special_cases = {"class_definition", "function_definition", "keyword_argument", "call", "import_statement", "import_from_statement", "block"}
	queue = []
	queue.append(node)
	curr_node = node
	while(len(queue) != 0):

		#break at leaf whose scope contains input index
		for child in curr_node.children:
			if (len(child.children) == 0 and
			child.start_byte <= input_index < child.end_byte):
				return words
			
			#if the input index is within the scope of a
			#class definition, add self and break out of the search
			#to look into that class definition
			# otherwise, collect all the attributes
			if(child.type == "class_definition"):
				if(child.start_byte <= input_index < child.end_byte):
					words = set()
					words.add("self")
					queue = []
					curr_node = child
					queue.append(curr_node)
					break
				else:
					continue
			
			if(child.end_byte < input_index and child.type in special_cases):
				continue
			#if the current node is an attribute, add the object part
			#make sure it's not our placeholder
			if(child.type == "attribute"):
				granchild = child.children[0]
				if not (child.start_byte <= input_index < child.end_byte):
					word = (filebyte[granchild.start_byte:granchild.end_byte]).decode("utf-8")
					words.add(word)
			
			#if the current node is an identifier, add the identifier
			#make sure it's not our placeholder
			#identifiers are added bc the identifier could be an object
			#that has never had one of its attribute accessed
			if(child.type == "identifier"):
				if not (child.start_byte <= input_index < child.end_byte):
					word = (filebyte[child.start_byte:child.end_byte]).decode("utf-8")
					words.add(word)
			queue.append(child)
		if(len(queue) != 0):
			curr_node = queue.pop(0)
	
	#this is a continuation of the 'breaking out of the BFS if
	#the input_index is found inside the scope of a class
	#definition' scenario. This part would never happen otherwise because
	#the only time the previous loop will break is if they reached
	#the leaf containing the input index and have collected all
	#the words or it broke when it realized that the input_index is 
	#found inside the scope of a class definition.
	#if it breaks the while loop because the queue is empty, it
	#would never call this because I added the class_definition
	#node that was the parent of the missing variable node before
	#breaking so the queue if this scenario happens can never be 0
	if(curr_node.type == "class_definition" and len(queue) > 0):

		#using BFS again to traverse the tree
		while(len(queue) != 0):

			#break at leaf whose scope contains input index
			for child in curr_node.children:
				if (len(child.children) == 0 and
			child.start_byte <= input_index < child.end_byte):
					return words
				
				
				if(child.end_byte < input_index and child.type in special_cases):
					continue

				#if the current node is an attribute, add the object part
				#make sure it's not our placeholder
				if(child.type == "attribute"):
					granchild = child.children[0]
					if not (child.start_byte <= input_index < child.end_byte):
						word = (filebyte[granchild.start_byte:granchild.end_byte]).decode("utf-8")
						words.add(word)

				#if the current node is an identifier, add the identifier
				#make sure it's not our placeholder
				if(child.type == "identifier"):
					if not (child.start_byte <= input_index < child.end_byte):
						word = (filebyte[child.start_byte:child.end_byte]).decode("utf-8")
						words.add(word)
				queue.append(child)
			curr_node = queue.pop(0)
	words.update(imports)
	return words

#look for attributes, including functions
#if object is self, add all attributes in
#class definition including functions
#if object is not self, just add
#all the attribute parts of object variables
def attrSearch(node, input_index, filebyte):
	
	#using BFS
	words = set()
	special_cases = {"class_definition", "function_definition", "keyword_argument", "call", "import_statement", "import_from_statement", "block"}
	queue = []
	queue.append(node)
	curr_node = node
	
	#check if the object identifier is self.
	cursor = findSpot(node, input_index)
	cursor.goto_parent()
	obj_node = cursor.node.children[0]
	obj_name = (filebyte[obj_node.start_byte:obj_node.end_byte]).decode("utf-8")
	
	#if the object identifier is self, find the
	#class definition node whose scope contains
	#the input index
	if(obj_name == "self"):
		while(len(queue) != 0):
			for child in curr_node.children:
				if(child.start_byte < input_index < child.end_byte):
					if(child.type == "class_definition"):
						curr_node = child
						queue = []
						break
					queue.append(child)
		
		#traverse through the class definition tree found
		queue.append(curr_node)
		while(len(queue) != 0):
			for child in curr_node.children:
				
				#add all the function calls that arent init
				#but dont add the function tree itself in
				#because outside of init, all the variables
				#inside the function node aren't in the scope
				#of the missing variable
				if(child.type == "function_definition"):
					granchild = child.children[1]
					name = (filebyte[granchild.start_byte:granchild.end_byte]).decode("utf-8")
					if(name != "__init__"):
						words.add(name)
						continue
				
				#if an attribute variable has been found, add the
				#attribute of the object
				#Make sure it isnt the placeholder
				if(child.type == "attribute"):
					granchild = child.children[2]
					name =(filebyte[granchild.start_byte:granchild.end_byte]).decode("utf-8")
					if not (child.start_byte <= input_index < child.end_byte):
						word = (filebyte[granchild.start_byte:granchild.end_byte]).decode("utf-8")
						words.add(word)

				queue.append(child)
			curr_node = queue.pop(0)
	#if the missing attribute variable is not within a class definition
	#look for all
	else:

		#BFS to traverse again
		while(len(queue) != 0):

			#break if child is leaf and input index is
			#within the scope
			for child in curr_node.children:
				if (len(child.children) == 0 and
			child.start_byte <= input_index < child.end_byte):
					return words

				#add the attribute part of object attribute variables
				if(child.type == "attribute"):
					granchild = child.children[2]
					if not (child.start_byte <= input_index < child.end_byte):
						word = (filebyte[granchild.start_byte:granchild.end_byte]).decode("utf-8")
						words.add(word)

				#do not traverse through subtrees with
				#identifiers outside the scope of the
				#input index
				if(child.end_byte < input_index and child.type in special_cases):
					continue
				queue.append(child)
			curr_node = queue.pop(0)
	return words

#look up for special case: attribute
#attributes are variables that are objects with attributes
#call objectSearch if the missing variable is an object
#call attribute search if the missing variable is missing 
def attrLookUp(node, input_index, filebyte):
	words = set()
	
	#check whether the missing variable is an object or attribute
	cursor = findSpot(node, input_index)
	cursor.goto_next_sibling()
	node_type = cursor.node.type
	if(node_type == "."):
		words = objectSearch(node, input_index, filebyte)
	else:
		words = attrSearch(node, input_index, filebyte)
	return words

#look up for special case : for loop
#the variable that is being looped through
#must be a string or collection such as dictionary,
#set, or list
def forLookUp(node, input_index, filebyte):
	
	#BFS again to traverse tree
	words = set()
	queue = []
	special_cases = {"class_definition", "function_definition", "subscript", "attribute", "call", "import_statement", "import_from_statement", "block"}
	queue.append(node)
	curr_node = node

	while(len(queue) != 0):
		for child in curr_node.children:
			
			#break if at leaf node and input index is in node's scope
			if (len(child.children) == 0 and
			child.start_byte <= input_index < child.end_byte):
				return words
			
			#if a list, dictionary, set, or string existed before
			#the input index, add its identifier into the list
			if(child.start_byte < input_index):
				if(child.type == "list" 
					or child.type == "dictionary"
					or child.type == "set"
					or child.type == "string"):
					cursor = findSpot(node, child.start_byte)
					while cursor.node.type != "assignment":
						cursor.goto_parent()
					granchild = cursor.node.children[0]
					word = (filebyte[granchild.start_byte:granchild.end_byte]).decode("utf-8")
					words.add(word)
				
				#if the current node is a special case and its scope
				#does not contain the input index, ignore that node
				if(child.end_byte < input_index and 
					child.type in special_cases):
					continue	
				queue.append(child)
		curr_node = queue.pop(0)
	return words

#look up for special case: subscript
#a subscript is a variable that is accessing
# an element in a collection or string
def subLookUp(node, input_index, filebyte):
	
	#check if the missing variable is a subscript
	#or a collection
	cursor = findSpot(node, input_index)
	cursor.goto_next_sibling()
	
	#if it is a subscript, look for every identifier
	#that is not a collection or string and not the
	#name of the collection that the subscript is
	#a part of.
	if(cursor.node.type == "]"):
		cursor.goto_parent()
		child = cursor.node.children[0]
		word = (filebyte[child.start_byte:child.end_byte]).decode("utf-8")
		return lookUpExclude(node, input_index, filebyte, word)
	
	#if we reach here, then the collection part of
	#the subscript is missing
	#BFS to traverse through tree
	words = set()
	
	#add all collections and strings identifiers found
	#for loop does this, since the forLookUp returns a
	#list of collections or strings 
	words = forLookUp(node, input_index, filebyte)
	
	#BFS to traverse the tree
	queue = []
	special_cases = {"class_definition", "function_definition", "keyword_argument","attribute", "call", "import_statement", "import_from_statement", "block"}
	queue.append(node)
	curr_node = node
	while(len(queue) != 0):
		for child in curr_node.children:
			
			#break if leaf and input index in scope
			if (len(child.children) == 0 and
			child.start_byte <= input_index < child.end_byte):
				return words

			#add all subscript collection variables
			if(child.start_byte < input_index):
				if(child.type == "subscript"):
					granchild = child.children[0]
					word = (filebyte[granchild.start_byte:granchild.end_byte]).decode("utf-8")
					words.add(word)
				
				#skip special cases outside of scope
				#input index is in
				if(child.end_byte < input_index and 
					child.type in special_cases):
					continue	
				queue.append(child)
		curr_node = queue.pop(0)
	return words

# Lookup for identifiers excluding exclude input and collection identifiers if specified
def lookUpExclude(node, input_index, filebyte, exclude, no_collections=True):
	
	#BFS to traverse through trees
	words = set()
	queue = []
	special_cases = {"class_definition", "function_definition", "keyword_argument", "attribute", "call", "import_statement", "import_from_statement", "block"}
	
	#collection types to avoid if specified
	collections = {"list", "set", "dictionary"}
	queue.append(node)
	curr_node = node
	while(len(queue) != 0):
		for child in curr_node.children:
			
			#break if leaf and input index in scope
			if (len(child.children) == 0 and
			child.start_byte <= input_index < child.end_byte):
				return words
			
			#add all identifiers found that aren't in exclude
			if(child.start_byte < input_index):
				if(child.type == "identifier"):
					word = (filebyte[child.start_byte:child.end_byte]).decode("utf-8")
					if(word not in exclude):
						words.add(word)

				#skip special case subtrees if input index
				#not in scope
				if(child.end_byte < input_index):
					if(child.type in special_cases):
						continue
					
					#if specified, skip collection identifiers
					if no_collections:
						colCheck = False
						if child.type == "assignment":
							exp_list = child.children[2]
							for item in exp_list.children:
								if item.type in collections:
									colCheck = True
									break			
						if colCheck == True:
							continue
				queue.append(child)
		curr_node = queue.pop(0)
	return words

#lookup for special case = dictionary values
#for key, exclude all other keys
#for values, exclude dictionary identifier
def dictLookUp(node, input_index, filebyte):
	#check if a key is missing or a value is missing	
	keys = []
	cursor = findSpot(node, input_index)
	cursor.goto_next_sibling()
	key_bool = False

	#key is missing if true
	if(cursor.node.type == ":"):
		key_bool = True
	
	#find identifier associated with dictionary if one exists
	identifier = ""
	while cursor.node.type != "assignment" or cursor.node.typ != "module":
		cursor.goto_parent()
		identifier_node = cursor.node.children[0]
		identifier =  (filebyte[identifier_node.start_byte:identifier_node.end_byte]).decode("utf-8")
	
	#if we are looking for values, collections are okay but exclude
	#dictionary identifer
	if(key_bool == False):
		return lookUpExclude(node, input_index, filebyte, identifier, no_collections=False)
	
	#find the dictionary node
	cursor = findSpot(node, input_index)
	while cursor.node.type != "dictionary" or cursor.node.typ != "module":
		cursor.goto_parent()
	dictionary = cursor.node
	
	#add all the keys of the all the pairs to the keys list
	for pairs in dictionary.children:
		if(len(pairs.children) > 0):
			child = pairs.children[0]
			key = (filebyte[child.start_byte:child.end_byte]).decode("utf-8")
			keys.append(key)
	keys.append(identifier)
	#return all non-collection identifiers that are also not keys
	return lookUpExclude(node, input_index, filebyte, keys)

#lookup special case - set values
#exclude values already in set
def setLookUp(node, input_index, filebyte):
	
	#find set identifier
	keys = []
	cursor = findSpot(node, input_index)
	while cursor.node.type != "assignment" or cursor.node.type != "module":
		cursor.goto_parent()
	identifier_node = cursor.node.children[0]
	identifier =  (filebyte[identifier_node.start_byte:identifier_node.end_byte]).decode("utf-8")
	keys.append(identifier)
	
	#find set node
	cursor = findSpot(node, input_index)
	while cursor.node.type != "set" or cursor.node.type != "module":
		cursor.goto_parent()
	set_node = cursor.node
	
	#add all values already in set into keys
	for child in set_node.children:
		if(child.type == "identifier"):
			key = (filebyte[child.start_byte:child.end_byte]).decode("utf-8")
			keys.append(key)

		#return all non collection identifiers that aren't already in set
	return lookUpExclude(node, input_index, filebyte, keys)