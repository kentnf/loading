#!/usr/bin/python3

import copy

'''
document is a dict, it includes both dict and list
'''

class Document():

	def __init__(self, doc):
		self.doc = doc
		#self.name = doc['name'] if 'name' in doc else self.name = ''
		#self.type = doc['type'] if 'type' in doc else self.type = ''
		#self._id = doc['_id'] if '_id'  in doc else self._id = ''

	'''
	check_path -- check if the path is true, return the value of the path
	'''
	def check_path(self, path):
		if (isinstance(path, list)):
			value = copy.deepcopy(self)
			for p in path:
				test(self.doc[p])
			return(value)
		else:
			print('[ERR] the path is not list')
			print(path)
			sys.exit() 
	'''
	add -- add new attribute to doc
	'''
	def add(self, path, add_doc):
		document = copy.deepcopy(self.doc)
		self.add_document(document, path, add_doc)
		self.doc = document

	def add_document(self, document, path, add_doc):
		key = path.pop(0)

		# add the k,v of the path
		if (len(path) == 0):

			if (key in document):
				if (isinstance(document[key], list)):
					document[key].append(add_doc)
				else:
					print('[ERR]value exist for key: %s, use update method.' % key)
			else:
				document[key] = add_doc
			return

		if (isinstance(document[key], dict) or isinstance(document[key], list)):
			self.add_document(document[key], path, add_doc)
		else:
			print('[ERR]value is char for key: %s, use update method.' % key)

	'''
	remove -- remove attribute from doc
	'''
	def remove(self, path):
		document = copy.deepcopy(self.doc)
		self.remove_document(document, path)
		self.doc = document

	def remove_document(self, document, path):
		key = path.pop(0)

		# delete the k,v of the path
		if (len(path) == 0):
			del document[key]
			return

		if (isinstance(document[key], dict) or isinstance(document[key], list)):
			self.remove_document(document[key], path)
		else:
			print("[ERR]branch end: %s, check path" % key)

	'''
	update -- update attribute of doc
	'''
	def update(self, path, value):
		document = copy.deepcopy(self.doc)
		self.update_document(document, path, value)
		self.doc = document

	def update_document(self, document, path, value):
		key = path.pop(0)

		# update the value of the path
		if (len(path) == 0):
			document[key] = value
			return

		# go to next path
		if (isinstance(document[key], dict) or isinstance(document[key], list)):
			self.update_document(document[key], path, value)
		else:
			print("[ERR]branch end: %s, check path" % key)
	'''
	update_all -- update attribute of doc for all searched key
	'''
	def update_all(self, keys, value):
		document = copy.deepcopy(self.doc)


	# below method only works for sequence features: gene, mRNA	
	'''
	get_length -- get length of feature
	'''
	def get_length(self):
		pass

	'''
	get_residues --
	'''
	def get_residues(self):
		pass

'''
Test code
'''

if __name__ == "__main__":

	dict1 = {'dk1': 'dv1', 'dk2': 'dv2'}
	dict2 = {'dka': 'dva', 'dkb': dict1}
	dict3 = {'xx': 'yy', 'zz': dict2 }
	doc1 = { 'k1': dict3, 'name': 'document1', 'type': 'gene'}
	
	d1 = Document(doc1)
	d1.doc_print()
	path = ['k1', 'zz', 'dkb', 'dk2', 'new']
	d1.remove(path)
	d1.doc_print()



