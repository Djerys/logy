import functools

import boolean_ast as ast


class ConstantFunctionError(Exception):
    pass


class BooleanCalculator(object):
    def __init__(self, function):
        self.function = function

    def function_have_variables(self):
        return True if self.function.variables else False

    def build_truth_table(self):
        if not self.function_have_variables():
            raise ConstantFunctionError(
                f'{self.function} does not have variables.')

        return self._truth_table(self.function)

    def cast_to_fcnf(self):
        truth_table = self.build_truth_table()
        nodes = [self._group_to_term(row, lambda x: x, lambda a, b: a | b)
                 for row in truth_table if not row['F']]

        fcnf = functools.reduce(lambda a, x: a & x, nodes)
        return fcnf

    def cast_to_fdnf(self):
        truth_table = self.build_truth_table()
        nodes = [self._group_to_term(row, lambda x: not x, lambda a, b: a & b)
                 for row in truth_table if row['F']]

        fdnf = functools.reduce(lambda a, x: a | x, nodes)
        return fdnf

    @staticmethod
    @functools.lru_cache()
    def _truth_table(function):
        variables = list(function.variables)
        variables.sort()
        variable_values_list = [dict(zip(variables, subset))
                                for subset in _subsets(len(variables))]

        table = []
        for variable_values in variable_values_list:
            variable_values['F'] = function.calculate(variable_values)
            table.append(variable_values)
        return table

    @staticmethod
    def _group_to_term(truth_table_row, should_invert, group_operation):
        nodes = []
        for variable in set(truth_table_row) - {'F'}:
            if should_invert(truth_table_row[variable]):
                nodes.append(~ast.VariableExpression(variable))
            else:
                nodes.append(ast.VariableExpression(variable))
        term = functools.reduce(group_operation, nodes)
        return term


def _subsets(power):
    for i in range(2 ** power):
        str_subset = bin(i).lstrip('0b').rjust(power, '0')
        subset = [int(x) for x in str_subset]
        yield subset
