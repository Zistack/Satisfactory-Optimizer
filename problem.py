import commentjson
import sys

from collections import defaultdict
import linprog as lp

import utils

from node_type import get_node_type
from well_type import get_well_type
from well_configuration import load_well_configuration
from item import load_item_quantities
from well_recipe import WellRecipe
from recipe import RawRecipe
from recipe_utils import get_recipe, get_recipe_set
from recipe_registry import RecipeRegistry
from overclock_limits import load_overclock_limits

from objective_function import load_objective_function

class Problem:

	def __init__ (
		self,
		node_types,
		well_configurations,
		searchable_recipes,
		input_items,
		output_items,
		overclock_limits,
		max_power_consumption,
		available_somersloops,
		power_augmentation_recipes,
		max_machine_count,
		objective_functions,
		minimize_machine_count
	):

		self . node_types = node_types
		self . well_configurations = well_configurations
		self . searchable_recipes = searchable_recipes
		self . input_items = input_items
		self . output_items = output_items
		self . overclock_limits = overclock_limits
		self . available_somersloops = available_somersloops
		self . power_augmentation_recipes = power_augmentation_recipes
		self . max_power_consumption = max_power_consumption
		self . max_machine_count = max_machine_count
		self . objective_functions = objective_functions
		self . minimize_machine_count = minimize_machine_count

	def __model_productivity (self):

		return self . available_somersloops != 0

	def __encode_recipe (self, constraints, recipe, recipe_registry):

		if type (recipe) == RawRecipe:

			encoded_recipe = recipe . encode (
				constraints,
				self . overclock_limits [recipe],
				self . __model_productivity ()
			)

			recipe_registry . register_recipe (recipe, encoded_recipe)

			return [encoded_recipe]

		if type (recipe) == WellRecipe:

			encoded_recipes = list ()

			for well_configuration \
			in self . well_configurations [recipe . well_type] . keys ():

				raw_recipe = recipe . specialize (well_configuration)

				encoded_recipe = raw_recipe . encode (
					constraints,
					self . overclock_limits [recipe],
					self . __model_productivity ()
				)

				recipe_registry . register_recipe (raw_recipe, encoded_recipe)
				recipe_registry . register_well_recipe (recipe, encoded_recipe)

				encoded_recipes . append (encoded_recipe)

			return encoded_recipes

	def __encode_recipes (self, constraints):

		print ('Encoding recipes', file = sys . stderr)

		recipe_registry = RecipeRegistry ()
		total_power_augmentation_factor = 0

		for recipe in self . searchable_recipes:

			self . __encode_recipe (constraints, recipe, recipe_registry)

		for power_augmentation_recipe, machine_count \
		in self . power_augmentation_recipes . items ():

			encoded_recipes = self . __encode_recipe (
				constraints,
				power_augmentation_recipe,
				recipe_registry
			)

			constraints . append (
				sum (
					encoded_recipe . machine_count ()
					for encoded_recipe in encoded_recipes
				)
				== machine_count
			)

			total_power_augmentation_factor += (
				machine_count
				* power_augmentation_recipe . power_augmentation_factor
			)

		return (
			recipe_registry,
			total_power_augmentation_factor
		)

	def __encode_somersloops (self, constraints, recipe_registry):

		total_allocated_somersloops = sum (
			recipe . allocated_somersloops ()
			for recipe in recipe_registry . somersloop_allocating_recipes
		)

		constraints . append (total_allocated_somersloops >= 0)
		constraints . append (
			total_allocated_somersloops <= self . available_somersloops
		)

	def __encode_node_types (self, constraints, recipe_registry):

		print ('Encoding nodes', file = sys . stderr)

		for node_type, consuming_recipes \
		in recipe_registry . node_type_consuming_recipes . items ():

			if node_type in self . node_types:

				count = self . node_types [node_type]

			else:

				count = 0

			constraints . append (
				sum (recipe . machine_count () for recipe in consuming_recipes)
				<= count
			)

	def __encode_well_configurations (self, constraints, recipe_registry):

		print ('Encoding wells', file = sys . stderr)

		for well_type, well_configurations in (
			self . well_configurations . items ()
		):

			for well_configuration, count in well_configurations . items ():

				well_configuration . add_constraints (
					constraints,
					count,
					recipe_registry . well_configuration_consuming_recipes [
						well_configuration
					]
				)

	def __input_rate (self, item):

		if item in self . input_items:

			return self . input_items [item]

		else:

			return 0.0

	def __output_rate (self, item):

		if item in self . output_items:

			return self . output_items [item]

		else:

			return 0.0

	def __encode_items (self, constraints, recipe_registry):

		print ('Encoding items', file = sys . stderr)

		used_items = set ()

		used_items |= self . input_items . keys ()
		used_items |= self . output_items . keys ()

		used_items |= recipe_registry . item_producing_recipes . keys ()
		used_items |= recipe_registry . item_consuming_recipes . keys ()

		for item in used_items:

			item . add_constraints (
				constraints,
				recipe_registry . item_producing_recipes [item],
				recipe_registry . item_consuming_recipes [item],
				self . __input_rate (item),
				self . __output_rate (item)
			)

		return used_items

	# This whole step is arguably a complete no-op now.
	def __encode_machines (self, constraints, recipe_registry):

		print ('Encoding machines', file = sys . stderr)

		for machine, using_recipes \
		in recipe_registry . machine_using_recipes . items ():

			machine . add_constraints (
				constraints,
				recipe_registry . machine_using_recipes [machine]
			)

	def __net_power_consumption (
		self,
		recipe_registry,
		total_power_augmentation_factor
	):

		(
			total_power_production,
			augmented_power_production,
			total_power_consumption
		) = self . __net_power_consumption_parts (
			recipe_registry,
			total_power_augmentation_factor
		)

		return total_power_consumption - augmented_power_production

	def __net_power_consumption_parts (
		self,
		recipe_registry,
		total_power_augmentation_factor
	):

		total_power_production = sum (
			- recipe . power_consumption ()
			for recipe in recipe_registry . power_producing_recipes
		)

		augmented_power_production = (
			total_power_production
			* (1 + total_power_augmentation_factor)
		)

		total_power_consumption = sum (
			recipe . power_consumption ()
			for recipe in recipe_registry . power_consuming_recipes
		)

		return (
			total_power_production,
			augmented_power_production,
			total_power_consumption
		)

	def __encode_power_consumption (
		self,
		constraints,
		recipe_registry,
		total_power_augmentation_factor
	):

		print ('Encoding total power consumption', file = sys . stderr)

		if self . max_power_consumption == None:

			return

		constraints . append (
			self . __net_power_consumption (
				recipe_registry,
				total_power_augmentation_factor
			)
			<= self . max_power_consumption
		)

	def __total_machine_count (self, recipe_registry):

		return sum (
			machine . total_count (using_recipes)
			for machine, using_recipes
			in recipe_registry . machine_using_recipes . items ()
		)

	def __encode_machine_count (self, constraints, recipe_registry):

		print ('Encoding total machine count', file = sys . stderr)

		if self . max_machine_count == None:

			return

		constraints . append (
			self . __total_machine_count (recipe_registry)
			<= self . max_machine_count
		)

	def __encode_objective_functions (
		self,
		constraints,
		objectives,
		recipe_registry,
		total_power_augmentation_factor
	):

		print ('Encoding objective functions', file = sys . stderr)

		for objective_function in self . objective_functions:

			objective_function . add_objective (
				constraints,
				objectives,
				recipe_registry
			)

		if (self . minimize_machine_count):

			objectives . append (self . __total_machine_count (recipe_registry))

		else:

			objectives . append (
				self . __net_power_consumption (
					recipe_registry,
					total_power_augmentation_factor
				)
			)

	def __interpret_model (
		self,
		model,
		precision,
		recipe_registry,
		total_power_augmentation_factor,
		used_items
	):

		interpreted_recipe_registry = (
			recipe_registry . interpret (model, precision)
		)

		def has_report (tuple):

			name, report = tuple

			return report != None

		searchable_recipe_interpretations = dict (
			filter (
				has_report,
				[
					(
						interpreted_searchable_recipe . pretty_name (),
						interpreted_searchable_recipe . get_report (precision)
					)
					for interpreted_searchable_recipe
					in interpreted_recipe_registry . get_interpreted_recipes (
						self . searchable_recipes
					)
				]
			)
		)

		power_augmentation_recipe_interpretations = dict (
			filter (
				has_report,
				[
					(
						interpreted_power_augmentation_recipe . pretty_name (),
						interpreted_power_augmentation_recipe
							. get_report (precision)
					)
					for interpreted_power_augmentation_recipe
					in interpreted_recipe_registry . get_interpreted_recipes (
						self . power_augmentation_recipes . keys ()
					)
				]
			)
		)

		item_interpretations = dict (
			filter (
				has_report,
				[
					(
						item . pretty_name,
						item . interpret (
							model,
							precision,
							interpreted_recipe_registry
								. item_producing_recipes [item],
							interpreted_recipe_registry
								. item_consuming_recipes [item],
							self . __input_rate (item),
							self . __output_rate (item)
						)
					)
					for item in used_items
				]
			)
		)

		machine_interpretations = dict (
			filter (
				has_report,
				[
					(
						machine . pretty_name,
						machine . interpret (model, precision, using_recipes)
					)
					for machine, using_recipes
					in interpreted_recipe_registry
						. machine_using_recipes
						. items ()
				]
			)
		)

		(
			power_production,
			augmented_power_production,
			power_consumption
		) = self . __net_power_consumption_parts (
			interpreted_recipe_registry,
			total_power_augmentation_factor
		)

		power_production_value = utils . format_value (
			power_production,
			precision
		)

		augmented_power_production_value = utils . format_value (
			augmented_power_production,
			precision
		)

		power_consumption_value = utils . format_value (
			power_consumption,
			precision
		)

		net_power_consumption_value = utils . format_value (
			power_consumption - augmented_power_production,
			precision
		)

		total_machine_count_value = utils . format_value (
			self . __total_machine_count (interpreted_recipe_registry),
			precision
		)

		report = {
			'items': item_interpretations,
			'machines': machine_interpretations,
			'recipes': searchable_recipe_interpretations,
			'power_augmentation_recipes':
				power_augmentation_recipe_interpretations,
		}

		report ['power_consumption'] = power_consumption_value

		if power_production != 0:

			report ['power_production'] = power_production_value

			if augmented_power_production != power_production:

				report ['augmented_power_production'] = augmented_power_production_value

			report ['net_power_consumption'] = net_power_consumption_value

		report ['total_machine_count'] = total_machine_count_value

		return report

	def solve (self, precision):

		print ('Encoding problem', file = sys . stderr)

		constraints = list ()
		objectives = list ()

		(
			recipe_registry,
			total_power_augmentation_factor
		) = self . __encode_recipes (constraints)

		self . __encode_somersloops (constraints, recipe_registry)

		self . __encode_node_types (constraints, recipe_registry)

		self . __encode_well_configurations (constraints, recipe_registry)

		used_items = self . __encode_items (constraints, recipe_registry)

		self . __encode_machines (constraints, recipe_registry)

		self . __encode_power_consumption (
			constraints,
			recipe_registry,
			total_power_augmentation_factor
		)

		self . __encode_machine_count (constraints, recipe_registry)

		self . __encode_objective_functions (
			constraints,
			objectives,
			recipe_registry,
			total_power_augmentation_factor
		)

		print ('Solving problem', file = sys . stderr)

		model = lp . solve (constraints, objectives)

		if model == None:

			return None

		print ('Interpreting model', file = sys . stderr)

		return self . __interpret_model (
			model,
			precision,
			recipe_registry,
			total_power_augmentation_factor,
			used_items
		)

def load_problem (
	problem_file_name,
	node_types,
	well_types,
	items,
	searchable_recipes,
	power_augmentation_recipes,
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

			well_configuration = load_well_configuration (
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

	problem_searchable_recipes = set ()

	for included_recipe in included_recipes:

		problem_searchable_recipes |= get_recipe_set (
			included_recipe,
			searchable_recipes,
			groups
		)

	if 'excluded_recipes' in problem_data:

		excluded_recipes = problem_data ['excluded_recipes']

		for excluded_recipe in excluded_recipes:

			problem_searchable_recipes -= get_recipe_set (
				excluded_recipe,
				searchable_recipes,
				groups
			)

	# Input items

	if 'input_items' in problem_data:

		problem_input_items = load_item_quantities (
			problem_data ['input_items'],
			items
		)

	else:

		problem_input_items = dict ()

	# Output items

	if 'output_items' in problem_data:

		problem_output_items = load_item_quantities (
			problem_data ['output_items'],
			items
		)

	else:

		problem_output_items = dict ()

	# Overclocking

	problem_overclock_limits = defaultdict (lambda: None)

	if 'overclocking' in problem_data:

		for recipe_name, overclock_limits_data in (
			problem_data ['overclocking'] . items ()
		):

			overclock_limits = load_overclock_limits (overclock_limits_data)

			for recipe in get_recipe_set (recipe_name, searchable_recipes, groups):

				if not recipe . supports_overclocking ():

					raise ValueError (
						'\'' + recipe_name + '\' does not support overclocking'
					)

				problem_overclock_limits [recipe] = overclock_limits

	# Power Consumption

	if 'max_power_consumption' in problem_data:

		problem_max_power_consumption = utils . real (
			problem_data ['max_power_consumption']
		)

	else:

		problem_max_power_consumption = None

	# Available Somersloops

	if 'available_somersloops' in problem_data:

		problem_available_somersloops = utils . real (
			problem_data ['available_somersloops']
		)

	else:

		problem_available_somersloops = 0

	# Power Augmentation

	problem_power_augmentation_recipes = dict ()

	if 'power_augmentation' in problem_data:

		for recipe_name, machine_count \
		in problem_data ['power_augmentation'] . items ():

			recipe = get_recipe (recipe_name, power_augmentation_recipes)
			machine_count = utils . real (machine_count)

			problem_power_augmentation_recipes [recipe] = machine_count

	# Machine Count

	if 'max_machine_count' in problem_data:

		problem_max_machine_count = utils . real (
			problem_data ['max_machine_count']
		)

	else:

		problem_max_machine_count = None

	# Objective Functions

	if 'optimization_goals' in problem_data:

		objective_functions_data = problem_data ['optimization_goals']

		problem_objective_functions = list (
			load_objective_function (
				function_type,
				function_data,
				items,
				searchable_recipes,
				groups
			)
			for function_type, function_data in objective_functions_data
		)

	else:

		problem_objective_functions = list ()

	# Passive Minimization

	if 'minimize_machine_count' in problem_data:

		problem_minimize_machine_count = bool (
			problem_data ['minimize_machine_count']
		)

	else:

		problem_minimize_machine_count = False

	return Problem (
		problem_node_types,
		problem_well_configurations,
		problem_searchable_recipes,
		problem_input_items,
		problem_output_items,
		problem_overclock_limits,
		problem_max_power_consumption,
		problem_available_somersloops,
		problem_power_augmentation_recipes,
		problem_max_machine_count,
		problem_objective_functions,
		problem_minimize_machine_count
	)
