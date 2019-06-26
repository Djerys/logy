from boolean_lexer import lex
from boolean_parser import parse
from calculation import BooleanCalculator


def print_table(table):
    for key in table[0]:
        print(key, end='\t')
    print()
    for row in table:
        for key in row:
            print(row[key], end='\t')
        print()


expression = '(-x & z) V (y & -z) V (x & z)'
expression1 = 'x & y'

tokens = lex(expression)
ast = parse(tokens)

tokens = lex(expression1)
function_ast = parse(tokens)

calculator = BooleanCalculator(ast)
print_table(calculator.build_truth_table())
print(calculator.cast_to_fdnf())
print()

calculator.function = function_ast
print_table(calculator.build_truth_table())
print(calculator.cast_to_fcnf())
print()

