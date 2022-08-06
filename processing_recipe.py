import commentjson

import utils

from collections import defaultdict

from item import get_finite_item_quantities
from machine import get_machine
from recipe import Recipe

class ProcessingRecipe:

	def __init__ (
		self,
		pretty_name,
		input_quantities,
		output_quantities,
		time,
		machine,
		power_consumption,
		overclock_exponent
	):

		self . pretty_name = pretty_name

		self . input_quantities = input_quantities
		self . output_quantities = output_quantities
		self . time = time

		self . recipe = Recipe (
			pretty_name,
			machine,
			power_consumption,
			overclock_exponent
		)

	def rate (self, quantity):

		return (
			self . recipe . magnitude_variable
			* quantity
			* 60
			/ self . time
		)

	def interpret_rate (self, model, quantity):

		return (
			model [self . recipe . magnitude_variable]
			* quantity
			* 60
			/ self . time
		)

	def input_rate (self, item):

		quantity = self . input_quantities [item]
		return self . rate (quantity)

	def output_rate (self, item):

		quantity = self . output_quantities [item]
		return self . rate (quantity)

	def add_constraints (self, constraints, overclock_limits):

		self . recipe . add_constraints (constraints, overclock_limits)

		for item, quantity in self . input_quantities . items ():

			item . constrain_total_flow_rate (
				constraints,
				self . rate (quantity),
				self . recipe . machine_count_variable
			)

		for item, quantity in self . output_quantities . items ():

			item . constrain_total_flow_rate (
				constraints,
				self . rate (quantity),
				self . recipe . machine_count_variable
			)

	def interpret_model (self, model, precision):

		interpretation = self . recipe . interpret_model (model, precision)

		if interpretation == None:

			return None

		if self . input_quantities:

			interpretation ['inputs'] = dict (
				(
					item . pretty_name,
					utils . format_value (
						self . interpret_rate (model, quantity),
						precision
					)
				)
				for item, quantity in self . input_quantities . items ()
			)

		if self . output_quantities:

			interpretation ['outputs'] = dict (
				(
					item . pretty_name,
					utils . format_value (
						self . interpret_rate (model, quantity),
						precision
					)
				)
				for item, quantity in self . output_quantities . items ()
			)

		return interpretation

def get_processing_recipe (
	processing_recipe_pretty_name,
	processing_recipe_data,
	items,
	machines
):

	if 'inputs' in processing_recipe_data:

		input_quantities = get_finite_item_quantities (
			processing_recipe_data ['inputs'],
			items
		)

	else:

		input_quantities = dict ()

	if 'outputs' in processing_recipe_data:

		output_quantities = get_finite_item_quantities (
			processing_recipe_data ['outputs'],
			items
		)

	else:

		output_quantities = dict ()

	time = utils . real (processing_recipe_data ['time'])

	machine = get_machine (processing_recipe_data ['machine'], machines)
	power_consumption = utils . real (
		processing_recipe_data ['power_consumption']
	)

	if 'overclock_exponent' in processing_recipe_data:

		overclock_exponent = utils . real (
			processing_recipe_data ['overclock_exponent']
		)

	else:

		overclock_exponent = None

	return ProcessingRecipe (
		processing_recipe_pretty_name,
		input_quantities,
		output_quantities,
		time,
		machine,
		power_consumption,
		overclock_exponent
	)
