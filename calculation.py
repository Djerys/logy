import functools

import boolean_ast as ast


class ConstantFunctionError(Exception):
    pass


class BooleanCalculator(object):
    def __init__(self, ast):
        self._ast = ast

    @property
    def ast(self):
        return self._ast

    def function_have_variables(self):
        return True if self.ast.variables else False

    @property
    @functools.lru_cache()
    def truth_table(self):
        if not self.function_have_variables():
            raise ConstantFunctionError(
                f'{self.ast} does not have variables.')

        variables = list(self.ast.variables)
        variables.sort()
        variable_values_list = [dict(zip(variables, subset))
                                for subset in _subsets(len(variables))]

        table = []
        for variable_values in variable_values_list:
            variable_values['F'] = self.ast.calculate(variable_values)
            table.append(variable_values)
        return table

    @property
    @functools.lru_cache()
    def fcnf(self):
        nodes = [self._disjunction(row) for row in self.truth_table
                 if not row['F']]

        fcnf_ast = functools.reduce(lambda a, x: a & x, nodes)
        return fcnf_ast

    @property
    @functools.lru_cache()
    def fdnf(self):
        nodes = [self._conjunction(row) for row in self.truth_table
                 if row['F']]

        fdnf_ast = functools.reduce(lambda a, x: a | x, nodes)
        return fdnf_ast

    @staticmethod
    def _disjunction(truth_table_row):
        nodes = []
        for variable in set(truth_table_row) - {'F'}:
            if truth_table_row[variable]:
                nodes.append(~ast.VariableExpression(variable))
            else:
                nodes.append(ast.VariableExpression(variable))

        disjunction = functools.reduce(lambda a, x: a | x, nodes)
        return disjunction

    @staticmethod
    def _conjunction(truth_table_row):
        nodes = []
        for variable in set(truth_table_row) - {'F'}:
            if truth_table_row[variable]:
                nodes.append(ast.VariableExpression(variable))
            else:
                nodes.append(~ast.VariableExpression(variable))

        conjunction = functools.reduce(lambda a, x: a & x, nodes)
        return conjunction


def _subsets(power):
    for i in range(2 ** power):
        str_subset = bin(i).lstrip('0b').rjust(power, '0')
        subset = [int(x) for x in str_subset]
        yield subset
