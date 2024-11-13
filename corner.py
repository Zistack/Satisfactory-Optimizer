import linprog as lp

import utils

class Corner:

	def __init__ (
		self,
		recipe_pretty_name,
		clock_speed = None,
		productivity_bonus = None
	):

		self . pretty_name = recipe_pretty_name

		# From 0.01 to 2.5 or None
		self . clock_speed = clock_speed

		# From 0 to 1 or None
		self . productivity_bonus = productivity_bonus

		if clock_speed != None:

			self . pretty_name += (
				' Clock '
				+ utils . format_value (clock_speed, 6)
			)

		if productivity_bonus != None:

			self . pretty_name += (
				' Productivity ' + str (1.0 + self . productivity_bonus)
			)

		name = utils . name (self . pretty_name)

		self . fractional_machine_count_variable = lp . Variable (
			 name + '_machine_count'
		)

		self . integer_machine_count_variable = None

		if productivity_bonus is not None and productivity_bonus > 0.0:

			self . integer_machine_count_variable = lp . Variable (
				name + '_machine_count_integer',
				1 # integer constraint
			)

	def machine_count (self):

		# While the integer_machine_count_variable would probably be more correct here,
		# having too many integer constraints makes the solver take too long to finish.
		# As a compromise for performance, it is only used for somersloops.
		return self . fractional_machine_count_variable

	def __speed_multiplier (self):

		if self . clock_speed != None:

			return self . clock_speed

		else:

			return 1.0

	def input_magnitude (self):

		return self . fractional_machine_count_variable * self . __speed_multiplier ()

	def __productivity_multiplier (self):

		if self . productivity_bonus != None:

			return 1.0 + self . productivity_bonus

		else:

			return 1.0

	def output_magnitude (self):

		return (
			self . fractional_machine_count_variable
			* self . __speed_multiplier ()
			* self . __productivity_multiplier ()
		)

	def __power_multiplier (self, machine):

		if self . clock_speed != None:

			overclock_power_multiplier = (
				self . clock_speed ** machine . overclock_exponent
			)

		else:

			overclock_power_multiplier = 1.0

		if self . productivity_bonus != None:

			productivity_power_multiplier = (
				self . __productivity_multiplier () ** 2
			)

		else:

			productivity_power_multiplier = 1.0

		return overclock_power_multiplier * productivity_power_multiplier

	def power_magnitude (self, machine):

		return (
			self . fractional_machine_count_variable
			* self . __power_multiplier (machine)
		)

	def __somersloop_factor (self, machine):

		if self . productivity_bonus != None:

			return self . productivity_bonus * machine . somersloop_slots

		else:

			return 0.0

	def somersloops_slotted (self, machine):

		if self . integer_machine_count_variable is not None:

			return (
				self . integer_machine_count_variable
				* self . __somersloop_factor (machine)
			)

		else:

			return 0.0

	def add_constraints (self, constraints):

		constraints . append (self . fractional_machine_count_variable >= 0)

		if self . integer_machine_count_variable is not None:

			constraints . append (self . integer_machine_count_variable >= self . fractional_machine_count_variable)

			# We don't need a constraint to keep the integer count close to the fractional count.
			# The optimization process will do this naturally if it matters. The number of machines
			# should be interpreted with ciel(fractional_machine_count_variable), instead of reading
			# integer_machine_count_variable, because if it isn't important for optimization
			# the integer value may be larger than expected.

	def interpret_model (self, model, machine):

		machine_count = model [self . fractional_machine_count_variable]

		return InterpretedCorner (
			machine_count,
			self . __speed_multiplier (),
			self . __productivity_multiplier (),
			self . __power_multiplier (machine),
			self . __somersloop_factor (machine)
		)

class InterpretedCorner:

	def __init__ (
		self,
		machine_count,
		speed_multiplier,
		productivity_multiplier,
		power_multiplier,
		somersloop_factor
	):

		self . machine_count = machine_count
		self . input_magnitude = machine_count * speed_multiplier
		self . output_magnitude = (
			machine_count
			* speed_multiplier
			* productivity_multiplier
		)
		self . power_magnitude = machine_count * power_multiplier
		self . overclock_setting = speed_multiplier
		self . somersloops_slotted = machine_count * somersloop_factor
