import linprog as lp

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

			if self . power_consumption >= 0:

				self . overclock_exponent = 1.6

			else:

				self . overclock_exponent = 1 / 1.3

		self . name = utils . name (pretty_name)

		self . machine_count_variable = lp . Variable (
			self . name + '_machine_count',
		)
		self . magnitude_variable = lp . Variable (self . name + '_magnitude')
		self . power_consumption_variable = lp . Variable (
			self . name + '_power_consumption'
		)

		self . linear_magnitude_variable = lp . Variable (
			self . name + '_linear_magnitude',
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
				overclock_limits . power_factors (self . overclock_exponent)
			)
		)

	def __magnitude (self, machine_count_variables, overclock_limits):

		if self . power_consumption >= 0:

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

		return (
			self . power_consumption
			* self . __power_magnitude (
				machine_count_variables,
				overclock_limits
			)
		)

	def add_constraints (self, constraints, overclock_limits):

		machine_count_variables = list (
			lp . Variable (
				self . name + '_machine_count_clock_' + str (scaled_clock_speed)
			)
			for scaled_clock_speed
			in overclock_limits . scaled_clock_speeds ()
		)

		for machine_count_variable in machine_count_variables:

			constraints . append (machine_count_variable >= 0)

		constraints . append (self . machine_count_variable >= 0)
		constraints . append (
			self . machine_count_variable == sum (machine_count_variables)
		)
		constraints . append (self . magnitude_variable >= 0)
		constraints . append (
			self . magnitude_variable == self . __magnitude (
				machine_count_variables,
				overclock_limits
			)
		)
		constraints . append (
			self . power_consumption_variable == self . __power_consumption (
				machine_count_variables,
				overclock_limits
			)
		)

		constraints . append (self . linear_magnitude_variable >= 0)
		constraints . append (
			self . linear_magnitude_variable == self . __linear_magnitude (
				machine_count_variables,
				overclock_limits
			)
		)

	def interpret_model (self, model, precision):

		machine_count = model [self . machine_count_variable]

		if utils . interpret_approximate (machine_count, precision) == 0:

			return None

		results = {
			'machine_count': utils . format_value (machine_count, precision)
		}

		clock_speed = (
			model [self . linear_magnitude_variable]
			/ model [self . machine_count_variable]
		)

		if utils . interpret_approximate (clock_speed, precision) != 1:

			results ['clock_speed'] = utils . format_value (
				clock_speed,
				precision
			)

		results ['power_consumption'] = (
			utils . format_value (
				model [self . power_consumption_variable],
				precision
			)
		)

		return results
