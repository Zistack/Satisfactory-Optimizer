import commentjson

class WellType:

	def __init__ (self, pretty_name):

		self . pretty_name = pretty_name

def load_well_types (well_types_file_name):

	with open (well_types_file_name, 'r') as well_types_file:

		well_types_data = commentjson . load (well_types_file)

	well_types = dict ()

	for well_type_pretty_name in well_types_data:

		well_types [well_type_pretty_name] = WellType (well_type_pretty_name)

	return well_types

def get_well_type (well_type_name, well_types):

	if well_type_name not in well_types:

		raise ValueError (
			'\''
			+ well_type_name
			+ '\' does not name a valid well type.'
		)

	return well_types [well_type_name]
