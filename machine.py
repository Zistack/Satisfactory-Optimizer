import commentjson

import linprog as lp

import utils

class Machine:

	def __init__ (
		self,
		pretty_name,
		overclock_exponent,
		somersloop_slots,
		required_somersloops
	):

		self . pretty_name = pretty_name

		self . overclock_exponent = overclock_exponent
		self . somersloop_slots = somersloop_slots
		self . required_somersloops = required_somersloops

	def supports_overclocking (self):

		return self . overclock_exponent is not None

	def supports_productivity (self):

		return self . somersloop_slots is not None

	def requires_somersloops (self):

		return self . required_somersloops is not None

	def add_constraints (self, constraints, using_recipes):

		pass

	def total_count (self, using_recipes):

		return sum (
			recipe . machine_count () for recipe in using_recipes
		)

	def interpret (self, model, precision, interpreted_using_recipes):

		total_count = self . total_count (interpreted_using_recipes)

		if total_count == 0:

			return None

		return utils . format_value (total_count, precision)

def load_machine (pretty_name, machine_data):

	if 'overclock_exponent' in machine_data:

		overclock_exponent = utils . real (machine_data ['overclock_exponent'])

	else:

		overclock_exponent = None

	if 'somersloop_slots' in machine_data:

		somersloop_slots = utils . real (machine_data ['somersloop_slots'])

	else:

		somersloop_slots = None

	if 'required_somersloops' in machine_data:

		required_somersloops = utils . real (
			machine_data ['required_somersloops']
		)

	else:

		required_somersloops = None

	return Machine (
		pretty_name,
		overclock_exponent,
		somersloop_slots,
		required_somersloops
	)

def load_machines (machines_file_name):

	with open (machines_file_name, 'r') as machines_file:

		machines_data = commentjson . load (machines_file)

	machines = dict ()

	for machine_pretty_name, machine_data in machines_data . items ():

		machines [machine_pretty_name] = load_machine (
			machine_pretty_name,
			machine_data
		)

	return machines

def get_machine (machine_name, machines):

	if machine_name not in machines:

		raise ValueError (
			'\'' + machine_name + '\' does not name a valid machine'
		)

	return machines [machine_name]
