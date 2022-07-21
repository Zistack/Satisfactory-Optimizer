import commentjson
import sys

from z3 import *

import utils

class Machine:

	def __init__ (self, pretty_name, name):

		self . pretty_name = pretty_name

		self . count_variable = Real ('total_' + name + '_count')

		self . supported_recipes = list ()

	def add_supported_recipe (self, recipe):

		self . supported_recipes . append (recipe)

	def add_constraints (self, solver):

		solver . add (self . count_calculation ())

	def count_calculation (self):

		return self . count_variable == sum (
			supported_recipe . machine_count_variable
			for supported_recipe in self . supported_recipes
		)

	def interpret_model (self, model):

		count = model . eval (self . count_variable)

		if count == 0:

			return None

		return str (count)

def load_machines (machines_file_name):

	with open (machines_file_name, 'r') as machines_file:

		machines_data = commentjson . load (machines_file)

	machines = dict ()

	for machine_pretty_name in machines_data:

		name = utils . variable_name (machine_pretty_name)

		machines [machine_pretty_name] = Machine (machine_pretty_name, name)

	return machines
