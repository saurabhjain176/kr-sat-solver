#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 10 17:16:56 2020

@author: saurabhjain
"""

import os
import re
import math
from typing import IO


def encode_sudoku(input_dir: str, file_name: str, output_dir: str):
    
    input_file: IO = open(input_dir+"/"+file_name, "r")
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
                column_counter+=1
            else:
                row_counter+=1
                column_counter = 1
            
            if token != '.':
                clause = (str(row_counter)+str(column_counter)+str(token)).replace(" ", "")
                clauses.append(re.sub(r"[^\w\s]", '', clause))
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_file_name: str = os.path.join(output_dir, file_name + '-' + str(i).rjust(4, '0') + '.cnf')
        output_file: IO = open(output_file_name, 'w')
        output_file.write("p cnf {} {}\n".format(str(int(size)) * 3, len(clauses)))
        for clause in clauses:
            output_file.write("".join(clause) + " 0\n")
        output_file.close()
                
        
if __name__ == '__main__':
    input_dir = "test_sudokus"
    file_name = '4x4.txt'
    output_dir = "encoded"
    encode_sudoku(input_dir, file_name, output_dir)