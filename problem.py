import commentjson

from z3 import *

import utils

from optimization_goal import get_optimization_goal

class Problem:

	def __init__ (
		self,
		recipes,
		input_items,
		output_items,
		max_power_consumption,
		optimization_goals
	):

		self . recipes = recipes
		self . input_items = input_items
		self . output_items = output_items
		self . max_power_consumption = max_power_consumption
		self . optimization_goals = optimization_goals

		self . total_power_consumption_variable = Real (
			'total_power_consumption'
		)

	def input_item_constraints (self, items):

		constraints = list ()

		for item in items . values ():

			if item in self . input_items . keys ():

				input_quantity = self . input_items [item]

				if type (input_quantity) != str:

					constraints . append (
						item . input_variable == input_quantity
					)

			else:

				# We do not assume that materials are available by default
				constraints . append (item . input_variable == 0)

		return constraints

	def output_item_constraints (self, items):

		constraints = list ()

		for item in items . values ():

			if item in self . output_items . keys ():

				output_quantity = self . output_items [item]

				if type (output_quantity) != str:

					constraints . append (
						item . output_variable == output_quantity
					)

			# We do not constrain outputs by default.

		return constraints

	def total_power_consumption_calculation (self, recipes):

		return self . total_power_consumption_variable == sum (
			recipe . power_consumption_calculation ()
			for recipe in recipes . values ()
		)

	def add_constraints (self, solver, items, recipes):

		for recipe in recipes . values ():

			if recipe not in self . recipes:

				solver . add (recipe . machine_count_variable == 0)

		for input_item_constraint in self . input_item_constraints (items):

			solver . add (input_item_constraint)

		for output_item_constraint in self . output_item_constraints (items):

			solver . add (output_item_constraint)

		solver . add (self . total_power_consumption_calculation (recipes))

		if self . max_power_consumption != None:

			solver . add (
				self . total_power_consumption_variable
					<= self . max_power_consumption
			)

	def add_objective_functions (self, solver):

		for optimization_goal in self . optimization_goals:

			optimization_goal . add_objective_function (solver)

		solver . minimize (self . total_power_consumption_variable)

def get_recipe_set (meta_recipe_name, recipes, groups):

	if meta_recipe_name in groups:

		return groups [meta_recipe_name]

	return {utils . get_recipe (meta_recipe_name, recipes)}

def load_problem (problem_file_name, items, recipes, groups):

	with open (problem_file_name, 'r') as problem_file:

		problem_data = commentjson . load (problem_file)

	# Recipes

	included_recipes = problem_data ['included_recipes']

	problem_recipes = set ()

	for included_recipe in included_recipes:

		problem_recipes |= get_recipe_set (included_recipe, recipes, groups)

	if 'excluded_recipes' in problem_data:

		excluded_recipes = problem_data ['excluded_recipes']

		for excluded_recipe in excluded_recipes:

			problem_recipes -= get_recipe_set (included_recipe, recipes, groups)

	# Input items

	input_items = utils . get_item_quantities (
		problem_data ['input_items'],
		items
	)

	# Output items

	if 'output_items' in problem_data:

		output_items = utils . get_item_quantities (
			problem_data ['output_items'],
			items
		)

	else:

		output_items = dict ()

	# Power Consumption

	if 'max_power_consumption' in problem_data:

		max_power_consumption = RealVal (problem_data ['max_power_consumption'])

	else:

		max_power_consumption = None

	# Optimization Goals

	if 'optimization_goals' in problem_data:

		optimization_goals_data = problem_data ['optimization_goals']

		optimization_goals = list (
			get_optimization_goal (goal_type, goal_data, items, recipes)
			for goal_type, goal_data in optimization_goals_data
		)

	else:

		optimization_goals = list ()

	return Problem (
		problem_recipes,
		input_items,
		output_items,
		max_power_consumption,
		optimization_goals
	)
