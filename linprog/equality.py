class Equality:

	def __init__ (self, terms, constant):

		self . terms = terms
		self . constant = constant

	def __str__ (self):

		sum_terms = [
			str (coefficient) + ' * ' + str (var_key)
			for var_key, coefficient in self . terms . items ()
		]

		return ' + ' . join (sum_terms) + ' == ' + str (self . constant)

	def var_keys (self):

		return self . terms . keys ()
