import commentjson
import sys

from collections import defaultdict
import linprog as lp

import utils

from node_type import get_node_type
from well_type import get_well_type
from well_configuration import get_well_configuration
from item import get_item_quantities
from well_recipe import ConfiguredWellRecipe
from recipe_utils import get_recipe, get_recipe_set, filter_recipe_sets

from overclock_limits import get_overclock_limits
from objective_function import get_objective_function

class Problem:

	def __init__ (
		self,
		node_types,
		well_configurations,
		node_recipes,
		well_recipes,
		processing_recipes,
		input_items,
		output_items,
		overclocking,
		max_power_consumption,
		objective_functions
	):

		self . node_types = node_types
		self . well_configurations = well_configurations
		self . node_recipes = node_recipes
		self . well_recipes = well_recipes
		self . processing_recipes = processing_recipes
		self . input_items = input_items
		self . output_items = output_items
		self . overclocking = overclocking
		self . max_power_consumption = max_power_consumption
		self . objective_functions = objective_functions

	def encode_recipes (self, constraints):

		print ('Encoding recipes', file = sys . stderr)

		used_node_types = set ()
		used_items = set ()
		used_machines = set ()

		node_type_consuming_recipes = defaultdict (list)
		well_configuration_consuming_recipes = defaultdict (list)
		item_producing_recipes = defaultdict (list)
		item_consuming_recipes = defaultdict (list)
		machine_supported_recipes = defaultdict (list)

		for node_recipe in self . node_recipes . values ():

			node_recipe . add_constraints (
				constraints,
				self . overclocking [node_recipe]
			)

			used_node_types . add (node_recipe . node_type)
			used_machines . add (node_recipe . recipe . machine)

			node_type_consuming_recipes [node_recipe . node_type] . append (
				node_recipe
			)

			if node_recipe . resource != None:

				used_items . add (node_recipe . resource)

				item_producing_recipes [node_recipe . resource] . append (
					node_recipe
				)

			machine_supported_recipes [
				node_recipe . recipe . machine
			] . append (node_recipe)

		configured_well_recipes = dict ()

		for well_type, well_configurations in (
			self . well_configurations . items ()
		):

			for well_configuration in well_configurations . keys ():

				for well_recipe in self . well_recipes [well_type] . values ():

					configured_well_recipe = ConfiguredWellRecipe (
						well_recipe,
						well_configuration,
					)

					configured_well_recipe . add_constraints (
						constraints,
						self . overclocking [well_recipe]
					)

					used_machines . add (well_recipe . machine)

					well_configuration_consuming_recipes [
						well_configuration
					] . append (
						configured_well_recipe
					)

					if well_recipe . resource != None:

						used_items . add (well_recipe . resource)

						item_producing_recipes [
							well_recipe . resource
						] . append (configured_well_recipe)

					machine_supported_recipes [
						well_recipe . machine
					] . append (configured_well_recipe)

					configured_well_recipes [
						(well_recipe, well_configuration)
					] = (configured_well_recipe)

		for processing_recipe in self . processing_recipes . values ():

			processing_recipe . add_constraints (
				constraints,
				self . overclocking [processing_recipe]
			)

			used_items |= set (processing_recipe . output_quantities . keys ())
			used_items |= set (processing_recipe . input_quantities . keys ())
			used_machines . add (processing_recipe . recipe . machine)

			for item in processing_recipe . output_quantities . keys ():

				item_producing_recipes [item] . append (
					processing_recipe
				)

			for item in processing_recipe . input_quantities . keys ():

				item_consuming_recipes [item] . append (
					processing_recipe
				)

			machine_supported_recipes [
				processing_recipe . recipe . machine
			] . append (processing_recipe)

		return (
			used_node_types,
			used_items,
			used_machines,
			node_type_consuming_recipes,
			well_configuration_consuming_recipes,
			item_producing_recipes,
			item_consuming_recipes,
			machine_supported_recipes,
			configured_well_recipes,
		)

	def encode_node_types (
		self,
		constraints,
		used_node_types,
		node_type_consuming_recipes
	):

		print ('Encoding nodes', file = sys . stderr)

		used_node_types |= self . node_types . keys ()

		for node_type in used_node_types:

			node_type . add_constraints (
				constraints,
				node_type_consuming_recipes [node_type]
			)

			count = (
				self . node_types [node_type]
				if node_type in self . node_types
				else 0
			)

			constraints . append (node_type . allocation_variable <= count)

	def encode_well_configurations (
		self,
		constraints,
		well_configuration_consuming_recipes
	):

		print ('Encoding wells', file = sys . stderr)

		for well_type, well_configurations in (
			self . well_configurations . items ()
		):

			for well_configuration, count in well_configurations . items ():

				well_configuration . add_constraints (
					constraints,
					well_configuration_consuming_recipes [well_configuration]
				)

				constraints . append (
					well_configuration . allocation_variable <= count
				)

	def encode_items (
		self,
		constraints,
		used_items,
		item_producing_recipes,
		item_consuming_recipes
	):

		print ('Encoding items', file = sys . stderr)

		used_items |= self . input_items . keys ()
		used_items |= self . output_items . keys ()

		for item in used_items:

			item . add_constraints (
				constraints,
				item_producing_recipes [item],
				item_consuming_recipes [item]
			)

			if item in self . input_items:

				if type (self . input_items [item]) != str:

					constraints . append (
						item . input_variable == self . input_items [item]
					)

			else:

				constraints . append (item . input_variable == 0)

			if item in self . output_items:

				if type (self . output_items [item]) != str:

					constraints . append (
						item . output_variable == self . output_items [item]
					)

			else:

				constraints . append (item . output_variable == 0)

	def encode_machines (
		self,
		constraints,
		used_machines,
		machine_supported_recipes
	):

		print ('Encoding items', file = sys . stderr)

		for machine in used_machines:

			machine . add_constraints (
				constraints,
				machine_supported_recipes [machine]
			)

	def encode_power_consumption (self, constraints, configured_well_recipes):

		print ('Encoding total power consumption', file = sys . stderr)

		node_recipe_power_consumption = sum (
			node_recipe . recipe . power_consumption_variable
			for node_recipe in self . node_recipes . values ()
		)

		well_recipe_power_consumption = sum (
			configured_well_recipe . recipe . power_consumption_variable
			for configured_well_recipe in configured_well_recipes . values ()
		)

		processing_recipe_power_consumption = sum (
			processing_recipe . recipe . power_consumption_variable
			for processing_recipe in self . processing_recipes . values ()
		)

		total_power_consumption_variable = lp . Variable (
			'total_power_consumption'
		)

		constraints . append (
			total_power_consumption_variable == (
				node_recipe_power_consumption
				+ well_recipe_power_consumption
				+ processing_recipe_power_consumption
			)
		)

		if self . max_power_consumption != None:

			constraints . append (
				total_power_consumption_variable <= self . max_power_consumption
			)

		return total_power_consumption_variable

	def encode_machine_count (self, constraints, used_machines):

		print ('Encoding total machine count', file = sys . stderr)

		total_machine_count_variable = lp . Variable ('total_machine_count')

		constraints . append (total_machine_count_variable >= 0)
		constraints . append (
			total_machine_count_variable == sum (
				machine . count_variable for machine in used_machines
			)
		)

		return total_machine_count_variable

	def encode_objective_functions (
		self,
		constraints,
		objectives,
		used_items,
		total_power_consumption_variable,
		total_machine_count_variable
	):

		print ('Encoding objective functions', file = sys . stderr)

		for objective_function in self . objective_functions:

			objective_function . add_objective (constraints, objectives)

		objectives . append (total_power_consumption_variable)
		#objectives . append (total_machine_count_variable)

	def interpret_model (
		self,
		model,
		used_items,
		used_machines,
		configured_well_recipes,
		total_power_consumption_variable,
		total_machine_count_variable,
		precision
	):

		def has_interpretation (pair):

			name, interpretation = pair

			return interpretation != None

		item_interpretations = dict (
			filter (
				has_interpretation,
				[
					(
						item . pretty_name,
						item . interpret_model (model, precision)
					)
					for item in used_items
				]
			)
		)

		machine_interpretations = dict (
			filter (
				has_interpretation,
				[
					(
						machine . pretty_name,
						machine . interpret_model (model, precision)
					)
					for machine in used_machines
				]
			)
		)

		node_recipe_interpretations_list = list (
			filter (
				has_interpretation,
				[
					(
						node_recipe . pretty_name,
						node_recipe . interpret_model (model, precision)
					)
					for node_recipe in self . node_recipes . values ()
				]
			)
		)

		well_recipe_interpretations_list = list (
			filter (
				has_interpretation,
				[
					(
						(
							well_recipe . pretty_name
							+ ' '
							+ well_configuration . pretty_name
						),
						configured_well_recipe . interpret_model (
							model,
							precision
						)
					)
					for (well_recipe, well_configuration),
						configured_well_recipe
					in configured_well_recipes . items ()
				]
			)
		)

		processing_recipe_interpretations_list = list (
			filter (
				has_interpretation,
				[
					(
						processing_recipe . pretty_name,
						processing_recipe . interpret_model (model, precision)
					)
					for processing_recipe
					in self . processing_recipes . values ()
				]
			)
		)

		recipe_interpretations = dict (
			node_recipe_interpretations_list
			+ well_recipe_interpretations_list
			+ processing_recipe_interpretations_list
		)

		total_power_consumption_value = utils . format_value (
			model [total_power_consumption_variable],
			precision
		)
		total_machine_count_value = utils . format_value (
			model [total_machine_count_variable],
			precision
		)

		return {
			'items': item_interpretations,
			'machines': machine_interpretations,
			'recipes': recipe_interpretations,
			'total_power_consumption': total_power_consumption_value,
			'total_machine_count': total_machine_count_value
		}

	def solve (self, precision):

		print ('Encoding problem', file = sys . stderr)

		constraints = list ()
		objectives = list ()

		(
			used_node_types,
			used_items,
			used_machines,
			node_type_consuming_recipes,
			well_configuration_consuming_recipes,
			item_producing_recipes,
			item_consuming_recipes,
			machine_supported_recipes,
			configured_well_recipes,
		) = self . encode_recipes (constraints)

		self . encode_node_types (
			constraints,
			used_node_types,
			node_type_consuming_recipes
		)

		self . encode_well_configurations (
			constraints,
			well_configuration_consuming_recipes
		)

		self . encode_items (
			constraints,
			used_items,
			item_producing_recipes,
			item_consuming_recipes
		)

		self . encode_machines (
			constraints,
			used_machines,
			machine_supported_recipes
		)

		total_power_consumption_variable = self . encode_power_consumption (
			constraints,
			configured_well_recipes
		)

		total_machine_count_variable = self . encode_machine_count (
			constraints,
			used_machines
		)

		self . encode_objective_functions (
			constraints,
			objectives,
			used_items,
			total_power_consumption_variable,
			total_machine_count_variable
		)

		print ('Solving problem', file = sys . stderr)

		model = lp . solve (constraints, objectives)

		if model == None:

			return None

		print ('Interpreting model', file = sys . stderr)

		return self . interpret_model (
			model,
			used_items,
			used_machines,
			configured_well_recipes,
			total_power_consumption_variable,
			total_machine_count_variable,
			precision
		)

def load_problem (
	problem_file_name,
	node_types,
	well_types,
	items,
	all_recipes,
	node_recipes,
	well_recipes,
	processing_recipes,
	groups
):

	with open (problem_file_name, 'r') as problem_file:

		problem_data = commentjson . load (problem_file)

	# Nodes

	problem_node_types = dict ()

	if 'nodes' in problem_data:

		for node_type_name, count in problem_data ['nodes'] . items ():

			node_type = get_node_type (node_type_name, node_types)

			problem_node_types [node_type] = int (count)

	# Wells

	problem_well_configurations = defaultdict (dict)

	if 'wells' in problem_data:

		for well_configuration_data in problem_data ['wells']:

			well_type = get_well_type (
				well_configuration_data ['type'],
				well_types
			)

			well_configuration = get_well_configuration (
				well_type,
				well_configuration_data
			)

			if 'count' in well_configuration_data:

				count = int (well_data ['count'])

			else:

				count = 1

			problem_well_configurations [well_type] [well_configuration] = count

	# Recipes

	included_recipes = problem_data ['included_recipes']

	problem_recipes = set ()

	for included_recipe in included_recipes:

		problem_recipes |= get_recipe_set (
			included_recipe,
			all_recipes,
			groups
		)

	if 'excluded_recipes' in problem_data:

		excluded_recipes = problem_data ['excluded_recipes']

		for excluded_recipe in excluded_recipes:

			problem_recipes -= get_recipe_set (
				excluded_recipe,
				all_recipes,
				groups
			)

	(
		problem_node_recipes,
		problem_well_recipes,
		problem_processing_recipes
	) = filter_recipe_sets (
		problem_recipes,
		node_recipes,
		well_recipes,
		processing_recipes
	)

	# Input items

	if 'input_items' in problem_data:

		input_items = get_item_quantities (
			problem_data ['input_items'],
			items
		)

	else:

		input_items = dict ()

	# Output items

	if 'output_items' in problem_data:

		output_items = get_item_quantities (
			problem_data ['output_items'],
			items
		)

	else:

		output_items = dict ()

	# Overclocking

	overclocking = defaultdict (lambda: get_overclock_limits ({}))

	if 'overclocking' in problem_data:

		for recipe_name, overclock_limits_data in (
			problem_data ['overclocking'] . items ()
		):

			overclock_limits = get_overclock_limits (overclock_limits_data)

			for recipe in get_recipe_set (recipe_name, all_recipes, groups):

				overclocking [recipe] = overclock_limits

	# Power Consumption

	if 'max_power_consumption' in problem_data:

		max_power_consumption = utils . real (
			problem_data ['max_power_consumption']
		)

	else:

		max_power_consumption = None

	# Objective Functions

	if 'optimization_goals' in problem_data:

		objective_functions_data = problem_data ['optimization_goals']

		objective_functions = list (
			get_objective_function (function_type, function_data, items)
			for function_type, function_data in objective_functions_data
		)

	else:

		objective_functions = list ()

	return Problem (
		problem_node_types,
		problem_well_configurations,
		problem_node_recipes,
		problem_well_recipes,
		problem_processing_recipes,
		input_items,
		output_items,
		overclocking,
		max_power_consumption,
		objective_functions
	)
