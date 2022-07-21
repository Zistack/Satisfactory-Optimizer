import commentjson
import sys

from collections import defaultdict
from z3 import *

import utils

class Recipe:

	def __init__ (
		self,
		pretty_name,
		name,
		input_quantities,
		output_quantities,
		time,
		machine,
		power_consumption
	):

		self . pretty_name = pretty_name

		self . input_quantities = input_quantities
		self . output_quantities = output_quantities
		self . time = time
		self . machine = machine
		self . power_consumption = power_consumption

		self . machine_count_variable = Real (name + '_machine_count')

		for item in self . input_quantities . keys ():

			item . add_consuming_recipe (self)

		for item in self . output_quantities . keys ():

			item . add_producing_recipe (self)

		self . machine . add_supported_recipe (self)

	def __rate_calculation (self, quantity):

		return (
			self . machine_count_variable
			* quantity
			* RealVal (60)
			/ self . time
		)

	def input_rate_calculation (self, item):

		return self . __rate_calculation (self . input_quantities [item])

	def output_rate_calculation (self, item):

		return self . __rate_calculation (self . output_quantities [item])

	def power_consumption_calculation (self):

		return self . machine_count_variable * self . power_consumption

	def add_constraints (self, solver):

		solver . add (self . machine_count_variable >= 0)

	def interpret_model (self, model):

		machine_count = model . eval (self . machine_count_variable)

		if machine_count == 0:

			return None

		inputs = dict (
			(
				item . pretty_name,
				str (model . eval (self . __rate_calculation (quantity)))
			)
			for item, quantity in self . input_quantities . items ()
		)
		outputs = dict (
			(
				item . pretty_name,
				str (model . eval (self . __rate_calculation (quantity)))
			)
			for item, quantity in self . output_quantities . items ()
		)

		power_consumption = str (
			model . eval (self . power_consumption_calculation ())
		)

		return {
			'machine_count': str (machine_count),
			'inputs': inputs,
			'outputs': outputs,
			'power_consumption': power_consumption
		}

def get_tags (recipe_data):

	if 'tags' in recipe_data:

		return recipe_data ['tags']

	else:

		return []

def load_recipes (recipes_file_name, items, machines):

	with open (recipes_file_name, 'r') as recipes_file:

		recipes_data = commentjson . load (recipes_file)

	recipes = dict ()
	groups = defaultdict (set)

	for recipe_pretty_name, recipe_data in recipes_data . items ():

		name = utils . variable_name (recipe_pretty_name)

		input_quantities = utils . get_item_quantities (
			recipe_data ['inputs'],
			items
		)

		output_quantities = utils . get_item_quantities (
			recipe_data ['outputs'],
			items
		)

		time = RealVal (recipe_data ['time'])
		machine = utils . get_machine (recipe_data ['machine'], machines)
		power_consumption = RealVal (recipe_data ['power_consumption'])

		recipe = Recipe (
			recipe_pretty_name,
			name,
			input_quantities,
			output_quantities,
			time,
			machine,
			power_consumption
		)

		for tag in get_tags (recipe_data):

			groups [tag] . add (recipe)

		recipes [recipe_pretty_name] = recipe

	return recipes, groups
