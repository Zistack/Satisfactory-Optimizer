class SetPowerConsumption:

	def __init__ (self, power_consumption):

		self . power_consumption = power_consumption

	def add_constraint (self, solver, problem):

		solver . add (
			problem . total_power_consumption_variable
				== self . power_consumption
		)

class BoundPowerConsumption:

	def __init__ (self, power_consumption):

		self . power_consumption = power_consumption

	def add_constraint (self, solver, problem):

		solver . add (
			problem . total_power_consumption_variable
				<= self . power_consumption
		)

def get_power_consumption_goal (problem_data):

	if 'set_power_consumption' in problem_data:

		return SetPowerConsumption (
			RealVal (problem_data ['set_power_consumption'])
		)

	if 'bound_power_consumption' in problem_data:

		return BoundPowerConsumption (
			RealVal (problem_data ['bound_power_consumption'])
		)

	return None
