import linprog as lp

import utils

class WellConfiguration:

	def __init__ (self, pretty_name, purity_counts):

		self . pretty_name = pretty_name
		self . purity_counts = purity_counts

	def add_constraints (self, constraints, count, consuming_recipes):

		constraints . append (
			sum (recipe . machine_count () for recipe in consuming_recipes)
			<= count
		)

def load_purity_counts (purity_counts_data):

	return dict (
		(purity, int (count))
		for purity, count in purity_counts_data . items ()
	)

def load_well_configuration (well_type, well_configuration_data):

	purity_counts = load_purity_counts (well_configuration_data ['satellites'])

	pretty_name = ' ' . join (
		[well_type]
		+ [
			str (count) + ' ' + purity
			for purity, count in purity_counts . items ()
		]
	)

	return WellConfiguration (pretty_name, purity_counts)
