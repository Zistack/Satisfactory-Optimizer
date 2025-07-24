import commentjson

from collections import defaultdict

import utils

from configurations import Configurations
from machine import get_machine
from node_type import get_node_type
from item import load_finite_item_quantities

class RawRecipe:

	def __init__ (
		self,
		pretty_name,
		time,
		machine,
		power_consumption,
		node_type = None,
		well_configuration = None,
		input_quantities = None,
		output_quantities = None,
		power_augmentation_factor = None,
	):

		self . pretty_name = pretty_name

		self . time = time
		self . machine = machine
		self . power_consumption = power_consumption

		self . node_type = node_type
		self . well_configuration = well_configuration
		self . input_quantities = input_quantities
		self . output_quantities = output_quantities
		self . power_augmentation_factor = power_augmentation_factor

	def supports_overclocking (self):

		return self . machine . supports_overclocking ()

	def supports_productivity (self):

		return self . machine . supports_productivity ()

	def somersloop_slots (self, model_productivity):

		return self . machine . somersloop_slots if model_productivity else None

	def requires_somersloops (self):

		return self . machine . requires_somersloops ()

	def input_items (self):

		return self . input_quantities . keys ()

	def output_items (self):

		return self . output_quantities . keys ()

	def encode (
		self,
		constraints,
		overclock_limits,
		model_productivity
	):

		configurations = Configurations (
			self . pretty_name,
			overclock_limits,
			self . somersloop_slots (model_productivity),
			self . requires_somersloops ()
		)

		configurations . add_constraints (constraints)

		return EncodedRecipe (self, configurations)

class EncodedRecipe:

	def __init__ (self, raw_recipe, configurations):

		self . raw_recipe = raw_recipe
		self . configurations = configurations

	def machine_count (self):

		return self . configurations . machine_count ()

	def output_magnitude (self):

		return self . configurations . output_magnitude ()

	def input_rate (self, item):

		quantity = self . raw_recipe . input_quantities [item]
		return (
			self . configurations . input_magnitude ()
			* quantity
			* 60
			/ self . raw_recipe . time
		)

	def output_rate (self, item):

		quantity = self . raw_recipe . output_quantities [item]
		return (
			self . configurations . output_magnitude ()
			* quantity
			* 60
			/ self . raw_recipe . time
		)

	def power_consumption (self):

		return (
			self . configurations . power_magnitude (self . raw_recipe . machine)
			* self . raw_recipe . power_consumption
		)

	# Only called if model_productivity is true
	def allocated_somersloops (self):

		allocated_somersloops = self . configurations . somersloops_slotted ()

		if self . raw_recipe . requires_somersloops ():

			allocated_somersloops += (
				self . configurations . machine_count ()
				* self . raw_recipe . machine . required_somersloops
			)

		return allocated_somersloops

	def interpret (self, model, precision):

		interpreted_configurations = self . configurations . interpret_model (
			model,
			self . raw_recipe . machine,
			precision
		)

		return InterpretedRecipe (self . raw_recipe, interpreted_configurations)

class InterpretedRecipe:

	def __init__ (self, raw_recipe, interpreted_configurations):

		self . raw_recipe = raw_recipe
		self . interpreted_configurations = interpreted_configurations

	def pretty_name (self):

		return self . raw_recipe . pretty_name

	def machine_count (self):

		return self . interpreted_configurations . machine_count ()

	def __input_magnitude (self):

		return self . interpreted_configurations . input_magnitude ()

	def __output_magnitude (self):

		return self . interpreted_configurations . output_magnitude ()

	def __power_magnitude (self):

		return self . interpreted_configurations . power_magnitude ()

	def input_rate (self, item):

		quantity = self . raw_recipe . input_quantities [item]
		return (
			self . __input_magnitude ()
			* quantity
			* 60
			/ self . raw_recipe . time
		)

	def output_rate (self, item):

		quantity = self . raw_recipe . output_quantities [item]
		return (
			self . __output_magnitude ()
			* quantity
			* 60
			/ self . raw_recipe . time
		)

	def power_consumption (self):

		return (
			self . __power_magnitude ()
			* self . raw_recipe . power_consumption
		)

	def get_report (self, precision):

		if (
			utils . interpret_approximate (
				self . machine_count (),
				precision
			) == 0
		):

			return None

		report = dict ()

		config_report = self . interpreted_configurations . get_report (
			self . raw_recipe . machine,
			precision
		)

		report . update (config_report)

		if self . raw_recipe . input_quantities:

			report ['inputs'] = dict (
				(
					item . pretty_name,
					utils . format_value (
						self . __input_magnitude ()
							* quantity
							* 60
							/ self . raw_recipe . time,
						precision
					)
				)
				for item, quantity
				in self . raw_recipe . input_quantities . items ()
			)

		if self . raw_recipe . output_quantities:

			report ['outputs'] = dict (
				(
					item . pretty_name,
					utils . format_value (
						self . __output_magnitude ()
							* quantity
							* 60
							/ self . raw_recipe . time,
						precision
					)
				)
				for item, quantity
				in self . raw_recipe . output_quantities . items ()
			)

		report ['power_consumption'] = utils . format_value (
			self . power_consumption (),
			precision
		)

		if self . raw_recipe . power_augmentation_factor:

			report [
				'total_power_augmentation_factor'
			] = utils . format_value (
				self . machine_count ()
					* self . raw_recipe . power_augmentation_factor,
				precision
			)

		return report

def load_node_type (recipe_data, node_types):

	if 'node_type' in recipe_data:

		return get_node_type (recipe_data ['node_type'], node_types)

	else:

		return None

def load_inputs (recipe_data, items):

	if 'inputs' in recipe_data:

		return load_finite_item_quantities (
			recipe_data ['inputs'],
			items
		)

	else:

		return dict ()

def load_outputs (recipe_data, items):

	if 'outputs' in recipe_data:

		return load_finite_item_quantities (
			recipe_data ['outputs'],
			items
		)

	else:

		return dict ()

def load_power_augmentation_factor (recipe_data):

	if 'power_augmentation_factor' in recipe_data:

		return utils . real (recipe_data ['power_augmentation_factor'])

	else:

		return None

def load_raw_recipe (
	pretty_name,
	recipe_data,
	machines,
	node_types,
	items
):

	time = utils . real (recipe_data ['time'])
	machine = get_machine (recipe_data ['machine'], machines)
	power_consumption = utils . real (recipe_data ['power_consumption'])

	node_type = load_node_type (recipe_data, node_types)
	input_quantities = load_inputs (recipe_data, items)
	output_quantities = load_outputs (recipe_data, items)
	power_augmentation_factor = load_power_augmentation_factor (recipe_data)

	return RawRecipe (
		pretty_name,
		time,
		machine,
		power_consumption,
		node_type = node_type,
		input_quantities = input_quantities,
		output_quantities = output_quantities,
		power_augmentation_factor = power_augmentation_factor
	)
