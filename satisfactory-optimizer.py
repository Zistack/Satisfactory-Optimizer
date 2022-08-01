#!/bin/python

import json
import sys

from z3 import *

from options import parse_args

from node_type import load_node_types
from well_type import load_well_types
from item import load_items
from machine import load_machines
from recipe_utils import load_recipes
from problem import load_problem

def main ():

	options = parse_args ()

	print ('Loading data', file = sys . stderr)

	node_types = load_node_types (options . node_types_file_name)
	well_types = load_well_types (options . well_types_file_name)
	items = load_items (options . items_file_name)
	machines = load_machines (options . machines_file_name)
	(
		all_recipes,
		node_recipes,
		well_recipes,
		processing_recipes,
		groups
	) = load_recipes (
		options . recipes_file_name,
		node_types,
		well_types,
		items,
		machines
	)

	print ('Loading problem', file = sys . stderr)

	problem = load_problem (
		options . problem_file_name,
		node_types,
		well_types,
		items,
		all_recipes,
		node_recipes,
		well_recipes,
		processing_recipes,
		groups
	)

	if options . precision >= 0:

		set_option (rational_to_decimal = True)
		set_option (precision = options . precision)

	results = problem . solve ()

	if results == None:

		print ("No solution found", file = sys . stderr)

	else:

		print (json . dumps (results, indent = 4))

main ()
