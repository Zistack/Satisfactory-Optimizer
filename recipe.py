import commentjson

from collections import defaultdict

import utils

from corners import Corners
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

		corners = Corners (
			utils . name (self . pretty_name),
			overclock_limits,
			self . machine . somersloop_slots if model_productivity else None
		)

		corners . add_constraints (constraints)

		return EncodedRecipe (self, corners)

class EncodedRecipe:

	def __init__ (self, raw_recipe, corners):

		self . raw_recipe = raw_recipe
		self . corners = corners

	def machine_count (self):

		return self . corners . machine_count ()

	def output_magnitude (self):

		return self . corners . output_magnitude ()

	def input_rate (self, item):

		quantity = self . raw_recipe . input_quantities [item]
		return (
			self . corners . input_magnitude ()
			* quantity
			* 60
			/ self . raw_recipe . time
		)

	def output_rate (self, item):

		quantity = self . raw_recipe . output_quantities [item]
		return (
			self . corners . output_magnitude ()
			* quantity
			* 60
			/ self . raw_recipe . time
		)

	def power_consumption (self):

		return (
			self . corners . power_magnitude (self . raw_recipe . machine)
			* self . raw_recipe . power_consumption
		)

	def allocated_somersloops (self):

		allocated_somersloops = self . corners . somersloops_slotted (
			self . raw_recipe . machine
		)

		if self . raw_recipe . requires_somersloops ():

			allocated_somersloops += (
				self . corners . machine_count ()
				* self . raw_recipe . machine . required_somersloops
			)

		return allocated_somersloops

	def interpret (self, model):

		interpreted_corners = self . corners . interpret_model (
			model,
			self . raw_recipe . machine
		)

		return InterpretedRecipe (self . raw_recipe, interpreted_corners)

class InterpretedRecipe:

	def __init__ (self, raw_recipe, interpreted_corners):

		self . raw_recipe = raw_recipe
		self . interpreted_corners = interpreted_corners

	def pretty_name (self):

		return self . raw_recipe . pretty_name

	def machine_count (self):

		return self . interpreted_corners . machine_count

	def output_magnitude (self):

		return self . interpreted_corners . output_magnitude

	def input_rate (self, item):

		quantity = self . raw_recipe . input_quantities [item]
		return (
			self . interpreted_corners . input_magnitude
			* quantity
			* 60
			/ self . raw_recipe . time
		)

	def output_rate (self, item):

		quantity = self . raw_recipe . output_quantities [item]
		return (
			self . interpreted_corners . output_magnitude
			* quantity
			* 60
			/ self . raw_recipe . time
		)

	def power_consumption (self):

		return (
			self . interpreted_corners . power_magnitude
			* self . raw_recipe . power_consumption
		)

	def allocated_somersloops (self):

		allocated_somersloops = self . interpreted_corners . somersloops_slotted

		if self . raw_recipe . requires_somersloops ():

			allocated_somersloops += (
				self . interpreted_corners . machine_count
				* self . raw_recipe . machine . required_somersloops
			)

		return allocated_somersloops

	def get_report (self, precision):

		if (
			utils . interpret_approximate (
				self . interpreted_corners . machine_count,
				precision
			) == 0
		):

			return None

		interpretation = dict ()

		interpretation ['machine_count'] = utils . format_value (
			self . interpreted_corners . machine_count,
			precision
		)

		interpretation ['power_consumption'] = utils . format_value (
			self . interpreted_corners . power_magnitude
				* self . raw_recipe . power_consumption,
			precision
		)

		if (
			utils . interpret_approximate (
				self . interpreted_corners . overclock_setting,
				6
			) != 1
		):
			interpretation ['overclock_setting'] = utils . format_value (
				self . interpreted_corners . overclock_setting,
				6
			)

		if (
			utils . interpret_approximate (
				self . interpreted_corners . somersloops_slotted,
				precision
			) != 0
		):

			interpretation ['somersloops_slotted'] = utils . format_value (
				self . interpreted_corners . somersloops_slotted,
				0
			)

		if self . raw_recipe . input_quantities:

			interpretation ['inputs'] = dict (
				(
					item . pretty_name,
					utils . format_value (
						self . interpreted_corners . input_magnitude
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

			interpretation ['outputs'] = dict (
				(
					item . pretty_name,
					utils . format_value (
						self . interpreted_corners . output_magnitude
							* quantity
							* 60
							/ self . raw_recipe . time,
						precision
					)
				)
				for item, quantity
				in self . raw_recipe . output_quantities . items ()
			)

		if self . raw_recipe . power_augmentation_factor:

			interpretation [
				'total_power_augmentation_factor'
			] = utils . format_value (
				self . interpreted_corners . machine_count
					* self . raw_recipe . power_augmentation_factor,
				precision
			)

		return interpretation

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
