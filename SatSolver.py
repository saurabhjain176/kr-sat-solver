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

    #remove rules bigger than 4x4
    #for clause in rules.clauses:
    #  if int(str(clause)[0]).startswith(range(int(str(example.num_vars)[0]),int(str())):


    return example.clauses, rules.clauses

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

def select_absolute_literal(cnf):
  for clause in cnf:
    for literal in clause:
      return literal


def difference(list1, list2):
  if type(list2) == int:
    list2=[list2]
  return (list(list(set(list1)-set(list2)) + list(set(list2)-set(list1))))

def dpll(cnf, assignments=[]):
  print("assignments: ", assignments, "   with len cnf: ",len(cnf))

  if len(cnf) == 0:
    print("done with: ", assignments)
    return assignments

  if any([len(c) == 0 for c in cnf]):
    return False, None

  lit = select_absolute_literal(cnf)

  new_cnf = [c for c in cnf if abs(lit) not in c]
  new_cnf = [difference(c, -abs(lit)) for c in new_cnf]
  new_assignments = assignments + [[abs(lit)]]

  #remove duplicates
  new_assignments = [list(x) for x in set(frozenset(y) for y in new_assignments)]
  #do new loop
  sat, vals = dpll(new_cnf, new_assignments)


  if sat:
    return sat, vals

  new_cnf = [c for c in cnf if -abs(lit) not in c]

  new_cnf = [difference(c, abs(lit)) for c in new_cnf]
  new_assignments = assignments + [[-abs(lit)]]

  #remove duplicates
  new_assignments = [list(x) for x in set(frozenset(y) for y in new_assignments)]
  #do new loop
  sat, vals = dpll(new_cnf, new_assignments)

  if sat:
    return sat, vals

  return False, None


if __name__ == '__main__':
  input_dir = "test_sudokus"
  file_name = '4x4.txt'
  output_dir = "encoded"
  encode_sudoku(input_dir, file_name, output_dir)
  example, rule = read_dimacs_file()
  print(example)
  dpll(rule, example)

