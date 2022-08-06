import linprog as lp

import utils

class PurityOutput:

	def __init__ (self, pretty_name, rate, count):

		self . rate = rate
		self . count = count

		name = utils . name (pretty_name)

		self . rate_variable = lp . Variable (name + '_rate')

	def add_constraints (self, constraints, magnitude):

		constraints . append (self . rate_variable >= 0)
		constraints . append (
			self . rate_variable <= self . rate * self . count * magnitude
		)

	def add_resource_flow_constraints (
		self,
		constraints,
		resource,
		machine_count
	):

		resource . constrain_total_flow_rate (
			constraints,
			self . rate_variable,
			self . count * machine_count
		)
