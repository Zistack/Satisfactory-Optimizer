import math

import utils

class Configuration:

	def __init__ (self):

		self . machine_count = 0
		self . input_magnitude = 0
		self . output_magnitude = 0
		self . power_magnitude = 0
		self . somersloops_slotted = 0

	def add_corner_machines (self, interpreted_corner):

		self . machine_count += interpreted_corner . machine_count
		self . input_magnitude += interpreted_corner . input_magnitude ()
		self . output_magnitude += interpreted_corner . output_magnitude ()
		self . power_magnitude += interpreted_corner . power_magnitude ()

	def get_report (
		self,
		somersloop_factor,
		machine_supports_overclocking,
		precision
	):

		report = dict ()

		if machine_supports_overclocking:

			integer_machine_count = math . ceil (
				utils . interpret_approximate (
					self . machine_count,
					precision
				)
			)

			report ['machine_count'] = utils . format_value (
				integer_machine_count,
				0
			)

			clock_speed_setting = self . input_magnitude / integer_machine_count

			report ['clock_speed_setting'] = utils . format_value (
				clock_speed_setting,
				6
			)

		else:

			report ['machine_count'] = utils . format_value (
				self . machine_count,
				precision
			)

		if utils . interpret_approximate (somersloop_factor, 0) != 0:

			report ['somersloops_slotted_per_machine'] = utils . format_value (
				somersloop_factor,
				0
			)

		return report
