from z3 import *

import utils

from item import get_item, get_finite_item_quantities
from recipe_utils import get_recipe

item_flow = lambda item: item . flow_variable
item_consumption = lambda item: item . input_variable
item_production = lambda item: item . output_variable

def maximize (solver, objective):

	solver . maximize (objective)

def minimize (solver, objective):

	solver . minimize (objective)

class ItemObjectiveFunction:

	def __init__ (self, item, item_variable, optimization_type):

		self . item = item
		self . item_variable = item_variable
		self . optimization_type = optimization_type

	def add_objective (self, solver):

		self . optimization_type (solver, self . item_variable (self . item))

class ItemsObjectiveFunction:

	def __init__ (self, item_ratios, item_variable, optimization_type):

		self . item_ratios = item_ratios
		self . item_variable = item_variable
		self . optimization_type = optimization_type

		pretty_name = ' ' . join (
			str (ratio) + ' ' + item . pretty_name
			for item, ratio in self . item_ratios . items ()
		)

		name = utils . name (pretty_name)

		self . variable = Real (name)

	def add_objective (self, solver):

		for item, ratio in self . item_ratios . items ():

			solver . add (
				self . item_variable (item) == self . variable * ratio
			)

		self . optimization_type (solver, self . variable)

class VariableObjectiveFunction:

	def __init__ (self, variable, optimization_type):

		self . variable = variable
		self . optimization_type = optimization_type

	def add_constraints (self, solver):

		self . optimization_type (solver, self . variable)

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
