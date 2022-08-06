import linprog as lp

import utils

class WellConfiguration:

	def __init__ (self, pretty_name, purity_counts):

		self . pretty_name = pretty_name

		self . purity_counts = purity_counts

		name = utils . name (pretty_name)

		self . allocation_variable = lp . Variable (name + '_allocation')

	def add_constraints (self, constraints, consuming_recipes):

		constraints . append (self . allocation_variable >= 0)
		constraints . append (
			self . allocation_variable == sum (
				well_recipe . recipe . machine_count_variable
				for well_recipe in consuming_recipes
			)
		)

def get_purity_counts (purity_counts_data):

	return dict (
		(purity, int (count))
		for purity, count in purity_counts_data . items ()
	)

def get_well_configuration (well_type, well_configuration_data):

	purity_counts = get_purity_counts (well_configuration_data ['satellites'])

	pretty_name = ' ' . join (
		[well_type . pretty_name]
		+ [
			str (count) + ' ' + purity
			for purity, count in purity_counts . items ()
		]
	)

	return WellConfiguration (pretty_name, purity_counts)
