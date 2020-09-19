import sys
import mxklabs.dimacs
import numpy as np
import os
import re
import math
from typing import IO
import sys
from collections import Counter
sys.setrecursionlimit(12500)



def read_dimacs_file(input_file):
  try:
    # Read the DIMACS files
    #input_file = sys.argv[1]
    example = mxklabs.dimacs.read(input_file)
    rules = mxklabs.dimacs.read("input//sudoku-rules.txt")

    #create a dictionary with keys as every option in sodoku and value yet to be assigned
    num_digits = len(str(example.num_vars))
    minimal_literal = int(num_digits*str(1))
    maximal_literal = int(num_digits * str(str(example.num_vars)[0]))
    value = None
    assignment = {k:value for k in range(minimal_literal, maximal_literal + 1)}
    #we can set the literals already to true of it is in the example
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

def rewrite_clause(clauses, assignment, literal, is_pure_literal):


  value = False if literal < 0 else True

  if (assignment[abs(literal)] == None or assignment[abs(literal)] == value):
    assignment[abs(literal)] = value

  elif not is_pure_literal:
    return False, False
  elif is_pure_literal:
    return clauses, assignment

  new_clauses = []
  for clause in clauses:
    if -literal in clause:
      clause.remove(-literal)
      new_clauses.append(clause)
    elif (literal not in clause) and (-literal not in clause):
      new_clauses.append(clause)

  return new_clauses, assignment



def dpll(clauses, assignment, type_of_heur):
  # The following code is derived from slide 10 of '2a Davis Putnam'
  # 1.1 remove tautologies
  numloops = 0
  for clause in clauses:
    for literal in clause:
      if -literal in clause:
        clauses.remove(clause)


  return looping(clauses, assignment, numloops, type_of_heur)


def empty(clauselist):
    a = 0
    for clause in clauselist:
        if not clause:
            a = a + 1
    return a

def looping(clauses, assignment, numloops, type_of_heur):
  numloops += 1

  if len(clauses) == 0:
    print("SATISFIABLE")
    print("num of loops", numloops)
    # return all the literals with true assigned, those are the numbers to be filled in sudoku
    print("assignment: ", [k for k, v in assignment.items() if assignment[k] == True])
    return True
  a = empty(clauses)
  if a > 0:
    print('empty')
    return False

  else:

    #1.3 check unit clauses
    #take all the literal that are unit clauses and rewrite the clauses where these unit clauses are in
    unit_literals = [clause[0] for clause in clauses if len(clause) == 1]
    for ul in unit_literals:
      clauses, assignment = rewrite_clause(clauses, assignment, ul, False)

    #if the above code returns false for the assignment, the sudoku for the literal assingment is not satisfiable
    if assignment == False:
      print("UNSAT")
      return False

    #keep going untill there arent unit clauses left
    if len(unit_literals) != 0:
      return looping(clauses, assignment, numloops, type_of_heur)

    # 1.2 check pure literals
    #However, checking pure literals for first loop seems redundant as there is no pure literal present initially
    flat_clauses = [l for clause in clauses for l in clause]
    pure_literals = [l for l in flat_clauses if -l not in flat_clauses]

    #iterate over all pure literals
    for pl in pure_literals:
      clauses, assignment = rewrite_clause(clauses, assignment, pl, True)

    #keep going untill there arent pure literals left
    if len(pure_literals) != 0:
      return looping(clauses, assignment, numloops, type_of_heur)

    if type_of_heur == "heur1":
      chosen_literal = MOM_heuristic1(clauses)
    elif type_of_heur == "heur2":
      chosen_literal = MOM_heuristic2(clauses)
    else:
      chosen_literal = random_assignment(clauses)
    print(chosen_literal)

    new_clauses, new_assignment = rewrite_clause(clauses, assignment, chosen_literal, False)
    #current_sat_satisfied =
    # if the current assignment is not satisfiable
    if looping(new_clauses, new_assignment, numloops, type_of_heur) == False:
      print(0)
      chosen_literal = -chosen_literal
      new_clauses, new_assignment = rewrite_clause(clauses, assignment, (-int(chosen_literal)), True)
      return looping(new_clauses, new_assignment, numloops, type_of_heur)


    return True


def random_assignment(clauses):
  # set one literal to true to explore if satifiable
  random_literal = int(np.random.choice([l for clause in clauses for l in clause]))
  return random_literal

def MOM_heuristic1(clauses):
  #implementing the normal MOM formula: [f∗(x) + f∗(¬x)] ∗ 2k + f∗(x) ∗ f∗(¬x)
  # first determine what the size is of the smallest clauses
  smallest_size_clause = min(set([len(clause) for clause in clauses]))
  #select only the literals which are in the smallest clauses, and then count all these values
  counted_lits_in_smallest_clauses = Counter([l for clause in clauses for l in clause if len(clause) == smallest_size_clause])
  score_mom_heur = dict()
  k = 10
  for key, count in list(counted_lits_in_smallest_clauses.items()):
    #here is the function
    score = (count + counted_lits_in_smallest_clauses[-key]) * 2^k + count * counted_lits_in_smallest_clauses[-key]
    # delete the opposite count of the literal, as this is not necessary to perform the formula, becuase it will give the same value as the intitial literal
    del counted_lits_in_smallest_clauses[-key]
    #add the score of the literal to the dict
    score_mom_heur[abs(key)] = score
  print(max(score_mom_heur, key=score_mom_heur.get))
  #return the key with the maximal value in the dict
  return max(score_mom_heur, key=score_mom_heur.get)

def MOM_heuristic2(clauses):
  # still to be implemented
  return 0





if __name__ == '__main__':
  input_dir = "test_sudokus"
  file_name = '100 sudokus.txt'
  output_dir = "encoded"
  #encode_sudoku(input_dir, file_name, output_dir)
  example, rule, assignment = read_dimacs_file("encoded//100 sudokus.txt-0000.cnf")

  clauses = example + rule
  heuristic = "heur12"
  dpll(clauses, assignment, heuristic)



#  def select_absolute_literal(cnf):
#   for clause in cnf:
#     for literal in clause:
#       return literal
#
#
# def difference(list1, list2):
#   if type(list2) == int:
#     list2=[list2]
#   return (list(list(set(list1)-set(list2)) + list(set(list2)-set(list1))))
#
# def dpll(cnf, assignments=[]):
#   print("assignments: ", assignments, "   with len cnf: ",len(cnf))
#
#   if len(cnf) == 0:
#     print("done with: ", assignments)
#     return assignments
#
#   if any([len(c) == 0 for c in cnf]):
#     return False, None
#
#   lit = select_absolute_literal(cnf)
#
#   new_cnf = [c for c in cnf if abs(lit) not in c]
#   new_cnf = [difference(c, -abs(lit)) for c in new_cnf]
#   assignments = assignments + [[abs(lit)]]
#
#   #remove duplicates
#   assignments = [list(x) for x in set(frozenset(y) for y in assignments)]
#   #do new loop
#   sat, vals = dpll(new_cnf, assignments)
#
#
#   if sat:
#     return sat, vals
#
#   new_cnf = [c for c in cnf if -abs(lit) not in c]
#
#   new_cnf = [difference(c, abs(lit)) for c in new_cnf]
#   assignments = assignments + [[-abs(lit)]]
#
#   #remove duplicates
#   assignments = [list(x) for x in set(frozenset(y) for y in assignments)]
#   #do new loop
#   sat, vals = dpll(new_cnf, assignments)
#
#   if sat:
#     return sat, vals
#
#   return False, None
