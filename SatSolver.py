import sys
import mxklabs.dimacs
import os
import re
import math
from typing import IO



def read_dimacs_file():
  try:
    # Read the DIMACS files
    #input_file = sys.argv[1]
    input_file = "encoded//top100.sdk.txt-0000.cnf"
    example = mxklabs.dimacs.read(input_file)
    rules = mxklabs.dimacs.read("input//sudoku-rules.txt")
    # Print some stats.
    print("num_vars=%d, num_clauses=%d" % (example.num_vars, example.num_clauses))
    #You can see the example as rules as well. We can throw all the rules together and then apply the algortihm to it
    all_clauses = example.clauses + rules.clauses

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

#def newClause(oldClause, newClause):


def dpll(clauses, assignment):
  print(len(clauses))
  # The following code is derived from slide 10 of '2a Davis Putnam'
  # 1.1 remove tautologies
  clausesToRemove = []
  for clause in clauses:
    for literal in clause:
      if -literal in clause:
        clausesToRemove.append(clause)

  if clausesToRemove != []:
    clauses.remove(clause)

  print("after Taut: ",len(clauses))
  looping(clauses, assignment)

def looping(clauses, assignment):
  # 1.2
  flat_clauses = [l for clause in clauses for l in clause]
  pure_literals = [l for l in flat_clauses if -l not in flat_clauses]
  #iterate over all pure literals
  for pure in pure_literals:
    clausesToRemove = []
    for clause in clauses:
      #if a pure literal occurs in a clause it should remove that literal from that clause if
      # it is negative, otherwise (positive) remove whole clause
      #TODO: not sure what to do here
      if pure in clause:
        # if pure.startswith('-'):
        #   clause.remove(pure)
        # else:
        #   clausesToRemove.append(clause)
        assignment[abs(pure)] = True

      #clauses.remove(clausesToRemove)

  #1.3 unit clause
  for clause in clauses:
    clausesToRemove = []
    if len(clause) == 1:
      assignment[clause[0]] = True
      clausesToRemove.append(clause)

  if clausesToRemove != []:
    clauses.remove(clausesToRemove)

  print("after Unit: ",len(clauses))
  if len(clauses) != 0:
    looping(clauses, assignment)
  else:
    return assignment
    #return all the literals with true assigned, those are the numbers to be filled in sudoku
    #return([k for k, v in assignment.items() if assignment[k]==True])


if __name__ == '__main__':
  input_dir = "test_sudokus"
  file_name = '4x4.txt'
  output_dir = "encoded"
  encode_sudoku(input_dir, file_name, output_dir)
  example, rule, assignment = read_dimacs_file()
  print(example)
  rules = dpll(rule, assignment)
  print(rules)


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
#   new_assignments = assignments + [[abs(lit)]]
#
#   #remove duplicates
#   new_assignments = [list(x) for x in set(frozenset(y) for y in new_assignments)]
#   #do new loop
#   sat, vals = dpll(new_cnf, new_assignments)
#
#
#   if sat:
#     return sat, vals
#
#   new_cnf = [c for c in cnf if -abs(lit) not in c]
#
#   new_cnf = [difference(c, abs(lit)) for c in new_cnf]
#   new_assignments = assignments + [[-abs(lit)]]
#
#   #remove duplicates
#   new_assignments = [list(x) for x in set(frozenset(y) for y in new_assignments)]
#   #do new loop
#   sat, vals = dpll(new_cnf, new_assignments)
#
#   if sat:
#     return sat, vals
#
#   return False, None
