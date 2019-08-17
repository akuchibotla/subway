from subway import solver
import json
import os

for i in xrange(10000):
	num_str = str(i)
	num_str = '0' * (4 - len(num_str)) + num_str
	file_name = 'solutions/' + num_str + '.json'

	if os.path.isfile(file_name):
		print num_str, 'has already been computed, so skipping'
		continue

	solutions = solver(num_str)._getvalue()
	with open(file_name, 'w') as outfile:
		json.dump(solutions, outfile)

	print 'finished with', num_str