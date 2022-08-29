import commentjson

from collections import defaultdict

from node_recipe import get_node_recipe
from well_recipe import WellRecipe, get_well_recipe
from processing_recipe import get_processing_recipe

def get_tags (recipe_data):

	if 'tags' in recipe_data:

		return recipe_data ['tags']

	else:

		return []

def load_recipes (recipes_file_name, node_types, well_types, items, machines):

	with open (recipes_file_name, 'r') as recipes_file:

		recipes_data = commentjson . load (recipes_file)

	all_recipes = dict ()
	node_recipes = dict ()
	well_recipes = defaultdict (dict)
	processing_recipes = dict ()
	groups = defaultdict (set)

	for recipe_pretty_name, recipe_data in recipes_data . items ():

		if 'node_type' in recipe_data:

			recipe = get_node_recipe (
				recipe_pretty_name,
				recipe_data,
				node_types,
				items,
				machines
			)

			node_recipes [recipe_pretty_name] = recipe

		elif 'well_type' in recipe_data:

			recipe = get_well_recipe (
				recipe_pretty_name,
				recipe_data,
				well_types,
				items,
				machines
			)

			well_recipes [recipe . well_type] [recipe_pretty_name] = recipe

		else:

			recipe = get_processing_recipe (
				recipe_pretty_name,
				recipe_data,
				items,
				machines
			)

			processing_recipes [recipe_pretty_name] = recipe

		all_recipes [recipe_pretty_name] = recipe

		for tag in get_tags (recipe_data):

			groups [tag] . add (recipe)

	return all_recipes, node_recipes, well_recipes, processing_recipes, groups

def get_recipe (recipe_name, all_recipes):

	if recipe_name not in all_recipes:

		raise ValueError (
			'\'' + recipe_name + '\' does not name a valid recipe'
		)

	return all_recipes [recipe_name]

def get_recipe_set (meta_recipe_name, all_recipes, groups):

	if meta_recipe_name in groups:

		return groups [meta_recipe_name]

	else:

		return {get_recipe (meta_recipe_name, all_recipes)}

def make_recipe_set_concrete (
	recipe_set,
	well_configurations,
	configured_well_recipes
):

	concrete_recipe_set = set ()

	for recipe in recipe_set:

		if type (recipe) == WellRecipe:

			for well_configuration in well_configurations [recipe . well_type]:

				concrete_recipe_set . add (
					configured_well_recipes [(recipe, well_configuration)]
				)

		else:

			concrete_recipe_set . add (recipe)

	return concrete_recipe_set

def filter_recipe_sets (
	used_recipes,
	node_recipes,
	well_recipes,
	processing_recipes
):

	def recipe_in_used_recipes (recipe_pair):

		name, recipe = recipe_pair

		return recipe in used_recipes

	used_node_recipes = dict (
		filter (recipe_in_used_recipes, node_recipes . items ())
	)

	used_well_recipes = defaultdict (dict)

	for well_type, well_type_recipes in well_recipes . items ():

		used_well_recipes [well_type] = dict (
			filter (recipe_in_used_recipes, well_type_recipes . items ())
		)

	used_processing_recipes = dict (
		filter (recipe_in_used_recipes, processing_recipes . items ())
	)

	return used_node_recipes, used_well_recipes, used_processing_recipes
