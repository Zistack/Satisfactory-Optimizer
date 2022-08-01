from z3 import *

import utils

class PurityOutput:

	def __init__ (self, pretty_name, rate, count):

		self . rate = rate
		self . count = count

		name = utils . name (pretty_name)

		self . rate_variable = Real (name + '_rate')

	def add_constraints (self, solver, magnitude):

		solver . add (self . rate_variable >= 0)
		solver . add (
			self . rate_variable <= self . rate * self . count * magnitude
		)

	def add_resource_flow_constraints (self, solver, resource, machine_count):

		resource . constrain_total_flow_rate (
			solver,
			self . rate_variable,
			self . count * machine_count
		)
