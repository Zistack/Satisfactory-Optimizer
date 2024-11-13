import commentjson

import linprog as lp

import utils

class Item:

	def __init__ (self, pretty_name):

		self . pretty_name = pretty_name



	def production (self, producing_recipes):

		return sum (
			producing_recipe . output_rate (self)
			for producing_recipe in producing_recipes
		)

	def consumption (self, consuming_recipes):

		return sum (
			consuming_recipe . input_rate (self)
			for consuming_recipe in consuming_recipes
		)

	def add_constraints (
		self,
		constraints,
		encoded_producing_recipes,
		encoded_consuming_recipes,
		input_rate,
		output_rate
	):

		if input_rate == 'unlimited' and output_rate == 'unlimited':

			# There are no meaningful constraints

			pass

		elif input_rate == 'unlimited':

			constraints . append (
				self . production (encoded_producing_recipes)
				<= self . consumption (encoded_consuming_recipes) + output_rate
			)

		elif output_rate == 'unlimited':

			constraints . append (
				self . production (encoded_producing_recipes) + input_rate
				>= self . consumption (encoded_consuming_recipes)
			)

		else:

			constraints . append (
				self . production (encoded_producing_recipes) + input_rate
				== self . consumption (encoded_consuming_recipes) + output_rate
			)

			constraint = (
				self . production (encoded_producing_recipes) + input_rate
				== self . consumption (encoded_consuming_recipes) + output_rate
			)

	def interpret (
		self,
		model,
		precision,
		interpreted_producing_recipes,
		interpreted_consuming_recipes,
		input_rate,
		output_rate
	):

		item_report = dict ()

		amount_produced = self . production (interpreted_producing_recipes)
		amount_consumed = self . consumption (interpreted_consuming_recipes)

		if utils . interpret_approximate (amount_produced, precision) != 0:

			item_report ['produced'] = utils . format_value (
				amount_produced,
				precision
			)

			item_report ['produced_by'] = dict (
				[
					(
						recipe . pretty_name (),
						utils . format_value (
							recipe . output_rate (self),
							precision
						)
					)
					for recipe in interpreted_producing_recipes
					if utils . interpret_approximate(recipe . output_rate (self), precision) != 0
				]
			)

		if utils . interpret_approximate (amount_consumed, precision) != 0:

			item_report ['consumed'] = utils . format_value (
				amount_consumed,
				precision
			)

			item_report ['consumed_by'] = dict (
				[
					(
						recipe . pretty_name (),
						utils . format_value (
							recipe . input_rate (self),
							precision
						)
					)
					for recipe in interpreted_consuming_recipes
					if utils . interpret_approximate(recipe . input_rate (self), precision) != 0
				]
			)

		if len (item_report) != 0:

			return item_report

		else:

			return None

def load_items (items_file_name):

	with open (items_file_name, 'r') as items_file:

		items_data = commentjson . load (items_file)

	items = dict ()

	for item_pretty_name in items_data:

		items [item_pretty_name] = Item (item_pretty_name)

	return items

def get_item (item_name, items):

	if item_name not in items:

		raise ValueError ('\'' + item_name + '\' does not name a valid item')

	return items [item_name]

def load_item_quantities (item_quantities_data, items):

	item_quantities = dict ()

	for item_name, quantity in item_quantities_data . items ():

		item = get_item (item_name, items)

		item_quantity = (
			'unlimited' if quantity == 'unlimited' else utils . real (quantity)
		)

		item_quantities [item] = item_quantity

	return item_quantities

def load_finite_item_quantities (item_quantities_data, items):

	item_quantities = dict ()

	for item_name, quantity in item_quantities_data . items ():

		item = get_item (item_name, items)

		item_quantity = utils . real (quantity)

		item_quantities [item] = item_quantity

	return item_quantities
