import itertools

from collections import defaultdict

import utils

from configuration import Configuration
from corner import Corner

class Corners:

	def __init__ (
		self,
		recipe_pretty_name,
		overclock_limits,
		somersloop_slots
	):

		if overclock_limits != None:

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

		if somersloop_slots != None:

			productivity_points = [0.0] + [1.0 / i for i in range (somersloop_slots, 1, -1)]

		else:

			productivity_points = [None]

		self . corners = list (
			Corner (recipe_pretty_name, clock_speed, productivity_bonus)
			for clock_speed, productivity_bonus
			in itertools . product (overclock_points, productivity_points)
		)

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

	def somersloops_slotted (self, machine):

		return sum (
			corner . somersloops_slotted (machine) for corner in self . corners
		)

	def add_constraints (self, constraints):

		for corner in self . corners:

			corner . add_constraints (constraints)

	def interpret_model (self, model, machine, precision):

		configurations = defaultdict (Configuration)

		for corner in self . corners:

			interpreted_corner = corner . interpret_model (model, machine)

			if (
				utils . interpret_approximate (
					interpreted_corner . machine_count,
					precision
				) != 0
			):

				configurations [
					interpreted_corner . somersloop_factor
				] . add_corner_machines (interpreted_corner)

		return configurations
