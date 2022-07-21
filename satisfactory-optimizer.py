#!/bin/python

import json
import sys

from z3 import *

import utils

from options import parse_args

from item import load_items
from machine import load_machines
from recipe import load_recipes
from problem import load_problem
from solve import solve

def main ():

	options = parse_args ()

	items = load_items (options . items_file_name)
	machines = load_machines (options . machines_file_name)
	recipes, groups = load_recipes (
		options . recipes_file_name,
		items,
		machines
	)

	if options . problem_file_name != None:

		problem = load_problem (
			options . problem_file_name,
			items,
			recipes,
			groups
		)

	else:

		problem = read_problem (sys . stdin, items, recipes, groups)

	if options . precision >= 0:

		set_option (rational_to_decimal = True)
		set_option (precision = options . precision)

	results = solve (problem, items, machines, recipes)

	if results == None:

		print ("No solution found", file = sys . stderr)

	else:

		print (json . dumps (results, indent = 4))

main ()
