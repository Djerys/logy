import sys
import cmd

import boolean_lexer as blex

from boolean_parser import parse
from calculation import BooleanCalculator, ConstantError


class CalculatorInterpreter(cmd.Cmd):
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.calculator = None
        self.prompt = '> '
        self.intro = ('-----------*-----------Logy-----------*-----------\n\n'
                      'Logy is a boolean calculator with console interface.\n'
                      'Use the command "help" to learn more:\n'
                      '                       ***\n')
        self.doc_leader = ('Logy allows such boolean operations as:\n'
                           '=======================================\n'
                           f'NOT     {blex.NOT}\n'
                           f'AND     {blex.AND}\n'
                           f'OR      {blex.OR}\n'
                           f'NAND    {blex.NAND}\n'
                           f'NOR     {blex.NOR}\n'
                           f'EQ      {blex.EQ}\n'
                           f'IMPLY   {blex.IMPLY}\n'
                           'Some expressions for example:\n'
                           '=============================\n'
                           '-(a + b) -> c\n'
                           'a + b * c ^ 1 <-> 0\n'
                           'a / b ! c / a\n\n'
                           'You can use the help command to learn what other\n'
                           'commands are doing.\n'
                           'For example:\n'
                           '============\n'
                           '> table a + b * c -> -d\n'
                           '> help load\n'
                           '> load a + b * c -> -d\n'
                           '> table')
        self.doc_header = 'Commands you can use:'

    def do_load(self, expression):
        """# Loads function and allows write commands without arguments."""
        try:
            self.calculator = get_calculator(expression)
        except ValueError:
            print('! Expression is not correct')
        else:
            print('# Function loaded successfully.')

    def do_loaded(self, empty):
        """# Returns loaded function or warning message."""
        if self.calculator:
            print(self.calculator.function)
        else:
            print('! No loaded function.')

    def do_table(self, expression):
        """# Builds truth table for function."""
        self._handle_optional_command(
            expression,
            lambda: print_table(get_calculator(expression).build_truth_table()),
            lambda: print_table(self.calculator.build_truth_table()))

    def do_fdnf(self, expression):
        """# Casts function to FCNF (full conjunctive normal form)."""
        self._handle_optional_command(
            expression,
            lambda: print(get_calculator(expression).cast_to_fdnf()),
            lambda: print(self.calculator.cast_to_fdnf()))

    def do_fcnf(self, expression):
        """# Casts function to FDNF (full disjunctive normal form)."""
        self._handle_optional_command(
            expression,
            lambda: print(get_calculator(expression).cast_to_fcnf()),
            lambda: print(self.calculator.cast_to_fcnf()))

    def do_poly(self, expression):
        """# Casts function to Zhegalkin polynomial."""
        self._handle_optional_command(
            expression,
            lambda: print(get_calculator(expression).cast_to_zhegalkin()),
            lambda: print(self.calculator.cast_to_zhegalkin()))

    def do_min(self, expression):
        """# Minimizes function using Quine–McCluskey algorithm."""
        self._handle_optional_command(
            expression,
            lambda: print(get_calculator(expression).minimize()),
            lambda: print(self.calculator.minimize())
        )

    def do_close(self, empty):
        """# Closes Logy."""
        sys.exit()

    def default(self, line):
        print('! Unknown command.')

    def _handle_optional_command(self, expression, standard_option, loaded_option):
        try:
            if expression:
                try:
                    standard_option()
                except ValueError:
                    print('! Expression is not correct')
            elif self.calculator:
                loaded_option()
            else:
                print('! No arguments and no loaded function.')
        except ConstantError as error:
            print(f'! Function always takes one value: {error.args[-1]}.')


def get_calculator(expression):
    tokens = blex.lex(expression)
    function = parse(tokens)
    return BooleanCalculator(function)


def print_table(table):
    for variable in table[0]:
        print(variable, end='\t')
    print()
    for row in table:
        for variable in row:
            separator = ' ' * (len(variable) // 2)
            print(separator, row[variable], end='\t', sep='')
        print()
