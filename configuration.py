import math

from collections import defaultdict

import linprog as lp

import utils

from corner import Corner

class Configuration:

	def __init__ (
		self,
		recipe_pretty_name,
		overclock_limits,
		productivity_bonus
	):

		self . pretty_name = recipe_pretty_name + ' Configuration'

		self . overclock_limits = overclock_limits
		self . productivity_bonus = productivity_bonus

		if overclock_limits is not None:

			overclock_points = list ()

			if (
				overclock_limits . min_clock_speed <= 1.0
				and overclock_limits . max_clock_speed >= 1.0
			):

				overclock_points . append (1.0)

			if overclock_limits . min_clock_speed not in overclock_points:

				overclock_points . append (overclock_limits . min_clock_speed)

			if overclock_limits . max_clock_speed not in overclock_points:

				overclock_points . append (overclock_limits . max_clock_speed)

		else:

			overclock_points = [None]

		if productivity_bonus is not None:

			self . pretty_name += (
				' Productivity ' + str (1.0 + productivity_bonus)
			)

		self . corners = list (
			Corner (recipe_pretty_name, clock_speed, productivity_bonus)
			for clock_speed in overclock_points
		)

		if (
			self . productivity_bonus is not None
			and self . productivity_bonus != 0.0
		):

			name = utils . name (self . pretty_name)

			self . machine_count_variable = lp . Variable (
				name + '_machine_count',
				1
			)

		else:

			self . machine_count_variable = None

	def machine_count (self):

		return sum (corner . machine_count () for corner in self . corners)

	def input_magnitude (self):

		return sum (corner . input_magnitude () for corner in self . corners)

	def output_magnitude (self):

		return sum (corner . output_magnitude () for corner in self . corners)

	def power_magnitude (self, machine):

		return sum (
			corner . power_magnitude (machine)
			for corner in self . corners
		)

	def somersloops_slotted (self, somersloops_slotted_per_machine):

		if self . machine_count_variable is not None:

			return (
				self . machine_count_variable * somersloops_slotted_per_machine
			)

		else:

			return 0

	def add_constraints (self, constraints):

		for corner in self . corners:

			corner . add_constraints (constraints)

		if self . machine_count_variable is not None:

			constraints . append (
				self . machine_count_variable >= sum (
					corner . machine_count () for corner in self . corners
				)
			)

	def interpret_model (self, model, machine, precision):

		interpreted_corners = list (
			corner . interpret_model (model, machine)
			for corner in self . corners
		)

		if self . machine_count_variable is not None:

			integer_machine_count = model [self . machine_count_variable]

		else:

			integer_machine_count = math . ceil (
				utils . interpret_approximate (
					sum (
						corner . machine_count
						for corner in interpreted_corners
					),
					precision
				)
			)

		return InterpretedConfiguration (
			integer_machine_count,
			interpreted_corners
		)

class InterpretedConfiguration:

	def __init__ (self, integer_machine_count, interpreted_corners):

		self . integer_machine_count = integer_machine_count
		self . interpreted_corners = interpreted_corners

	def machine_count (self):

		return sum (
			corner . machine_count
			for corner in self . interpreted_corners
		)

	def input_magnitude (self):

		return sum (
			corner . input_magnitude ()
			for corner in self . interpreted_corners
		)

	def output_magnitude (self):

		return sum (
			corner . output_magnitude ()
			for corner in self . interpreted_corners
		)

	def power_magnitude (self):

		return sum (
			corner . power_magnitude ()
			for corner in self . interpreted_corners
		)

	def get_report (self, machine, precision):

		report = dict ()

		if machine . supports_overclocking ():

			report ['machine_count'] = utils . format_value (
				self . integer_machine_count,
				0
			)

			clock_speed_setting = utils . interpret_approximate (
				self . input_magnitude () / self . integer_machine_count,
				6
			)

			if clock_speed_setting != 1.0:

				report ['clock_speed_setting'] = utils . format_value (
					clock_speed_setting,
					6
				)

		else:

			report ['machine_count'] = utils . format_value (
				self . machine_count (),
				precision
			)

		return report
