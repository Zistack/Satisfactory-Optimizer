import commentjson

from z3 import *

from well_type import get_well_type
from item import get_item
from machine import get_machine

from purity_output import PurityOutput
from recipe import Recipe

class WellRecipe:

	def __init__ (
		self,
		pretty_name,
		well_type,
		resource,
		purity_rates,
		machine,
		power_consumption,
		overclock_exponent
	):

		self . pretty_name = pretty_name

		self . well_type = well_type
		self . resource = resource
		self . purity_rates = purity_rates

		self . machine = machine
		self . power_consumption = power_consumption
		self . overclock_exponent = overclock_exponent

class ConfiguredWellRecipe:

	def __init__ (self, well_recipe, well_configuration):

		pretty_name = (
			well_recipe . pretty_name + ' ' + well_configuration . pretty_name
		)

		self . recipe = Recipe (
			well_recipe . machine,
			well_recipe . power_consumption,
			well_recipe . overclock_exponent
		)

		self . purity_outputs = dict ()

		for purity, count in well_configuration . purity_counts . keys ():

			purity_output_pretty_name = pretty_name + ' ' + purity

			rate = well_recipe . purity_rates [purity]

			self . purity_outputs [purity] = PurityOutput (
				purity_output_pretty_name,
				rate,
				count
			)

	def output_rate (self, item):

		assert (item == self . resource)

		return sum (
			purity_output . output_rate (self . recipe . machine_count_variable)
			for purity_output in self . purity_outputs . values ()
		)

	def add_constraints (self, solver, overclock_limits):

		recipe_constraints = self . recipe . add_constraints (overclock_limits)

		for purity_output in self . purity_outputs . values ():

			purity_output . add_constraints (
				solver,
				self . recipe . magnitude_variable
			)

			if self . resource != None:

				purity_output . add_resource_flow_constraints (
					solver,
					self . resource,
					self . recipe . machine_count_variable
				)

	def interpret_model (self, model):

		self . interpretation = recipe . interpret_model (model)

		if interpretation == None:

			return None

		interpretation ['output'] = {
			self . resource . pretty_name:
				str (model . eval (self . output_rate (self . resource)))
		}

		return interpretation

def get_purity_rates (purity_rates_data):

	return dict (
		(purity, RealVal (rate))
		for purity, rate in purity_rates_data . items ()
	)

def get_well_recipe (
	well_recipe_pretty_name,
	well_recipe_data,
	well_types,
	items,
	machines
):

	well_type = get_well_type (
		well_recipe_data ['well_type'],
		well_types
	)

	resource = get_item (well_recipe_data ['resource'], items)
	purity_rates = get_purity_rates (
		well_recipe_data ['purity_rates']
	)

	machine = get_machine (well_recipe_data ['machine'], machines)
	power_consumption = RealVal (well_recipe_data ['power_consumption'])

	if 'overclock_exponent' in well_recipe_data:

		overclock_exponent = float (well_recipe_data ['overclock_exponent'])

	else:

		overclock_exponent = None

	return WellRecipe (
		well_recipe_pretty_name,
		well_type,
		resource,
		purity_rates,
		machine,
		power_consumption,
		overclock_exponent
	)
