from linprog . utils import convert_constant

from linprog . inequality import Inequality
from linprog . equality import Equality

class Variable:

	def __init__ (self, name):

		self . name = name

	def __str__ (self):

		return self . name

	def __hash__ (self):

		return self . name . __hash__ ()

	def __cmp__ (self, other):

		return self . name . __cmp__ (other . name)

	def __neg__ (self):

		return Sum ({self: -1}, 0)

	def __add__ (self, other):

		other = convert_constant (other)

		if type (other) == float:

			if other == 0:

				return self

			else:

				return Sum ({self: 1}, other)

		if type (other) == Variable:

			return Sum ({self: 1, other: 1}, 0)

		if type (other) == Sum:

			if self in other . terms:

				new_terms = dict (other . terms . items ())

				new_terms [self] += 1

				if new_terms [self] == 0:

					del new_terms [self]

					if len (new_terms) == 0:

						return other . constnat

				return Sum (new_terms, other . constant)

			else:

				new_terms = dict ()

				new_terms [self] = 1

				new_terms . update (other . terms . items ())

				return Sum (new_terms, other . constant)

		raise TypeError (
			'Addition with variable not supported for \''
			+ str (type (other))
			+ '\''
		)

	def __radd__ (self, other):

		return self + other

	def __sub__ (self, other):

		return self + (- other)

	def __rsub__ (self, other):

		return (- self) + other

	def __mul__ (self, other):

		# We only support multiplication with constants

		other = convert_constant (other)

		if type (other) == float:

			if other == 0:

				return 0

			else:

				return Sum ({self: other}, 0)

		raise TypeError (
			'Multiplication with variable not supported for \''
			+ str (type (other))
			+ '\''
		)

	def __rmul__ (self, other):

		return self * other

	def __truediv__ (self, other):

		if type (other) == float:

			return Sum ({self: 1 / other}, 0)

	def __le__ (self, other):

		other = convert_constant (other)

		if type (other) == float:

			return Inequality ({self: 1}, other)

		if type (other) == Variable:

			return Inequality ({self: 1, other: -1}, 0)

		if type (other) == Sum:

			return self - other <= 0

		raise TypeError (
			'Comparison with variable not supported for \''
			+ str (type (other))
			+ '\''
		)

	def __ge__ (self, other):

		return (- self) <= (- other)

	def __eq__ (self, other):

		other = convert_constant (other)

		if type (other) == float:

			return Equality ({self: 1}, other)

		if type (other) == Variable:

			return Equality ({self: 1, other: -1}, 0)

		if type (other) == Sum:

			return self - other == 0

		raise TypeError (
			'Comparison with variable not supported for \''
			+ str (type (other))
			+ '\''
		)

	def variables (self):

		return [self]

class Sum:

	def __init__ (self, terms, constant):

		self . terms = terms
		self . constant = constant

	def __str__ (self):

		sum_terms = [
			str (coefficient) + ' * ' + str (variable)
			for variable, coefficient in self . terms . items ()
		]

		if self . constant != 0:

			sum_terms . append (str (self . constant))

		return ' + ' . join (sum_terms)

	def __neg__ (self):

		return Sum (
			{
				variable: - coefficient
				for variable, coefficient in self . terms . items ()
			},
			- self . constant
		)

	def __add__ (self, other):

		other = convert_constant (other)

		if type (other) == float:

			if other == 0:

				return self

			return Sum (self . terms, self . constant + other)

		if type (other) == Variable:

			new_terms = dict (self . terms . items ())

			if other in new_terms:

				new_terms [other] += 1

				if new_terms [other] == 0:

					del new_terms [other]

					if len (new_terms) == 0:

						return self . constant

			else:

				new_terms [other] = 1

			return Sum (new_terms, self . constant)

		if type (other) == Sum:

			new_terms = dict (self . terms . items ())

			for variable, coefficient in other . terms . items ():

				if variable in new_terms:

					new_terms [variable] += coefficient

					if new_terms [variable] == 0:

						del new_terms [variable]

				else:

					new_terms [variable] = coefficient

			if len (new_terms) == 0:

				return other . constant

			return Sum (new_terms, other . constant)

		raise TypeError (
			'Addition with sum not supported for \''
			+ str (type (other))
			+ '\''
		)

	def __radd__ (self, other):

		return self + other

	def __sub__ (self, other):

		return self + (- other)

	def __rsub__ (self, other):

		return (- self) + other

	def __mul__ (self, other):

		other = convert_constant (other)

		if type (other) == float:

			if other == 0:

				return 0

			new_terms = dict (
				(variable, coefficient * other)
				for variable, coefficient in self . terms . items ()
			)

			new_constant = self . constant * other

			return Sum (new_terms, new_constant)

		raise TypeError (
			'Multiplication with sum not supported for \''
			+ str (type (other))
			+ '\''
		)

	def __rmul__ (self, other):

		return self * other

	def __truediv__ (self, other):

		other = convert_constant (other)

		if type (other) == float:

			new_terms = dict (
				(variable, coefficient / other)
				for variable, coefficient in self . terms . items ()
			)

			new_constant = self . constant / other

			return Sum (new_terms, new_constant)

	def __le__ (self, other):

		other = convert_constant (other)

		if type (other) == float:

			return Inequality (self . terms, other - self . constant)

		if type (other) == Variable:

			return self - other <= 0

		if type (other) == Sum:

			return self - other <= 0

		raise TypeError (
			'Comparison with sum not supported for \''
			+ str (type (other))
			+ '\''
		)

	def __ge__ (self, other):

		return (- self) <= (- other)

	def __eq__ (self, other):

		other = convert_constant (other)

		if type (other) == float:

			return Equality (self . terms, other - self . constant)

		if type (other) == Variable:

			return self - other == 0

		if type (other) == Sum:

			return self - other == 0

		raise TypeError (
			'Comparison with sum not supported for \''
			+ str (type (other))
			+ '\''
		)

	def variables (self):

		return self . terms . keys ()
