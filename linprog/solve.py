import itertools
import sys

import numpy as np
import scipy as sp

from linprog . inequality import Inequality
from linprog . equality import Equality
from linprog . expression import Variable, Sum

def encode_inequality_bound (inequality, variable_ids, bounds):

	variable, coefficient = tuple (inequality . terms . items ()) [0]

	value = inequality . constant / coefficient

	idx = variable_ids [variable]

	l, u = bounds [idx]

	if coefficient < 0:

		if l > value:

			return False

		bounds [idx] = (value, u)

	if coefficient > 0:

		if u < value:

			return False

		bounds [idx] = (l, value)

	return True

def encode_equality_bound (equality, variable_ids, bounds):

	variable, coefficient = tuple (equality . terms . items ()) [0]

	value = equality . constant / coefficient

	idx = variable_ids [variable]

	l, u = bounds [idx]

	if l > value or u < value:

		return False

	bounds [idx] = (value, value)

	return True

def encode_linear_constraint (
	constraint,
	variable_ids,
	A,
	b
):

	(num_constraints, num_variables) = A . shape

	A . resize ((num_constraints + 1, num_variables))
	b . resize ((num_constraints + 1,), refcheck = False)

	constraint_idx = num_constraints

	for variable, coefficient in constraint . terms . items ():

		variable_idx = variable_ids [variable]

		A [constraint_idx, variable_idx] = coefficient

	b [constraint_idx] = constraint . constant

def encode_objective (objective, variable_ids):

	if type (objective) == Variable:

		c = np . zeros ((len (variable_ids),))
		c [variable_ids [objective]] = 1

		return c

	if type (objective) == Sum:

		c = np . zeros ((len (variable_ids),))

		for variable, coefficient in objective . terms . items ():

			c [variable_ids [variable]] = coefficient

		return c

	raise TypeError (
		'\'' + str (type (objective)) + '\' is not a valid objective type'
	)

def pin_objective (objective, objective_value, variable_ids, A, b, bounds):

	if type (objective) == Variable:

		encode_equality_bound (objective == objective_value, variable_ids, bounds)

	if type (objective) == Sum:

		if len (objective . terms) == 1:

			encode_equality_bound (objective == objective_value, variable_ids, bounds)

		else:

			encode_linear_constraint (objective == objective_value, variable_ids, A, b)

def add_variables (expression, variable_ids):

	for variable in expression . variables ():

		if variable not in variable_ids:

			variable_ids [variable] = len (variable_ids)

def solve (constraints, objectives):

	variable_ids = dict ()

	unary_ub_constraints = list ()
	linear_ub_constraints = list ()

	unary_eq_constraints = list ()
	linear_eq_constraints = list ()

	for constraint in constraints:

		if type (constraint) == bool:

			if not constraint:

				return None

			else:

				continue

		add_variables (constraint, variable_ids)

		if type (constraint) == Inequality:

			if len (constraint . terms) == 1:

				unary_ub_constraints . append (constraint)

			else:

				linear_ub_constraints . append (constraint)

			continue

		if type (constraint) == Equality:

			if len (constraint . terms) == 1:

				unary_eq_constraints . append (constraint)

			else:

				linear_eq_constraints . append (constraint)

			continue

		raise TypeError (
			'\''
			+ str (type (constraint))
			+ '\' is not a valid type of constraint'
		)

	bounds = np . full ((len (variable_ids), 2), (- np . inf, np . inf))

	A_ub = sp . sparse . dok_array (
		(0, len (variable_ids))
	)
	b_ub = np . ndarray ((0,))

	A_eq = sp . sparse . dok_array (
		(0, len (variable_ids))
	)
	b_eq = np . ndarray ((0,))

	integrality = np . zeros ((len (variable_ids),), dtype=np.uint8)

	for (variable, index) in variable_ids . items ():

		if variable . integrality is not None:

			integrality [index] = variable . integrality

	for inequality in unary_ub_constraints:

		if not encode_inequality_bound (inequality, variable_ids, bounds):

			return None

	for equality in unary_eq_constraints:

		if not encode_equality_bound (equality, variable_ids, bounds):

			return None

	for inequality in linear_ub_constraints:

		encode_linear_constraint (inequality, variable_ids, A_ub, b_ub)

	for equality in linear_eq_constraints:

		encode_linear_constraint (equality, variable_ids, A_eq, b_eq)

	for objective in objectives:

		c = encode_objective (objective, variable_ids)

		result = sp . optimize . linprog (c, A_ub, b_ub, A_eq, b_eq, bounds,
			integrality=integrality)

		if not result . success:

			print ("Optimization Failed:", result . message, file = sys . stderr)

			return None

		objective_value = result . fun

		pin_objective (
			objective,
			objective_value,
			variable_ids,
			A_eq,
			b_eq,
			bounds
		)

	return dict (
		(variable, result . x [idx])
		for variable, idx in variable_ids . items ()
	)
