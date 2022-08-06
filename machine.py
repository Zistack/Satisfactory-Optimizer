import commentjson

import linprog as lp

import utils

class Machine:

	def __init__ (self, pretty_name):

		self . pretty_name = pretty_name

		name = utils . name (pretty_name)

		self . count_variable = lp . Variable (name + '_count')

	def __count (self, supported_recipes):

		return sum (
			supported_recipe . recipe . machine_count_variable
			for supported_recipe in supported_recipes
		)

	def add_constraints (self, constraints, supported_recipes):

		constraints . append (self . count_variable >= 0)
		constraints . append (
			self . count_variable == self . __count (supported_recipes)
		)

	def interpret_model (self, model, precision):

		count = model [self . count_variable]

		if utils . interpret_approximate (count, precision) == 0:

			return None

		return utils . format_value (count, precision)

def load_machines (machines_file_name):

	with open (machines_file_name, 'r') as machines_file:

		machines_data = commentjson . load (machines_file)

	machines = dict ()

	for machine_pretty_name in machines_data:

		machines [machine_pretty_name] = Machine (machine_pretty_name)

	return machines

def get_machine (machine_name, machines):

	if machine_name not in machines:

		raise ValueError (
			'\'' + machine_name + '\' does not name a valid machine'
		)

	return machines [machine_name]
