import commentjson

def load_well_types (well_types_file_name):

	with open (well_types_file_name, 'r') as well_types_file:

		well_types_data = commentjson . load (well_types_file)

	return set (well_types_data)

def get_well_type (well_type_name, well_types):

	if well_type_name not in well_types:

		raise ValueError (
			'\''
			+ well_type_name
			+ '\' does not name a valid well type.'
		)

	return well_type_name
