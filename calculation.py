import functools
from copy import deepcopy
from collections import OrderedDict

import boolean_ast as ast


class ConstantError(Exception):
    pass


class BooleanCalculator(object):
    def __init__(self, function):
        self.function = function
        self.F = str(self.function)

    def function_is_constant(self):
        table = self._truth_table(self.function)
        return (all([row[self.F] == 1 for row in table])
                or all([row[self.F] == 0 for row in table]))

    def build_truth_table(self):
        """
        Returns truth table if function is not constant.

        Raises:
            ConstantError: An error occurred building truth table
            if function always takes one value.

        """
        if self.function_is_constant():
            raise ConstantError(
                f'{self.F} is constant.',
                self._truth_table(self.function)[0][self.F])

        # Deepcopy because using lru_cache.
        return deepcopy(self._truth_table(self.function))

    def cast_to_fcnf(self):
        return self._cnf(self._false_vectors())

    def cast_to_fdnf(self):
        return self._dnf(self._true_vectors())

    def cast_to_zhegalkin(self):
        triangle_table = self._build_triangle_table()
        self._fill_triangle_table(triangle_table)
        terms = self._zhegalkin_xored(triangle_table[:2])
        return self._xor_all(terms)

    def minimize(self):
        """
        Minimizes function using Quine–McCluskey algorithm.
        If function takes a value of 0 or 1 then returns it.

        """
        try:
            vectors = self._true_vectors()
        except ConstantError as exc:
            return exc.args[-1]

        vectors.sort(key=lambda x: list(x.values()).count(1))
        result_vectors = []
        while vectors:
            vectors, not_glued = self._glue_vectors(vectors)
            result_vectors.extend(not_glued)
            vectors = self._deleted_sames(vectors)
            result_vectors = self._deleted_sames(result_vectors)

        for i, vector in enumerate(result_vectors):
            result_vectors[i] = {var: vector[var] for var in vector
                                 if vector[var] != '-'}
        return self._dnf(result_vectors)

    @functools.lru_cache()
    def _truth_table(self, function):
        """Returns truth table using LRU cache."""
        variables = list(function.variables)
        variables.sort()
        variable_values_list = [OrderedDict(zip(variables, subset))
                                for subset in _subsets(len(variables))]

        table = []
        for variable_values in variable_values_list:
            variable_values[self.F] = function.calculate(variable_values)
            table.append(variable_values)
        return table

    def _dnf(self, vectors):
        terms = self._grouped_to_terms(
            vectors, lambda x: not x, lambda a: ~a,
            lambda a, b: a & b)

        return self._or_all(terms)

    def _cnf(self, vectors):
        terms = self._grouped_to_terms(
            vectors, lambda x: x, lambda a: ~a,
            lambda a, b: a | b)

        return self._and_all(terms)

    @staticmethod
    def _or_all(terms):
        return functools.reduce(lambda a, b: a | b, terms)

    @staticmethod
    def _and_all(terms):
        return functools.reduce(lambda a, b: a & b, terms)

    @staticmethod
    def _xor_all(terms):
        return functools.reduce(lambda a, b: a ^ b, terms)

    def _build_triangle_table(self):
        truth_table = self.build_truth_table()
        help_table = [[0 for _ in range(i)]
                      for i in range(len(truth_table), 0, -1)]
        for i in range(len(help_table)):
            help_table[i][0] = truth_table[i][self.F]
        terms = self._conjunction_terms(truth_table[1:])
        terms.insert(0, ast.ConstantExpression(1))
        help_table.insert(0, terms)
        return help_table

    @staticmethod
    def _fill_triangle_table(table):
        for j in range(1, len(table[1:])):
            for i in range(1, len(table[j])):
                table[i][j] = (table[i][j - 1] ^ table[i + 1][j - 1])

    @staticmethod
    def _zhegalkin_xored(terms_table):
        terms = []
        for term, should_be in zip(*terms_table):
            if should_be:
                terms.append(term)
        return terms

    def _conjunction_terms(self, vectors):
        terms = self._grouped_to_terms(
            vectors, lambda x: not x,
            lambda a: None,
            lambda a, b: a & b
        )

        return terms

    def _grouped_to_terms(self, vectors, should_modify,
                          modify, group_operation):
        terms = []
        for vector in vectors:
            nodes = []
            for variable in sorted(list(set(vector) - {self.F})):
                if should_modify(vector[variable]):
                    modified = modify(ast.VariableExpression(variable))
                    if modified:
                        nodes.append(modified)
                else:
                    nodes.append(ast.VariableExpression(variable))
            term = functools.reduce(group_operation, nodes)
            terms.append(term)
        return terms

    def _glue_vectors(self, vectors):
        vector_groups = self._grouped_by_ones_count(vectors)
        new_vectors = []
        glued_vectors = []
        for i in range(0, len(vector_groups) - 1):
            for vector1 in vector_groups[i]:
                for vector2 in vector_groups[i + 1]:
                    new_vector = self._glued(vector1, vector2)
                    if new_vector is not None:
                        new_vectors.append(new_vector)
                        glued_vectors.extend([vector1, vector2])

        not_glued = [v for v in vectors if v not in glued_vectors]
        return new_vectors, not_glued

    @staticmethod
    def _glued(vector1, vector2):
        new_vector = OrderedDict()
        difference_count = 0
        for variable, _ in zip(vector1, vector2):
            if vector1[variable] != vector2[variable]:
                new_vector[variable] = '-'
                difference_count += 1
            else:
                new_vector[variable] = vector1[variable]
        if difference_count == 1:
            return new_vector
        return None

    def _true_vectors(self):
        return [vector for vector in self.build_truth_table()
                if vector.pop(self.F)]

    def _false_vectors(self):
        return [vector for vector in self.build_truth_table()
                if not vector.pop(self.F)]

    @staticmethod
    def _deleted_sames(iterable):
        new = []
        for i in iterable:
            if i not in new:
                new.append(i)
        return new

    @staticmethod
    def _grouped_by_ones_count(vectors):
        groups = []
        group = []
        count = 0
        for vector in vectors:
            if list(vector.values()).count(1) == count:
                group.append(vector)
            else:
                count += 1
                groups.append(group)
                group = [vector]
        groups.append(group)
        return groups


def _subsets(power):
    for i in range(2 ** power):
        str_subset = bin(i).lstrip('0b').rjust(power, '0')
        subset = [int(x) for x in str_subset]
        yield subset
