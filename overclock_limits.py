import math

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
			scaled_clock_speed / CLOCK_SPEED_DENOMINATOR
			for scaled_clock_speed in self . scaled_clock_speeds ()
		)

	def power_factors (self, exponent):

		return (
			clock_speed ** exponent
			for clock_speed in self . clock_speeds ()
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
