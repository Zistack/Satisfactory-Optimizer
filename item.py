import commentjson

import linprog as lp

import utils

class Item:

	def __init__ (self, pretty_name, max_flow_rate):

		self . pretty_name = pretty_name
		self . max_flow_rate = max_flow_rate

		name = utils . name (pretty_name)

		self . flow_variable = lp . Variable (name + '_flow')
		self . input_variable = lp . Variable (name + '_input')
		self . output_variable = lp . Variable (name + '_output')

	def constrain_total_flow_rate (
		self,
		constraints,
		total_flow_rate,
		output_count
	):

		if self . max_flow_rate != None:

			return constraints . append (
				total_flow_rate <= self . max_flow_rate * output_count
			)

	def __production (self, item, producing_recipes):

		return sum (
			[
				producing_recipe . output_rate (item)
				for producing_recipe in producing_recipes
			]
			+ [self . input_variable]
		)

	def __consumption (self, item, consuming_recipes):

		return sum (
			[
				consuming_recipe . input_rate (item)
				for consuming_recipe in consuming_recipes
			]
			+ [self . output_variable]
		)

	def add_constraints (
		self,
		constraints,
		producing_recipes,
		consuming_recipes
	):

		constraints . append (self . flow_variable >= 0)
		constraints . append (self . input_variable >= 0)
		constraints . append (self . output_variable >= 0)

		constraints . append (
			self . flow_variable
				== self . __production (self, producing_recipes)
		)
		constraints . append (
			self . flow_variable
				== self . __consumption (self, consuming_recipes)
		)

	def interpret_model (self, model, precision):

		amount = model [self . flow_variable]

		if utils . interpret_approximate (amount, precision) == 0:

			return None

		else:

			return utils . format_value (amount, precision)

def load_items (items_file_name):

	with open (items_file_name, 'r') as items_file:

		items_data = commentjson . load (items_file)

	items = dict ()

	for item_pretty_name, item_data in items_data . items ():

		if 'max_flow_rate' in item_data:

			max_flow_rate = utils . real (item_data ['max_flow_rate'])

		else:

			max_flow_rate = None

		items [item_pretty_name] = Item (item_pretty_name, max_flow_rate)

	return items

def get_item (item_name, items):

	if item_name not in items:

		raise ValueError ('\'' + item_name + '\' does not name a valid item')

	return items [item_name]

def get_item_quantities (item_quantities_data, items):

	item_quantities = dict ()

	for item_name, quantity in item_quantities_data . items ():

		item = get_item (item_name, items)

		item_quantity = (
			'unlimited' if quantity == 'unlimited' else utils . real (quantity)
		)

		item_quantities [item] = item_quantity

	return item_quantities

def get_finite_item_quantities (item_quantities_data, items):

	item_quantities = dict ()

	for item_name, quantity in item_quantities_data . items ():

		item = get_item (item_name, items)

		item_quantity = utils . real (quantity)

		item_quantities [item] = item_quantity

	return item_quantities
