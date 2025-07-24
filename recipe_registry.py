from collections import defaultdict

from well_recipe import WellRecipe
from recipe import RawRecipe

class RecipeRegistry:

	def __init__ (self):

		self . encoded_recipes = dict ()
		self . encoded_well_recipes = defaultdict (list)

		self . machine_using_recipes = defaultdict (list)

		self . power_producing_recipes = list ()
		self . power_consuming_recipes = list ()

		self . well_configuration_consuming_recipes = defaultdict (list)
		self . node_type_consuming_recipes = defaultdict (list)
		self . item_consuming_recipes = defaultdict (list)
		self . item_producing_recipes = defaultdict (list)

		self . somersloop_allocating_recipes = list ()

	def register_recipe (self, raw_recipe, encoded_recipe):

		self . encoded_recipes [raw_recipe] = encoded_recipe

		self . machine_using_recipes [
			raw_recipe . machine
		] . append (encoded_recipe)

		if raw_recipe . power_consumption < 0:

			self . power_producing_recipes . append (encoded_recipe)

		if raw_recipe . power_consumption > 0:

			self . power_consuming_recipes . append (encoded_recipe)

		if raw_recipe . well_configuration is not None:

			self . well_configuration_consuming_recipes [
				raw_recipe . well_configuration
			] . append (encoded_recipe)

		if raw_recipe . node_type is not None:

			self . node_type_consuming_recipes [
				raw_recipe . node_type
			] . append (encoded_recipe)

		for item in raw_recipe . input_items ():

			self . item_consuming_recipes [item] . append (encoded_recipe)

		for item in raw_recipe . output_items ():

			self . item_producing_recipes [item] . append (encoded_recipe)

		if (
			raw_recipe . supports_productivity ()
			or raw_recipe . requires_somersloops ()
		):

			self . somersloop_allocating_recipes . append (encoded_recipe)

	def register_well_recipe (self, well_recipe, encoded_recipe):

		self . encoded_well_recipes [well_recipe] . append (encoded_recipe)

	def get_encoded_recipes (self, recipe_set):

		encoded_recipes = set ()

		for recipe in recipe_set:

			if recipe in self . encoded_well_recipes:

				encoded_recipes |= set (self . encoded_well_recipes [recipe])

			else:

				encoded_recipes . add (self . encoded_recipes [recipe])

		return encoded_recipes

	def interpret (self, model, precision):

		interpreted_raw_recipes = dict ()
		interpreted_encoded_recipes = dict ()

		for raw_recipe, encoded_recipe in self . encoded_recipes . items ():

			interpreted_recipe = encoded_recipe . interpret (model, precision)

			interpreted_raw_recipes [raw_recipe] = interpreted_recipe
			interpreted_encoded_recipes [encoded_recipe] = interpreted_recipe

		interpreted_well_recipes = dict (
			(
				well_recipe,
				list (
					interpreted_encoded_recipes [encoded_recipe]
					for encoded_recipe in encoded_recipes
				)
			)
			for well_recipe, encoded_recipes
			in self . encoded_well_recipes . items ()
		)

		interpreted_machine_using_recipes = dict (
			(
				machine,
				list (
					interpreted_encoded_recipes [encoded_recipe]
					for encoded_recipe in using_recipes
				)
			)
			for machine, using_recipes
			in self . machine_using_recipes . items ()
		)

		interpreted_power_producing_recipes = list (
			interpreted_encoded_recipes [encoded_recipe]
			for encoded_recipe in self . power_producing_recipes
		)

		interpreted_power_consuming_recipes = list (
			interpreted_encoded_recipes [encoded_recipe]
			for encoded_recipe in self . power_consuming_recipes
		)

		interpreted_item_consuming_recipes = dict (
			(
				item,
				list (
					interpreted_encoded_recipes [encoded_recipe]
					for encoded_recipe in consuming_recipes
				)
			)
			for item, consuming_recipes
			in self . item_consuming_recipes . items ()
		)

		interpreted_item_producing_recipes = dict (
			(
				item,
				list (
					interpreted_encoded_recipes [encoded_recipe]
					for encoded_recipe in producing_recipes
				)
			)
			for item, producing_recipes
			in self . item_producing_recipes . items ()
		)

		return InterpretedRecipeRegistry (
			interpreted_raw_recipes,
			interpreted_well_recipes,
			interpreted_machine_using_recipes,
			interpreted_power_producing_recipes,
			interpreted_power_consuming_recipes,
			interpreted_item_consuming_recipes,
			interpreted_item_producing_recipes
		)

class InterpretedRecipeRegistry:

	def __init__ (
		self,
		interpreted_recipes,
		interpreted_well_recipes,
		machine_using_recipes,
		power_producing_recipes,
		power_consuming_recipes,
		item_consuming_recipes,
		item_producing_recipes
	):

		self . interpreted_recipes = interpreted_recipes
		self . interpreted_well_recipes = interpreted_well_recipes

		self . machine_using_recipes = machine_using_recipes
		self . power_producing_recipes = power_producing_recipes
		self . power_consuming_recipes = power_consuming_recipes
		self . item_consuming_recipes = item_consuming_recipes
		self . item_producing_recipes = item_producing_recipes

	def get_interpreted_recipes (self, recipe_set):

		output_interpreted_recipes = set ()

		for recipe in recipe_set:

			if type (recipe) == WellRecipe:

				if recipe in self . interpreted_well_recipes:

					output_interpreted_recipes |= set (
						self . interpreted_well_recipes [recipe]
					)

			elif type (recipe) == RawRecipe:

				output_interpreted_recipes . add (
					self . interpreted_recipes [recipe]
				)

		return output_interpreted_recipes
