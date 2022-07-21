import utils

class MaximizeItemProduction:

	def __init__ (self, item):

		self . item = item

	def add_objective_function (self, solver):

		solver . maximize (self . item . output_variable)

class MinimizeItemProduction:

	def __init__ (self, item):

		self . item = item

	def add_objective_function (self, solver):

		solver . minimize (self . item . output_variable)

class MaximizeItemConsumption:

	def __init__ (self, item):

		self . item = item

	def add_objective_function (self, solver):

		solver . maximize (self . item . input_variable)

class MinimizeItemConsumption:

	def __init__ (self, item):

		self . item = item

	def add_objective_function (self, solver):

		solver . minimize (self . item . input_variable)

class MaximizeItemsProduction:

	def __init__ (self, items):

		self . items = items

	def add_objective_function (self, solver):

		solver . maximize (
			sum (item . output_variable * quantity for item, quantity in items)
		)

class MaximizeItemFlow:

	def __init__ (self, item):

		self . item = item

	def add_objective_function (self, solver):

		solver . maximize (self . item . flow_variable)

class MinimizeItemFlow:

	def __init__ (self, item):

		self . item = item

	def add_objective_function (self, solver):

		solver . minimize (self . item . flow_variable)

class MaximizeItemsFlow:

	def __init__ (self, items):

		self . items = items

	def add_objective_function (self, solver):

		solver . maximize (
			sum (item . flow_variable * quantity for item, quantity in items)
		)

class MaximizeRecipe:

	def __init__ (self, recipe):

		self . recipe = recipe

	def add_objective_function (self, solver):

		solver . maximize (self . recipe . machine_count_variable)

class MinimizeRecipe:

	def __init__ (self, recipe):

		self . recipe = recipe

	def add_objective_function (self, solver):

		solver . minimize (self . recipe . machine_count_variable)

def get_optimization_goal (goal_type, goal_data, items, recipes):

	if goal_type == 'maximize_item_production':

		return MaximizeItemProduction (
			utils . get_item (goal_data, items)
		)

	if goal_type == 'minimize_item_production':

		return MinimizeItemProduction (
			utils . get_item (goal_data, items)
		)

	if goal_type == 'maximize_item_consumption':

		return MaximizeItemProduction (
			utils . get_item (goal_data, items)
		)

	if goal_type == 'minimize_item_consumption':

		return MinimizeItemConsumption (
			utils . get_item (goal_data, items)
		)

	if goal_type == 'maximize_items_production':

		return MaximizeItemsConsumption (
			utils . get_finite_item_quantities (goal_data, items)
		)

	if goal_type == 'maximize_item_flow':

		return MaximizeItemFlow (utils . get_item (goal_data, items))

	if goal_type == 'minimize_item_flow':

		return MinimizeItemFlow (utils . get_item (goal_data, items))

	if goal_type == 'maximize_items_flow':

		return MaximizeItemsFlow (
			utils . get_finite_item_quantities (goal_data, items)
		)

	if goal_type == 'maximize_recipe':

		return MaximizeRecipe (utils . get_recipe (goal_data, recipes))

	if goal_type == 'minimize_recipe':

		return MinimizeRecipe (utils . get_recipe (goal_data, recipes))

	raise ValueError (
		'\'' + goal_type + '\' does not name a valid production goal'
	)
