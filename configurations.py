import math

import utils

from configuration import Configuration

class Configurations:

	def __init__ (
		self,
		recipe_pretty_name,
		overclock_limits,
		somersloop_slots,
		recipe_requires_somersloops
	):

		self . configurations = list ()

		if somersloop_slots is not None:

			for somersloop_count in range (0, somersloop_slots + 1):

				productivity_bonus = somersloop_count / somersloop_slots

				configuration = Configuration (
					recipe_pretty_name,
					overclock_limits,
					productivity_bonus
				)

				self . configurations . append (configuration)

		else:

			configuration = Configuration (
				recipe_pretty_name,
				overclock_limits,
				None
			)

			self . configurations . append (configuration)

	def machine_count (self):

		return sum (
			configuration . machine_count ()
			for configuration in self . configurations
		)

	def input_magnitude (self):

		return sum (
			configuration . input_magnitude ()
			for configuration in self . configurations
		)

	def output_magnitude (self):

		return sum (
			configuration . output_magnitude ()
			for configuration in self . configurations
		)

	def power_magnitude (self, machine):

		return sum (
			configuration . power_magnitude (machine)
			for configuration in self . configurations
		)

	def somersloops_slotted (self):

		return sum (
			configuration . somersloops_slotted (somersloops_slotted_per_machine)
			for somersloops_slotted_per_machine, configuration
			in enumerate (self . configurations)
		)

	def add_constraints (self, constraints):

		for configuration in self . configurations:

			configuration . add_constraints (constraints)

	def interpret_model (self, model, machine, precision):

		interpreted_configurations = list (
			configuration . interpret_model (model, machine, precision)
			for configuration in self . configurations
		)

		return InterpretedConfigurations (interpreted_configurations)

class InterpretedConfigurations:

	def __init__ (self, interpreted_configurations):

		self . interpreted_configurations = interpreted_configurations

	def machine_count (self):

		return sum (
			configuration . machine_count ()
			for configuration in self . interpreted_configurations
		)

	def input_magnitude (self):

		return sum (
			configuration . input_magnitude ()
			for configuration in self . interpreted_configurations
		)

	def output_magnitude (self):

		return sum (
			configuration . output_magnitude ()
			for configuration in self . interpreted_configurations
		)

	def power_magnitude (self):

		return sum (
			configuration . power_magnitude ()
			for configuration in self . interpreted_configurations
		)

	def get_report (self, machine, precision):

		config_reports = list ()

		for somersloops_slotted_per_machine, configuration in enumerate (
			self . interpreted_configurations
		):

			if configuration . integer_machine_count != 0:

				config_report = configuration . get_report (machine, precision)

				if somersloops_slotted_per_machine != 0:

					config_report ['somersloops_slotted_per_machine'] = (
						somersloops_slotted_per_machine
					)

				config_reports . append (config_report)

		if len (config_reports) == 1:

			return config_reports [0]

		else:

			return {'configurations': config_reports}
