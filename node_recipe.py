from z3 import *

from utils import *

from node_type import get_node_type
from item import get_item
from machine import get_machine
from recipe import Recipe

class NodeRecipe:

	def __init__ (
		self,
		pretty_name,
		node_type,
		resource,
		rate,
		machine,
		power_consumption,
		overclock_exponent
	):

		self . pretty_name = pretty_name

		self . node_type = node_type
		self . resource = resource
		self . rate = rate

		self . recipe = Recipe (
			pretty_name,
			machine,
			power_consumption,
			overclock_exponent
		)

	def output_rate (self, item):

		assert (item == self . resource)

		return self . recipe . magnitude () * self . rate

	def add_constraints (self, solver, overclock_limits):

		self . recipe . add_constraints (solver, overclock_limits)

		if self . resource != None:

			self . resource . constrain_total_flow_rate (
				solver,
				self . recipe . magnitude () * self . rate,
				self . recipe . machine_count_variable
			)

	def interpret_model (self, model):

		interpretation = self . recipe . get_interpretation ()

		if interpretation == None:

			return None

		interpretation ['output'] = {
			self . resource . pretty_name:
				str (model . eval (self . output_rates [self . resource]))
		}

		return interpretation

def get_node_recipe (
	node_recipe_pretty_name,
	node_recipe_data,
	node_types,
	items,
	machines
):

	node_type = get_node_type (
		node_recipe_data ['node_type'],
		node_types
	)

	if 'resource' in node_recipe_data:

		resource = get_item (node_recipe_data ['resource'], items)
		rate = RealVal (node_recipe_data ['rate'])

	else:

		resource = None
		rate = None

	machine = get_machine (node_recipe_data ['machine'], machines)
	power_consumption = RealVal (node_recipe_data ['power_consumption'])

	if 'overclock_exponent' in node_recipe_data:

		overclock_exponent = float (node_recipe_data ['overclock_exponent'])

	else:

		overclock_exponent = None

	return NodeRecipe (
		node_recipe_pretty_name,
		node_type,
		resource,
		rate,
		machine,
		power_consumption,
		overclock_exponent
	)
