import linprog as lp

import utils

from item import get_item, get_finite_item_quantities
from recipe_utils import get_recipe

item_flow = lambda item: item . flow_variable
item_consumption = lambda item: item . input_variable
item_production = lambda item: item . output_variable

maximize = lambda v: - v
minimize = lambda v: v

class ItemObjectiveFunction:

	def __init__ (self, item, item_variable, objective_type):

		self . item = item
		self . item_variable = item_variable
		self . objective_type = objective_type

	def add_objective (self, constraints, objectives):

		objectives . append (
			self . objective_type (self . item_variable (self . item))
		)

class ItemsObjectiveFunction:

	def __init__ (self, item_ratios, item_variable, objective_type):

		self . item_ratios = item_ratios
		self . item_variable = item_variable
		self . objective_type = objective_type

		pretty_name = ' ' . join (
			str (ratio) + ' ' + item . pretty_name
			for item, ratio in self . item_ratios . items ()
		)

		name = utils . name (pretty_name)

		self . variable = lp . Variable (name)

	def add_objective (self, constraints, objectives):

		for item, ratio in self . item_ratios . items ():

			constraints . append (self . variable >= 0)
			constraints . append (
				self . item_variable (item) == self . variable * ratio
			)

		objectives . append (self . objective_type (self . variable))

def get_objective_function (function_type, function_data, items):

	if function_type == 'maximize_item_production':

		return ItemObjectiveFunction (
			get_item (function_data, items),
			item_production,
			maximize
		)

	if function_type == 'minimize_item_production':

		return ItemObjectiveFunction (
			get_item (function_data, items),
			item_production,
			minimize
		)

	if function_type == 'maximize_items_production':

		return ItemsObjectiveFunction (
			get_finite_item_quantities (function_data, items),
			item_production,
			maximize
		)

	if function_type == 'maximize_item_consumption':

		return ItemObjectiveFunction (
			get_item (function_data, items),
			item_consumption,
			maximize
		)

	if function_type == 'minimize_item_consumption':

		return ItemObjectiveFunction (
			get_item (function_data, items),
			item_consumption,
			minimize
		)

	if function_type == 'maximize_item_flow':

		return ItemObjectiveFunction (
			get_item (function_data, items),
			item_flow,
			maximize
		)

	if function_type == 'minimize_item_flow':

		return ItemObjectiveFunction (
			get_item (function_data, items),
			item_flow,
			minimize
		)

	if function_type == 'maximize_items_flow':

		return ItemsObjectiveFunction (
			get_finite_item_quantities (function_data, items),
			item_flow,
			maximize
		)

	raise ValueError (
		'\'' + function_type + '\' does not name a valid production goal'
	)
