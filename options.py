import argparse

parser = argparse . ArgumentParser (
	description = 'A Satisfactory planner/optimizer based on scipy.linprog.optimize'
)

parser . add_argument (
	'--node-types-file',
	dest = 'node_types_file_name',
	default = 'node_types.json',
	help = 'The location of the file containing node type data (default: '
		+ 'node_types.json).'
)

parser . add_argument (
	'--well-types-file',
	dest = 'well_types_file_name',
	default = 'well_types.json',
	help = 'The location of the file containing well type data (default: '
		+ 'well_types.json).'
)

parser . add_argument (
	'--items-file',
	dest = 'items_file_name',
	default = 'items.json',
	help = 'The location of the file containing item data (default: '
		+ 'items.json).'
)

parser . add_argument (
	'--machines-file',
	dest = 'machines_file_name',
	default = 'machines.json',
	help = 'The location of the file containing machine data (default: '
		+ 'machines.json).'
)

parser . add_argument (
	'--recipes-file',
	dest = 'recipes_file_name',
	default = 'recipes.json',
	help = 'The location of the file containing recipe data (default: '
		+ 'recipes.json).'
)

parser . add_argument (
	'--precision',
	type = int,
	default = 3,
	help = 'Specifies the number of digits to display after the decimal point '
		+ 'when reporting fractional results (default: 3).'
)

parser . add_argument (
	'problem_file_name',
	help = 'The location of the file containing the problem description.'
)

def parse_args ():

	return parser . parse_args ()
