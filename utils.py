def name (pretty_name):

	return (
		'' . join (c if c . isalnum () else '_' for c in pretty_name) . lower ()
	)

def real (value):

	if type (value) == str:

		if '/' in value:

			numerator, denominator = value . split ('/')

			return float (numerator) / float (denominator)

		else:

			return float (value)

	else:

		return value

def format_value (value, precision):

	return ('{:.' + str (precision) + 'f}') . format (value)

def interpret_approximate (value, precision):

	return float (format_value (value, precision))
