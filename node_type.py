import commentjson

import linprog as lp

import utils

class NodeType:

	def __init__ (self, pretty_name):

		self . pretty_name = pretty_name

		name = utils . name (pretty_name)

		self . allocation_variable = lp . Variable (name + '_allocation')

	def add_constraints (self, constraints, consuming_recipes):

		constraints . append (self . allocation_variable >= 0)
		constraints . append (
			self . allocation_variable == sum (
				node_recipe . recipe . machine_count_variable
				for node_recipe in consuming_recipes
			)
		)

def load_node_types (node_types_file_name):

	with open (node_types_file_name, 'r') as node_types_file:

		node_types_data = commentjson . load (node_types_file)

	node_types = dict ()

	for node_type_pretty_name in node_types_data:

		node_types [node_type_pretty_name] = NodeType (node_type_pretty_name)

	return node_types

def get_node_type (node_type_name, node_types):

	if node_type_name not in node_types:

		raise ValueError (
			'\''
			+ node_type_name
			+ '\' does not name a valid node type.'
		)

	return node_types [node_type_name]
