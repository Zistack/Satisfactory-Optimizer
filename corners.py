import itertools

from corner import Corner

class Corners:

	def __init__ (
		self,
		recipe_pretty_name,
		overclock_limits,
		model_productivity
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

		if model_productivity:

			productivity_points = [0.0, 1.0]

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

	def interpret_model (self, model, machine):

		machine_count = 0
		input_magnitude = 0
		output_magnitude = 0
		power_magnitude = 0
		total_clock_speed = 0
		somersloops_slotted = 0

		for corner in self . corners:

			interpreted_corner = corner . interpret_model (model, machine)

			machine_count += interpreted_corner . machine_count
			input_magnitude += interpreted_corner . input_magnitude
			output_magnitude += interpreted_corner . output_magnitude
			power_magnitude += interpreted_corner . power_magnitude
			total_clock_speed += (
				interpreted_corner . machine_count
				* interpreted_corner . overclock_setting
			)
			somersloops_slotted += interpreted_corner . somersloops_slotted

		if machine_count != 0:

			overclock_setting = total_clock_speed / machine_count

		else:

			overclock_setting = 1.0

		return InterpretedCorners (
			machine_count,
			input_magnitude,
			output_magnitude,
			power_magnitude,
			overclock_setting,
			somersloops_slotted
		)

class InterpretedCorners:

	def __init__ (
		self,
		machine_count,
		input_magnitude,
		output_magnitude,
		power_magnitude,
		overclock_setting,
		somersloops_slotted
	):

		self . machine_count = machine_count
		self . input_magnitude = input_magnitude
		self . output_magnitude = output_magnitude
		self . power_magnitude = power_magnitude
		self . overclock_setting = overclock_setting
		self . somersloops_slotted = somersloops_slotted
