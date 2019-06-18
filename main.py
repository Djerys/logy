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


expression = 'x V y & z -> z V x'
expression1 = '1 & 1 V 0 V 0 / 1'
tokens = lex(expression)
print(tokens)
ast = parse(tokens)
print(ast.variables)
print(ast)
calculator = BooleanCalculator(ast)
print_table(calculator.truth_table)

