import commentjson
import sys

from z3 import *

import utils

class Item:

	def __init__ (self, pretty_name, name):

		self . pretty_name = pretty_name

		self . flow_variable = Real ('total_' + name + '_flow')

		self . input_variable = Real ('input_' + name)
		self . output_variable = Real ('output_' + name)

		self . producing_recipes = list ()
		self . consuming_recipes = list ()

	def add_producing_recipe (self, recipe):

		self . producing_recipes . append (recipe)

	def add_consuming_recipe (self, recipe):

		self . consuming_recipes . append (recipe)

	def add_constraints (self, solver):

		solver . add (self . flow_variable >= 0)
		solver . add (self . input_variable >= 0)
		solver . add (self . output_variable >= 0)

		solver . add (self . production_calculation ())
		solver . add (self . consumption_calculation ())

	def production_calculation (self):

		return self . flow_variable == sum (
			[
				producing_recipe . output_rate_calculation (self)
				for producing_recipe in self . producing_recipes
			]
			+ [self . input_variable]
		)

	def consumption_calculation (self):

		return self . flow_variable == sum (
			[
				consuming_recipe . input_rate_calculation (self)
				for consuming_recipe in self . consuming_recipes
			]
			+ [self . output_variable]
		)

	def interpret_model (self, model):

		amount = model . eval (self . flow_variable)

		if amount == 0:

			return None

		else:

			return str (amount)

def load_items (items_file_name):

	with open (items_file_name, 'r') as items_file:

		items_data = commentjson . load (items_file)

	items = dict ()

	for item_pretty_name in items_data:

		name = utils . variable_name (item_pretty_name)

		items [item_pretty_name] = Item (item_pretty_name, name)

	return items
