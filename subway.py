from __future__ import division
import re
import sys
import itertools
import multiprocessing

error_exprs = []

# function used to evaluate string expressions
def evaluate(expr, solutions):
	try:
		if eval(expr) == 10:
			solutions.append(expr)
	except ZeroDivisionError:
		error_exprs.append((expr, 'zero division error'))
	except OverflowError:
		error_exprs.append((expr, 'overflow error'))
	except ValueError:
		error_exprs.append((expr, 'mathematical violation'))
	except SyntaxError:
		error_exprs.append((expr, 'syntax error detected'))

def solver(number_str):
	# tolerance for long computations (usually exponents)
	TIMEOUT = 1 # seconds

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

	# the None value is used to join numbers together rather than separate them with an operand
	# operands.append(None)

	# provides all combinations of operands to fill the n-1 slots in a number
	possible_operand_combinations = list(itertools.product(operands + operands_with_parentheses, repeat=len(number_str) - 1))

	manager = multiprocessing.Manager()
	solutions = manager.list()
	# kicks off the evaluation process by constructing the expr string
	for possible_operand_combination in possible_operand_combinations:
		# wraps expression in paranthesis
		expr = '(' + number_str[0]
		for i in range(len(number_str) - 1):
			if possible_operand_combination[i]:
				expr += possible_operand_combination[i]
			expr += number_str[i + 1]
		expr += ')'

		# this regex matches on expressions containing no parentheses inside it other
		# than the encapsulating ones
		# if this matches, then the encapsulating parentheses are no longer needed
		# if this doesn't match, then the encapsulating parentheses are needed
		if not len(list(re.finditer(r'^\([^()]+\)$', expr))) == 0:
			expr = expr[1:-1]

		# this matches if it can find a number wrapped in parentheses without an operand inside it
		wrapped_numbers = list(re.finditer(r'\(\d+\)', expr))

		# if there are any numbers (not expressions) that are wrapped in parentheses
		# remove the surrounding parentheses from them
		subtract = 0
		for parentheses in wrapped_numbers:
			expr = expr[:parentheses.start() - subtract] + expr[parentheses.start() - subtract + 1:]
			subtract += 1
			expr = expr[:parentheses.end() - 1 - subtract] + expr[parentheses.end() - subtract:]
			subtract += 1

		process = multiprocessing.Process(target=evaluate, args=(expr, solutions))
		process.start()
		process.join(TIMEOUT)

		if process.is_alive():
			error_exprs.append((expr, 'timeout'))
			process.terminate()
			process.join()

	# prints out all solutions
	for solution in solutions:
		print solution

	# prints out all un-evaluated expressions
	for error_expr in error_exprs:
		print error_expr[0], 'could not be computed because of a', error_expr[1]

	return solutions

# in order to use, run it from bash as python subway.py [number]
if __name__ == '__main__':
	if len(sys.argv) < 2:
		print 'must supply argument, please call from command line as such:\n\n' + ' ' * 4 + 'python subway.py 1234\n\n'
		quit()

	solver(sys.argv[1])
