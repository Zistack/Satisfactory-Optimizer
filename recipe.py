from z3 import *

import utils

class Recipe:

	def __init__ (
		self,
		pretty_name,
		machine,
		power_consumption,
		overclock_exponent
	):

		self . machine = machine
		self . power_consumption = power_consumption

		if overclock_exponent != None:

			self . overclock_exponent = overclock_exponent

		else:

			if simplify (self . power_consumption >= 0):

				self . overclock_exponent = 1.6

			else:

				self . overclock_exponent = 1 / 1.3

		self . name = utils . name (pretty_name)

		self . machine_count_variable = Real (self . name + '_machine_count')
		self . magnitude_variable = Real (self . name + '_magnitude')
		self . power_consumption_variable = Real (
			self . name + '_power_consumption'
		)

		self . linear_magnitude_variable = Real (
			self . name + '_linear_magnitude'
		)

	def __linear_magnitude (self, machine_count_variables, overclock_limits):

		return sum (
			machine_count_variable * clock_speed
			for machine_count_variable, clock_speed
			in zip (machine_count_variables, overclock_limits . clock_speeds ())
		)

	def __power_magnitude (self, machine_count_variables, overclock_limits):

			return sum (
				machine_count_variable * power_factor
				for machine_count_variable, power_factor
				in zip (
					machine_count_variables,
					overclock_limits . power_factors (
						self . overclock_exponent
					)
				)
			)

	def __magnitude (self, machine_count_variables, overclock_limits):

		if simplify (self . power_consumption >= 0):

			return self . __linear_magnitude (
				machine_count_variables,
				overclock_limits
			)

		else:

			return self . __power_magnitude (
				machine_count_variables,
				overclock_limits
			)

	def __power_consumption (self, machine_count_variables, overclock_limits):

		return self . power_consumption * sum (
			machine_count_variable * power_factor
			for machine_count_variable, power_factor
			in zip (
				machine_count_variables,
				overclock_limits . power_factors (self . overclock_exponent)
			)
		)

	def add_constraints (self, solver, overclock_limits):

		machine_count_variables = list (
			Real (
				self . name + '_machine_count_clock_' + str (scaled_clock_speed)
			)
			for scaled_clock_speed
			in overclock_limits . scaled_clock_speeds ()
		)

		for machine_count_variable in machine_count_variables:

			solver . add (machine_count_variable >= 0)

		solver . add (
			self . machine_count_variable == sum (machine_count_variables)
		)
		solver . add (
			self . magnitude_variable == self . __magnitude (
				machine_count_variables,
				overclock_limits
			)
		)
		solver . add (
			self . power_consumption_variable == self . __power_consumption (
				machine_count_variables,
				overclock_limits
			)
		)

		solver . add (
			self . linear_magnitude_variable == self . __linear_magnitude (
				machine_count_variables,
				overclock_limits
			)
		)

	def interpret_model (self, model):

		machine_count = model . eval (self . machine_count_variable)

		if machine_count == 0:

			return None

		results = {'machine_count': str (machine_count)}

		clock_speed = model . eval (
			self . linear_magnitude_variable / self . machine_count_variable
		)

		if simplify (clock_speed != 1):

			results ['clock_speed'] = str (clock_speed)

		results ['power_consumption'] = (
			str (model . eval (self . power_consumption_variable))
		)

		return results
