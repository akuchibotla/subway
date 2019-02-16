from __future__ import division
import re
import sys
import itertools
import multiprocessing

error_exprs = []

# function used to evaluate string expressions
def evaluate(expr):
	try:
		if eval(expr) == 10:
			print expr
	except ZeroDivisionError:
		error_exprs.append((expr, 'zero division error'))
	except OverflowError:
		error_exprs.append((expr, 'overflow error'))
	except ValueError:
		error_exprs.append((expr, 'mathematical violation'))

def main():
	# tolerance for long computations (usually exponents)
	TIMEOUT = 3 # seconds

	# in order to use, run it from bash as python subway.py [number]
	if len(sys.argv) < 2:
		print 'must supply argument, please call from command line as such:\n\n' + ' ' * 4 + 'python subway.py 1234\n\n'
		quit()

	number_str = sys.argv[1]
	operands = ['+', '-', '/', '*', '**']

	# adds another operand with a closing paranthesis preceeding it and an openening paranthesis proceeding it
	# the entire function will be wrapped parantheses (to guarantee closure)
	# and this provides an easy way to allow for all parantheses combinations within it
	#
	# ex: ')+('
	# ex: ')**('
	operands_with_parentheses = []
	for operand in operands:
		operands_with_parentheses.append(')' + operand + '(')

	# provides all combinations of operands for how many avaialble separators there are between the numbers
	# the return value will be a dictionary with int keys and iterable values
	# these iterable values will indicate all the possible combinations of operands for key number of available separators
	#
	# ex: 5 _ 2 _ 1 _ 0
	# in this case, we'd use the key 3, result = { 1:[...], 2:[...], 3:[('+', '+', '+'), ('+, '+', '-'), ...] }
	#
	# ex: 52 _ 1 _ 0
	# in this case, we'd use the key 2, result = { 1:[...], 2:[('+', '+'), ('+', '-'), ('-', '**'), ...], 3: [...]}
	possible_operand_combinations_by_length = {}
	for i in range(len(number_str)):
		possible_operand_combinations_by_length[i] = list(itertools.product(operands + operands_with_parentheses, repeat=i))

	possible_digit_combinations_by_length = {}
	separators = range(len(number_str) - 1)

	# separates the number string in all possible ways based on how many separations are being allowed
	#
	# ex: {0: [[1234]], 1: [[1, 234], [12, 34], [123, 4]], 2: [1,2,34], ...], ...}
	for available_separations in range(0, len(separators) + 1):
	    for separation_position in itertools.combinations(separators, available_separations):
			num_str = number_str[0]
			for i in range(len(number_str) - 1):
				if i in separation_position:
					num_str += ','
				num_str += number_str[i + 1]

			if available_separations in possible_digit_combinations_by_length:
				possible_digit_combinations_by_length[available_separations].append(num_str.split(','))
			else:
				possible_digit_combinations_by_length[available_separations] = [num_str.split(',')]

	# kicks off the evaluation process by constructing the expr string
	for i in range(len(number_str)):
		for possible_digit_combination in possible_digit_combinations_by_length[i]:
			for possible_operand_combination in possible_operand_combinations_by_length[i]:
				# wraps expression in paranthesis
				expr = '(' + str(possible_digit_combination[0])
				for j in range(i):
					expr += possible_operand_combination[j]
					expr += possible_digit_combination[j + 1]
				expr += ')'

				# this regex matches on expressions containing no parentheses inside it other
				# than the encapsulating ones
				# if this matches, then the encapsulating parentheses are no longer needed
				# if this doesn't match, then the encapsulating parentheses are needed
				wrapping_necessary = len(list(re.finditer(r'^\([^()]+\)$', expr))) == 0

				# this matches if it can find a number wrapped in parentheses without an operand inside it
				wrapped_numbers = list(re.finditer(r'\(\d+\)', expr))

				# if there are as many matches as there are numbers being considered, all of the parentheses
				# are unnecessary and should therefore not be evaluated
				#
				# ex: (23)+(45) matches because of (23) and (45)
				# there are two numbers being considered: 23 and 34
				# therefore the parantheses are unnecessary
				redundant_expression = len(wrapped_numbers) == len(possible_digit_combination)

				# this is a special case, like (0010), which is a valid solution
				if not wrapping_necessary and redundant_expression:
					pass
				else:
					if not wrapping_necessary:
						expr = expr[1:-1]

					if redundant_expression:
						continue

				# if there are any numbers (not expressions) that are wrapped in parentheses
				# remove the surrounding parentheses from them
				subtract = 0
				for parentheses in wrapped_numbers:
					expr = expr[:parentheses.start() - subtract] + expr[parentheses.start() - subtract + 1:]
					subtract += 1
					expr = expr[:parentheses.end() - 1 - subtract] + expr[parentheses.end() - subtract:]
					subtract += 1

				# this is how timeout functionality is attained
				process = multiprocessing.Process(target=evaluate, args=(expr,))
				process.start()
				process.join(TIMEOUT)

				if process.is_alive():
					error_exprs.append((expr, 'timeout'))
					process.terminate()
					process.join()

	# prints out all un-evaluated expressions
	for error_expr in error_exprs:
		print error_expr[0], 'could not be computed because of a', error_expr[1]

if __name__ == '__main__':
	main()
