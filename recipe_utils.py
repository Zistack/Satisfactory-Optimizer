import commentjson

from collections import defaultdict

from recipe import load_raw_recipe
from well_recipe import load_well_recipe

def load_tags (recipe_data):

	if 'tags' in recipe_data:

		return recipe_data ['tags']

	else:

		return []

def load_recipes (recipes_file_name, machines, well_types, node_types, items):

	with open (recipes_file_name, 'r') as recipes_file:

		recipes_data = commentjson . load (recipes_file)

	searchable_recipes = dict ()
	power_augmentation_recipes = dict ()

	groups = defaultdict (set)

	for recipe_pretty_name, recipe_data in recipes_data . items ():

		if 'well_type' in recipe_data:

			recipe = load_well_recipe (
				recipe_pretty_name,
				recipe_data,
				machines,
				well_types,
				items
			)

		else:

			recipe = load_raw_recipe (
				recipe_pretty_name,
				recipe_data,
				machines,
				node_types,
				items
			)


		if recipe . power_augmentation_factor == None:

			searchable_recipes [recipe_pretty_name] = recipe

			for tag in load_tags (recipe_data):

				groups [tag] . add (recipe)

		else:

			power_augmentation_recipes [recipe_pretty_name] = recipe

	return searchable_recipes, power_augmentation_recipes, groups

def get_recipe (recipe_name, recipe_bank):

	if recipe_name not in recipe_bank:

		raise ValueError (
			'\'' + recipe_name + '\' does not name a valid recipe'
		)

	return recipe_bank [recipe_name]

def get_recipe_set (meta_recipe_name, searchable_recipes, groups):

	if meta_recipe_name in groups:

		return groups [meta_recipe_name]

	else:

		return {get_recipe (meta_recipe_name, searchable_recipes)}
