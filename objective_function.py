import linprog as lp

import utils

from item import get_item, load_finite_item_quantities
from recipe_utils import get_recipe, get_recipe_set

def item_production (item, recipe_registry):

	return item . production (
		recipe_registry . item_producing_recipes [item]
	)

def item_consumption (item, recipe_registry):

	return item . consumption (
		recipe_registry . item_consuming_recipes [item]
	)

def item_output (item, recipe_registry):

	return (
		item . production (recipe_registry . item_producing_recipes [item])
		- item . consumption (recipe_registry . item_consuming_recipes [item])
	)

def item_input (item, recipe_registry):

	return (
		item . consumption (recipe_registry . item_consuming_recipes [item])
		- item . production (recipe_registry . item_producing_recipes [item])
	)

maximize = lambda v: - v
minimize = lambda v: v

class ItemObjectiveFunction:

	def __init__ (self, item, item_expression, objective_type):

		self . item = item
		self . item_expression = item_expression
		self . objective_type = objective_type

	def add_objective (self, constraints, objectives, recipe_registry):

		objectives . append (
			self . objective_type (
				self . item_expression (self . item, recipe_registry)
			)
		)

class ItemsObjectiveFunction:

	def __init__ (self, item_ratios, item_expression, objective_type):

		self . item_ratios = item_ratios
		self . item_expression = item_expression
		self . objective_type = objective_type

		pretty_name = ' ' . join (
			str (ratio) + ' ' + item . pretty_name
			for item, ratio in self . item_ratios . items ()
		)

		name = utils . name (pretty_name)

		self . combination_variable = lp . Variable (name)

	def add_objective (self, constraints, objectives, recipe_registry):

		constraints . append (self . combination_variable >= 0)

		for item, ratio in self . item_ratios . items ():

			constraints . append (
				self . item_expression (item, recipe_registry)
				== self . combination_variable * ratio
			)

		objectives . append (self . objective_type (self . combination_variable))

class WeightedItemsObjectiveFunction:

	def __init__ (self, item_weights, item_expression, objective_type):

		self . item_weights = item_weights
		self . item_expression = item_expression
		self . objective_type = objective_type

	def add_objective (self, constraints, objectives, recipe_registry):

		objectives . append (
			self . objective_type (
				sum (
					self . item_expression (item, recipe_registry) * weight
					for item, weight in self . item_weights . items ()
				)
			)
		)

class RecipeObjectiveFunction:

	def __init__ (self, raw_recipes, objective_type):

		self . raw_recipes = raw_recipes
		self . objective_type = objective_type

	def add_objective (
		self,
		constraints,
		objectives,
		recipe_registry
	):

		encoded_recipes = recipe_registry . get_encoded_recipes (
			self . raw_recipes
		)

		objectives . append (
			self . objective_type (
				sum (
					encoded_recipe . output_magnitude ()
					for encoded_recipe in encoded_recipes
				)
			)
		)

def load_objective_function (
	function_type,
	function_data,
	items,
	searchable_recipes,
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

	if function_type == 'maximize_items_production_by_weight':

		return WeightedItemsObjectiveFunction (
			load_finite_item_quantities (function_data, items),
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

	if function_type == 'minimize_items_consumption_by_weight':

		return WeightedItemsObjectiveFunction (
			load_finite_item_quantities (function_data, items),
			item_consumption,
			minimize
		)

	if function_type == 'maximize_item_input':

		return ItemObjectiveFunction (
			get_item (function_data, items),
			item_input,
			maximize
		)

	if function_type == 'minimize_item_input':

		return ItemObjectiveFunction (
			get_item (function_data, items),
			item_input,
			minimize
		)

	if function_type == 'maximize_item_output':

		return ItemObjectiveFunction (
			get_item (function_data, items),
			item_output,
			maximize
		)

	if function_type == 'minimize_item_output':

		return ItemObjectiveFunction (
			get_item (function_data, items),
			item_output,
			minimize
		)

	if function_type == 'maximize_items_output':

		return ItemsObjectiveFunction (
			load_finite_item_quantities (function_data, items),
			item_output,
			maximize
		)

	if function_type == 'maximize_recipe':

		return RecipeObjectiveFunction (
			get_recipe_set (function_data, searchable_recipes, groups),
			maximize
		)

	if function_type == 'minimize_recipe':

		return RecipeObjectiveFunction (
			get_recipe_set (function_data, searchable_recipes, groups),
			minimize
		)

	raise ValueError (
		'\'' + function_type + '\' does not name a valid production goal'
	)
