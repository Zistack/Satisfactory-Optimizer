import commentjson

def load_node_types (node_types_file_name):

	with open (node_types_file_name, 'r') as node_types_file:

		node_types_data = commentjson . load (node_types_file)

	return set (node_types_data)

def get_node_type (node_type_name, node_types):

	if node_type_name not in node_types:

		raise ValueError (
			'\''
			+ node_type_name
			+ '\' does not name a valid node type.'
		)

	return node_type_name
