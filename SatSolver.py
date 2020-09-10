import sys
import mxklabs.dimacs

try:
  # Read the DIMACS files
  example = mxklabs.dimacs.read(sys.argv[1])
  rules = mxklabs.dimacs.read("sudoku-rules.txt")
  # Print some stats.
  print("num_vars=%d, num_clauses=%d" % (example.num_vars, example.num_clauses))
  #You can see the example as rules as well. We can throw all the rules together and then apply the algortihm to it
  all_clauses = example.clauses + rules.clauses


except Exception as e:
  # Report error.
  print(e)

