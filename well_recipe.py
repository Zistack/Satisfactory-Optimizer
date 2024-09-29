import commentjson

import utils

from machine import get_machine

from well_type import get_well_type
from item import get_item

from recipe import (
	RawRecipe,
	load_inputs,
	load_outputs,
	load_power_augmentation_factor
)

class WellRecipe:

	def __init__ (
		self,
		pretty_name,
		time,
		machine,
		power_consumption,

		well_type,
		resource,
		purity_quantities,

		input_quantities,
		output_quantities,
		power_augmentation_factor
	):

		self . pretty_name = pretty_name

		self . time = time
		self . machine = machine
		self . power_consumption = power_consumption

		self . well_type = well_type
		self . resource = resource
		self . purity_quantities = purity_quantities

		self . input_quantities = input_quantities
		self . output_quantities = output_quantities
		self . power_augmentation_factor = power_augmentation_factor

	def supports_overclocking (self):

		return self . machine . supports_overclocking ()

	def supports_productivity (self):

		return self . machine . supports_productivity ()

	def requires_somersloops (self):

		return self . machine . supports_somersloops ()

	def input_items (self):

		return self . input_quantities . keys ()

	def output_items (self):

		return self . output_quantities . keys ()

	def specialize (self, well_configuration):

		pretty_name = (
			self . pretty_name + ' ' + well_configuration . pretty_name
		)

		output_quantities = self . output_quantities . copy ()

		resource_output_quantity = 0

		for purity, count in well_configuration . purity_counts . items ():

			resource_output_quantity += (
				self . purity_quantities [purity] * count
			)

		if self . resource in output_quantities:

			output_quantities [self . resource] += resource_output_quantity

		else:

			output_quantities [self . resource] = resource_output_quantity

		return RawRecipe (
			pretty_name,
			self . time,
			self . machine,
			self . power_consumption,
			well_configuration = well_configuration,
			input_quantities = self . input_quantities,
			output_quantities = output_quantities,
			power_augmentation_factor = self . power_augmentation_factor
		)

def load_purity_quantities (purity_quantities_data):

	return dict (
		(purity, utils . real (quantity))
		for purity, quantity in purity_quantities_data . items ()
	)

def load_well_recipe (
	pretty_name,
	recipe_data,
	machines,
	well_types,
	items
):

	time = utils . real (recipe_data ['time'])
	machine = get_machine (recipe_data ['machine'], machines)
	power_consumption = utils . real (recipe_data ['power_consumption'])

	well_type = get_well_type (
		recipe_data ['well_type'],
		well_types
	)
	resource = get_item (recipe_data ['resource'], items)
	purity_quantities = load_purity_quantities (
		recipe_data ['purity_quantities']
	)

	input_quantities = load_inputs (recipe_data, items)
	output_quantities = load_outputs (recipe_data, items)
	power_augmentation_factor = load_power_augmentation_factor (recipe_data)

	return WellRecipe (
		pretty_name,
		time,
		machine,
		power_consumption,
		well_type,
		resource,
		purity_quantities,
		input_quantities,
		output_quantities,
		power_augmentation_factor
	)
