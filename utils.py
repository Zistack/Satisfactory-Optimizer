from z3 import *

def variable_name (pretty_name):

	return (
		''.join (c if c . isalnum () else '_' for c in pretty_name) . lower ()
	)

def get_item_quantities (item_quantities_data, items):

	item_quantities = dict ()

	for item_name, quantity in item_quantities_data . items ():

		item = get_item (item_name, items)

		item_quantity = (
			'unlimited' if quantity == 'unlimited' else RealVal (quantity)
		)

		item_quantities [item] = item_quantity

	return item_quantities

def get_finite_item_quantities (item_quantities_data, items):

	item_quantities = dict ()

	for item_name, quantity in item_quantities_data . items ():

		item = get_item (item_name, items)

		item_quantity = RealVal (quantity)

		item_quantities [item] = item_quantity

	return item_quantities

def get_item (item_name, items):

	if item_name not in items:

		raise ValueError ('\'' + item_name + '\' does not name a valid item')

	return items [item_name]

def get_machine (machine_name, machines):

	if machine_name not in machines:

		raise ValueError (
			'\'' + machine_name + '\' does not name a valid machine'
		)

	return machines [machine_name]

def get_recipe (recipe_name, recipes):

	if recipe_name not in recipes:

		raise ValueError (
			'\'' + recipe_name + '\' does not name a valid recipe'
		)

	return recipes [recipe_name]

def second_is_not_none (tuple):

	first, second = tuple

	return second != None
