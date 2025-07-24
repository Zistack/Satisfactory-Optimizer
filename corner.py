import linprog as lp

import utils

class Corner:

	def __init__ (
		self,
		recipe_pretty_name,
		clock_speed = None,
		productivity_bonus = None
	):

		self . pretty_name = recipe_pretty_name + ' Corner'

		# From 0.01 to 2.5 or None
		self . clock_speed = clock_speed

		# From 0 to 1 or None
		self . productivity_bonus = productivity_bonus

		if clock_speed is not None:

			self . pretty_name += (
				' Clock '
				+ utils . format_value (clock_speed, 6)
			)

		if productivity_bonus is not None:

			self . pretty_name += (
				' Productivity ' + str (1.0 + self . productivity_bonus)
			)

		name = utils . name (self . pretty_name)

		self . machine_count_variable = lp . Variable (name + '_machine_count')

	def machine_count (self):

		return self . machine_count_variable

	def __speed_multiplier (self):

		if self . clock_speed is not None:

			return self . clock_speed

		else:

			return 1.0

	def input_magnitude (self):

		return self . machine_count_variable * self . __speed_multiplier ()

	def __productivity_multiplier (self):

		if self . productivity_bonus is not None:

			return 1.0 + self . productivity_bonus

		else:

			return 1.0

	def output_magnitude (self):

		return (
			self . machine_count_variable
			* self . __speed_multiplier ()
			* self . __productivity_multiplier ()
		)

	def __power_multiplier (self, machine):

		if self . clock_speed is not None:

			overclock_power_multiplier = (
				self . clock_speed ** machine . overclock_exponent
			)

		else:

			overclock_power_multiplier = 1.0

		if self . productivity_bonus is not None:

			productivity_power_multiplier = (
				self . __productivity_multiplier () ** 2
			)

		else:

			productivity_power_multiplier = 1.0

		return overclock_power_multiplier * productivity_power_multiplier

	def power_magnitude (self, machine):

		return (
			self . machine_count_variable
			* self . __power_multiplier (machine)
		)

	def add_constraints (self, constraints):

		constraints . append (self . machine_count_variable >= 0)

	def interpret_model (self, model, machine):

		machine_count = model [self . machine_count_variable]

		return InterpretedCorner (
			machine_count,
			self . __speed_multiplier (),
			self . __productivity_multiplier (),
			self . __power_multiplier (machine)
		)

class InterpretedCorner:

	def __init__ (
		self,
		machine_count,
		speed_multiplier,
		productivity_multiplier,
		power_multiplier
	):

		self . machine_count = machine_count
		self . speed_multiplier = speed_multiplier
		self . productivity_multiplier = productivity_multiplier
		self . power_multiplier = power_multiplier

	def input_magnitude (self):

		return self . machine_count * self . speed_multiplier

	def output_magnitude (self):

		return (
			self . machine_count
			* self . speed_multiplier
			* self . productivity_multiplier
		)

	def power_magnitude (self):

		return self . machine_count * self . power_multiplier
