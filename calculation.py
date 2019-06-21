from functools import reduce

import boolean_ast as ast


class BooleanCalculator(object):
    def __init__(self, ast):
        self._ast = ast
        self._truth_table = None
        self._fcnf = None
        self._fdnf = None

    @property
    def ast(self):
        return self._ast

    @property
    def truth_table(self):
        if self._truth_table is None:
            variables = list(self.ast.variables)
            variables.sort()
            variable_values_list = [dict(zip(variables, subset))
                                    for subset in _subsets(len(variables))]

            self._truth_table = []
            for variable_values in variable_values_list:
                variable_values['F'] = self.ast.calculate(variable_values)
                self._truth_table.append(variable_values)

        return self._truth_table

    @property
    def fcnf(self):
        if self._fcnf is None:
            truth_table = self.truth_table
            nodes = [self._fcnf_sum(row) for row in truth_table
                     if self._fcnf_sum(row) is not None]
            self._fcnf = reduce(lambda a, x: a & x, nodes)

        return self._fcnf

    @property
    def fdnf(self):
        if self._fdnf is None:
            truth_table = self.truth_table
            nodes = [self._fdnf_product(row) for row in truth_table
                     if self._fdnf_product(row) is not None]
            self._fdnf = reduce(lambda a, x: a | x, nodes)

        return self._fdnf

    def _fcnf_sum(self, variable_values):
        if variable_values['F']:
            return None
        nodes = []
        for variable in set(variable_values) - {'F'}:
            if variable_values[variable]:
                nodes.append(
                    ast.NotExpression(ast.VariableExpression(variable)))
            else:
                nodes.append(ast.VariableExpression(variable))
        fcnf_sum = reduce(lambda a, x: a | x, nodes)
        return fcnf_sum

    def _fdnf_product(self, variable_values):
        if not variable_values['F']:
            return None
        nodes = []
        for variable in set(variable_values) - {'F'}:
            if variable_values[variable]:
                nodes.append(ast.VariableExpression(variable))
            else:
                nodes.append(
                    ast.NotExpression(ast.VariableExpression(variable)))
        fdnf_product = reduce(lambda a, x: a & x, nodes)
        return fdnf_product


def _subsets(power):
    for i in range(2 ** power):
        str_subset = bin(i).lstrip('0b').rjust(power, '0')
        subset = [int(x) for x in str_subset]
        yield subset
