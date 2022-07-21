import argparse

parser = argparse . ArgumentParser (
	description = 'A Satisfactory planner/optimizer based on Z3'
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
	default = 2,
	help = 'Specifies the number of digits to display after the decimal point '
		+ 'when reporting fractional results (default: 2).  Set to a negative '
		+ 'number to display fractional values as exact fractions.'
)

parser . add_argument (
	'problem_file_name',
	default = None,
	help = 'The location of the file containing the problem description '
		+ '(default: standard input).'
)

def parse_args ():

	return parser . parse_args ()
