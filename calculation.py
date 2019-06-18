class BooleanCalculator(object):
    def __init__(self, ast):
        self._ast = ast

    @property
    def ast(self):
        return self._ast

    @property
    def truth_table(self):
        variables = self.ast.variables
        variables = list(variables)
        variables.sort()
        variable_values_list = [dict(zip(variables, subset))
                                for subset in _subsets(len(variables))]

        table = []
        for variable_values in variable_values_list:
            variable_values['F'] = self.ast.calculate(variable_values)
            table.append(variable_values)
        return table


def _subsets(power):
    for i in range(2 ** power):
        str_subset = bin(i).lstrip('0b').rjust(power, '0')
        subset = [int(x) for x in str_subset]
        yield subset


if __name__ == '__main__':
    print(list(_subsets(3)))