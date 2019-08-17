from flask import Flask, render_template, request
from subway import solver
import os, json

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('form.html')

@app.route('/<number>')
def solution(number):
	try:
		int(number)
	except:
		return ('', 204)

	if len(number) != 4:
		raise ValueError('only 4 digit numbers are currently supported')

	file_name = './solutions/{0}.json'.format(number)
	if os.path.isfile(file_name):
		with open(file_name) as solutions_file:
			solutions = eval(solutions_file.read())
	else:
		solutions = solver(number)
		with open(file_name, 'w') as outfile:
			json.dump(solutions, outfile)

	num_solutions = len(solutions)
	is_solvable = num_solutions > 0
	return render_template('solution.html', number=number, solutions=solutions, num_solutions=num_solutions, is_solvable=is_solvable)