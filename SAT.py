import time
import mxklabs.dimacs
import numpy as np
import os
import copy
import re
import math
from typing import IO
import sys
import csv
from collections import Counter
from datetime import datetime

sys.setrecursionlimit(12500)


def read_dimacs_file(input_file, rule_file):
    try:
        # Read the DIMACS files
        # input_file = sys.argv[1]
        example = mxklabs.dimacs.read(input_file)
        rules = mxklabs.dimacs.read(rule_file)
        # create a dictionary with keys as every option in sodoku and value yet to be assigned
        num_digits = len(str(example.num_vars))
        minimal_literal = int(num_digits * str(1))
        maximal_literal = int(num_digits * str(str(example.num_vars)[0]))
        value = None
        assignment = {k: value for k in range(minimal_literal, maximal_literal + 1)}
        # we can set the literals already to true of it is in the example
        for givenSudokuNum in example.clauses:
            assignment[givenSudokuNum[0]] = True
        return example.clauses, rules.clauses, assignment

    except Exception as e:
        # Report error.
        print(e)


def encode_sudoku(input_dir: str, file_name: str, output_dir: str):
    input_file: IO = open(input_dir + "/" + file_name, "r")
    for i, sudoku in enumerate(input_file):
        sudoku: str = re.sub('[^1-9A-Z.]', '', sudoku)
        size: float = math.sqrt(len(sudoku))
        # Check Sudoku dimensions
        if not size.is_integer():
            print("Sudoku '{0}' does not have square dimensions.".format(sudoku))
            continue

        row_counter = 1
        column_counter = 0
        clauses = []
        for token in sudoku:
            if column_counter != size:
                column_counter += 1
            else:
                row_counter += 1
                column_counter = 1

            if token != '.':
                clause = (str(row_counter) + str(column_counter) + str(token)).replace(" ", "")
                clauses.append(re.sub(r"[^\w\s]", '', clause))

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_file_name: str = os.path.join(output_dir, file_name + '-' + str(i).rjust(4, '0') + '.cnf')
        output_file: IO = open(output_file_name, 'w')
        output_file.write("p cnf {} {}\n".format(str(int(size)) * 3, len(clauses)))
        for clause in clauses:
            output_file.write("".join(clause) + " 0\n")
        output_file.close()


def rewrite_clause(clauses, assignment, literal, backtrack_allowence_bool):
    assignment = copy.deepcopy(assignment)
    copied_clauses = copy.deepcopy(clauses)
    value = False if literal < 0 else True

    if (assignment[abs(literal)] == None or assignment[abs(literal)] == value):
        assignment[abs(literal)] = value
    # backtrack_bool indicates whether to conclude that the sudoku is UNSAT or an assignment should be flipped
    elif not backtrack_allowence_bool:
        return clauses, False
    elif backtrack_allowence_bool:
        return clauses, assignment

    new_clauses = []
    for clause in copied_clauses:
        if (literal not in clause) and (-literal not in clause):
            new_clauses.append(clause)
        elif -literal in clause:
            clause.remove(-literal)
            new_clauses.append(clause)

    return new_clauses, assignment

def write_dimacs(file_name, solution):
    file_out: str = os.path.join(file_name + ".out")
    output_file: IO = open(file_out, 'w')
    output_file.write("p cnf {} {}\n".format(str(max(solution)), str(len(solution))))
    for clause_out in solution:
        output_file.write("{} 0\n".format(str(clause_out)))

    output_file.close() 

def print_solution(solution):
    sqrt: float = math.sqrt(len(solution))
    if sqrt.is_integer():
        for row in range(0, len(solution), int(sqrt)):
            print(solution[row:row+int(sqrt)])
    else:
        print(solution)

def looping(clauses, assignment, type_of_heur, num_loops, num_assigns, num_backtrack):
    num_loops += 1
    are_empty_clauses = len([clause for clause in clauses if not clause]) > 0
    if are_empty_clauses:
        return False, num_loops, num_assigns, num_backtrack
    elif len(clauses) == 0:
        solution =  [k for k, v in assignment.items() if assignment[k] == True]
        print_solution(solution)
        write_dimacs(sys.argv[3], solution)
        return True, num_loops, num_assigns, num_backtrack

    # 1.2 check pure literals
    # However, checking pure literals for first loop seems redundant as there is no pure literal present initially
    if num_loops != 0:
        flat_clauses = [l for clause in clauses for l in clause]
        pure_literals = [l for l in flat_clauses if -l not in flat_clauses]

        # iterate over all pure literals
        for pl in pure_literals:
            clauses, assignment = rewrite_clause(clauses, assignment, pl, True)

        # keep going untill there arent pure literals left
        if len(pure_literals) != 0:
            return looping(clauses, assignment, type_of_heur, num_loops, num_assigns, num_backtrack)

    # 1.3 check unit clauses
    # take all the literal that are unit clauses and rewrite the clauses where these unit clauses are in
    unit_literals = [clause[0] for clause in clauses if len(clause) == 1]
    for unit_literal in unit_literals:
        clauses, assignment = rewrite_clause(clauses, assignment, unit_literal, False)

    # if the above code returns false for the assignment, the sudoku for the literal assingment is not satisfiable
    if assignment == False:
        print("UNSAT")
        return False, num_loops, num_assigns, num_backtrack

    # keep going untill there arent unit clauses left
    if len(unit_literals) != 0:
        return looping(clauses, assignment, type_of_heur, num_loops, num_assigns, num_backtrack)

    if type_of_heur == "heur1":
        chosen_literal = heuristic1(clauses)
    elif type_of_heur == "heur2":
        chosen_literal = heuristic2(clauses)
    else:
        chosen_literal = random_assignment(clauses)
    num_assigns += 1
    new_clauses, new_assignment = rewrite_clause(clauses, assignment, chosen_literal, False)

    satisfied, num_loops, num_assigns, num_backtrack = looping(new_clauses, new_assignment, type_of_heur, num_loops, num_assigns, num_backtrack)
    if not satisfied:
        num_backtrack += 1
        new_clauses, new_assignment = rewrite_clause(clauses, assignment, -chosen_literal, True)
        return looping(new_clauses, new_assignment, type_of_heur, num_loops, num_assigns, num_backtrack)
    return True, num_loops, num_assigns, num_backtrack


def dpll(clauses, assignment, type_of_heur):
    # The following code is derived from slide 10 of '2a Davis Putnam'
    # 1.1 remove tautologies
    num_loops = 0
    num_assigns = 0
    num_backtrack = 0
    # clauses = list(set([clause for clause in clauses for l in clause if not -l in clause]))
    for clause in clauses:
        for literal in clause:
            if -literal in clause:
                clauses.remove(clause)
    satisfied, num_loops, num_assigns, num_backtrack = looping(clauses, assignment, type_of_heur, num_loops, num_assigns,
                                                    num_backtrack)
    return satisfied, num_loops, num_assigns, num_backtrack


def random_assignment(clauses):
    # set one literal to true to explore if satifiable
    random_literal = np.random.choice([l for clause in clauses for l in clause])
    return random_literal


def heuristic1(clauses):
    # implementing the normal MOM formula: [f∗(x) + f∗(¬x)] ∗ 2k + f∗(x) ∗ f∗(¬x)
    # first determine what the size is of the smallest clauses
    smallest_size_clause = min(set([len(clause) for clause in clauses]))
    # select only the literals which are in the smallest clauses, and then count all these values
    counted_lits_in_smallest_clauses = Counter(
        [l for clause in clauses for l in clause if len(clause) == smallest_size_clause])
    score_mom_heur = dict()
    # TODO: k still to be determined
    k = 10
    for key, count in list(counted_lits_in_smallest_clauses.items()):
        # here is the function
        score = (count + counted_lits_in_smallest_clauses[-key]) * 2 ^ k + count * counted_lits_in_smallest_clauses[
            -key]
        # delete the opposite count of the literal, as this is not necessary to perform the formula, becuase it will give the same value as the intitial literal
        del counted_lits_in_smallest_clauses[-key]
        # add the score of the literal to the dict
        score_mom_heur[abs(key)] = score
    # return the key with the maximal value in the dict
    return max(score_mom_heur, key=score_mom_heur.get)


def heuristic2(clauses):
    max_unsat_clause = {}
    for clause in clauses:
        for literal in clause:
            if literal in max_unsat_clause:
                max_unsat_clause[literal] += 1
            else:
                max_unsat_clause[literal] = 1
    return max(max_unsat_clause, key=max_unsat_clause.get)


def create_csv_file(name_file):
    # this creates a csv in the same directory folder
    with open(name_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Run", "CPU Time", "Number of Loops", "Number of Assigns", "Number of Backtracks"])


def write_line_to_csv(cpu_time, num_loops, num_assigns, num_backtrack, num_run, name_file):
    with open(name_file, 'a+', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([num_run, cpu_time, num_loops, num_assigns, num_backtrack])
    # implemeted in such a way that it adds a single line every time


if __name__ == '__main__':
    heuristics_dict = {'-S1': 'heur1', '-S2': 'heur2', '-S3': 'random'}
    if sys.argv[1] not in heuristics_dict:
        print("Value of first argument is '{}', '-S1' '-S2' or '-S3' expected.".format(sys.argv[1]))
    elif not os.path.exists(sys.argv[2]):
        print("File: '{}' does not exist".format(sys.argv[2]))

    input_file = sys.argv[3]
    clauses_file = sys.argv[2]
    heuristic = heuristics_dict.get(sys.argv[1])

    try:
        example, rule, assignment = read_dimacs_file(input_file, clauses_file)
        dpll_input = example + rule
        satisfied, num_loops, num_assigns, num_backtrack = dpll(dpll_input, assignment, heuristic)
    except Exception as e:
        print("Something went wrong ", e)