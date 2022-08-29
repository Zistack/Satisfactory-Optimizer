import linprog as lp

import utils

from item import get_item, get_finite_item_quantities
from recipe_utils import get_recipe, get_recipe_set, make_recipe_set_concrete

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

	def add_objective (
		self,
		constraints,
		objectives,
		well_configurations,
		configured_well_recipes
	):

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

	def add_objective (
		self,
		constraints,
		objectives,
		well_configurations,
		configured_well_recipes
	):

		constraints . append (self . variable >= 0)

		for item, ratio in self . item_ratios . items ():

			constraints . append (
				self . item_variable (item) == self . variable * ratio
			)

		objectives . append (self . objective_type (self . variable))

class RecipeObjectiveFunction:

	def __init__ (self, recipes, objective_type):

		self . recipes = recipes
		self . objective_type = objective_type

		pretty_name = ' ' . join (recipe . pretty_name for recipe in recipes)

		name = utils . name (pretty_name)

		self . variable = lp . Variable (name)

	def add_objective (
		self,
		constraints,
		objectives,
		well_configurations,
		configured_well_recipes
	):

		concrete_recipes = make_recipe_set_concrete (
			self . recipes,
			well_configurations,
			configured_well_recipes
		)

		constraints . append (self . variable >= 0)
		constraints . append (
			self . variable == sum (
				recipe . recipe . linear_magnitude_variable
				for recipe in concrete_recipes
			)
		)

		objectives . append (self . objective_type (self . variable))

def get_objective_function (
	function_type,
	function_data,
	items,
	recipes,
	groups
):

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

	if function_type == 'maximize_recipe':

		return RecipeObjectiveFunction (
			get_recipe_set (function_data, recipes, groups),
			maximize
		)

	if function_type == 'minimize_recipe':

		return RecipeObjectiveFunction (
			get_recipe_set (function_data, recipes, groups),
			minimize
		)

	raise ValueError (
		'\'' + function_type + '\' does not name a valid production goal'
	)
