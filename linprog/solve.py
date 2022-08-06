import itertools

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
	constraint_idx,
	constraint,
	variable_ids,
	A,
	b
):

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

		if len (objective . terms) == 1:

			variable, coefficient = tuple (objective . terms . items ()) [0]

			c = np . zeros ((len (variable_ids),))
			c [variable_ids [variable]] = coefficient

			return c

		raise ValueError (
			'Only objective containing a single variable may be encoded'
		)

	raise TypeError (
		'\'' + str (type (objective)) + '\' is not a valid objective type'
	)

def pin_objective (objective, objective_value, variable_ids, bounds):

	if type (objective) == Variable:

		bounds [variable_ids [objective]] = (objective_value, objective_value)

	if type (objective) == Sum:

		variable, coefficient = tuple (objective . terms . items ()) [0]

		variable_value = objective_value / coefficient

		bounds [variable_ids [variable]] = (variable_value, variable_value)

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
		(len (linear_ub_constraints), len (variable_ids))
	)
	b_ub = np . ndarray ((len (linear_ub_constraints),))

	A_eq = sp . sparse . dok_array (
		(len (linear_eq_constraints), len (variable_ids))
	)
	b_eq = np . ndarray ((len (linear_eq_constraints),))

	for inequality in unary_ub_constraints:

		if not encode_inequality_bound (inequality, variable_ids, bounds):

			return None

	for equality in unary_eq_constraints:

		if not encode_equality_bound (equality, variable_ids, bounds):

			return None

	for i, inequality in zip (
		range (0, len (linear_ub_constraints)),
		linear_ub_constraints
	):

		encode_linear_constraint (i, inequality, variable_ids, A_ub, b_ub)

	for i, equality in zip (
		range (0, len (linear_eq_constraints)),
		linear_eq_constraints
	):

		encode_linear_constraint (i, equality, variable_ids, A_eq, b_eq)

	for objective in objectives:

		c = encode_objective (objective, variable_ids)

		result = sp . optimize . linprog (c, A_ub, b_ub, A_eq, b_eq, bounds)

		if not result . success:

			return None

		objective_value = result . fun

		pin_objective (objective, objective_value, variable_ids, bounds)

	return dict (
		(variable, result . x [idx])
		for variable, idx in variable_ids . items ()
	)
