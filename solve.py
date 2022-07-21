from z3 import *

import utils

def solve (problem, items, machines, recipes):

	solver = Optimize ()
	solver . set (priority = 'lex')

	for item in items . values ():

		item . add_constraints (solver)

	for machine in machines . values ():

		machine . add_constraints (solver)

	for recipe in recipes . values ():

		recipe . add_constraints (solver)

	problem . add_constraints (solver, items, recipes)

	problem . add_objective_functions (solver)

	# Solve

	if solver . check () != sat:

		return None

	# Report results

	model = solver . model ()

	item_interpretations = dict (
		(item_name, item . interpret_model (model))
		for item_name, item in items . items ()
	)

	item_results = dict (
		filter (
			utils . second_is_not_none,
			item_interpretations . items ()
		)
	)

	recipe_interpretations = dict (
		(recipe_name, recipe . interpret_model (model))
		for recipe_name, recipe in recipes . items ()
	)

	recipe_results = dict (
		filter (
			utils . second_is_not_none,
			recipe_interpretations . items ()
		)
	)

	machine_interpretations = dict (
		(machine_name, machine . interpret_model (model))
		for machine_name, machine in machines . items ()
	)

	machine_results = dict (
		filter (
			utils . second_is_not_none,
			machine_interpretations . items ()
		)
	)

	total_power_consumption = str (
		model . eval (problem . total_power_consumption_variable)
	)

	return {
		'items': item_results,
		'recipes': recipe_results,
		'machines': machine_results,
		'total_power_consumption': total_power_consumption
	}
