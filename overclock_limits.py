import math

import utils

class OverclockLimits:

	def __init__ (self, min_clock_speed, max_clock_speed):

		self . min_clock_speed = min_clock_speed
		self . max_clock_speed = max_clock_speed

def load_overclock_limits (overclock_limits_data):

	if 'min_clock_speed' in overclock_limits_data:

		min_clock_speed = (
			utils . real (overclock_limits_data ['min_clock_speed'])
		)

	else:

		min_clock_speed = 1.0

	if 'max_clock_speed' in overclock_limits_data:

		max_clock_speed = (
			utils . real (overclock_limits_data ['max_clock_speed'])
		)

	else:

		max_clock_speed = 1.0

	return OverclockLimits (min_clock_speed, max_clock_speed)
