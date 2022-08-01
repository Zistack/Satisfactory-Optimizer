def name (pretty_name):

	return (
		'' . join (c if c . isalnum () else '_' for c in pretty_name) . lower ()
	)
