import math

from z3 import *

CLOCK_SPEED_DENOMINATOR = 400
MIN_CLOCK_SPEED = 4
MAX_CLOCK_SPEED = 1000

class OverclockLimits:

	def __init__ (self, scaled_min_clock_speed, scaled_max_clock_speed):

		self . scaled_min_clock_speed = scaled_min_clock_speed
		self . scaled_max_clock_speed = scaled_max_clock_speed

	def scaled_clock_speeds (self):

		return range (
			self . scaled_min_clock_speed,
			self . scaled_max_clock_speed + 1
		)

	def indices (self):

		return range (
			0,
			self . scaled_max_clock_speed - self . scaled_min_clock_speed + 1
		)

	def clock_speeds (self):

		return (
			Q (scaled_clock_speed, CLOCK_SPEED_DENOMINATOR)
			for scaled_clock_speed in self . scaled_clock_speeds ()
		)

	def power_factors (self, exponent):

		# Z3 can't _actually_ handle exact exponentiation, so we have to do all
		# of this as float math before Z3 gets to touch it.
		return (
			(scaled_clock_speed / CLOCK_SPEED_DENOMINATOR) ** exponent
			for scaled_clock_speed in self . scaled_clock_speeds ()
		)

def get_overclock_limits (overclock_limits_data):

	if 'min_clock_speed' in overclock_limits_data:

		float_min_clock_speed = (
			float (overclock_limits_data ['min_clock_speed'])
			* CLOCK_SPEED_DENOMINATOR
		)

		scaled_min_clock_speed = max (
			MIN_CLOCK_SPEED,
			math . ceil (float_min_clock_speed)
		)

	else:

		scaled_min_clock_speed = CLOCK_SPEED_DENOMINATOR

	if 'max_clock_speed' in overclock_limits_data:

		float_max_clock_speed = (
			float (overclock_limits_data ['max_clock_speed'])
			* CLOCK_SPEED_DENOMINATOR
		)

		scaled_max_clock_speed = min (
			MAX_CLOCK_SPEED,
			math . floor (float_max_clock_speed)
		)

	else:

		scaled_max_clock_speed = CLOCK_SPEED_DENOMINATOR

	return OverclockLimits (scaled_min_clock_speed, scaled_max_clock_speed)
