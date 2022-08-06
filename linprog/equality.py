class Equality:

	def __init__ (self, terms, constant):

		self . terms = terms
		self . constant = constant

	def __str__ (self):

		sum_terms = [
			str (coefficient) + ' * ' + str (variable)
			for variable, coefficient in self . terms . items ()
		]

		return ' + ' . join (sum_terms) + ' == ' + str (self . constant)

	def variables (self):

		return self . terms . keys ()
