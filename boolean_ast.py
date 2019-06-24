import functools
from abc import ABC, abstractmethod


class Expression(ABC):
    @abstractmethod
    def __repr__(self):
        pass

    def __and__(self, other):
        return AndExpression(self, other)

    def __or__(self, other):
        return OrExpression(self, other)

    def __invert__(self):
        return NotExpression(self)

    @property
    @abstractmethod
    def variables(self):
        pass

    @abstractmethod
    def calculate(self, variable_values):
        pass


class NotExpression(Expression):
    def __init__(self, expression):
        self.expression = expression

    def __repr__(self):
        return f'NOT({self.expression})'

    @property
    @functools.lru_cache()
    def variables(self):
        return self.expression.variables

    def calculate(self, variable_values):
        result = not self.expression.calculate(variable_values)
        return int(result)


class ConstantExpression(Expression):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f'{self.value}'

    @property
    @functools.lru_cache()
    def variables(self):
        return set()

    def calculate(self, variable_values):
        return self.value


class VariableExpression(Expression):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

    @property
    @functools.lru_cache()
    def variables(self):
        return {self.name}

    def calculate(self, variable_values):
        if self.name not in variable_values:
            raise ValueError('No such variable value in given variables.')
        return variable_values[self.name]


class BinaryExpression(Expression):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    @abstractmethod
    def __repr__(self):
        return '{}' + f'({self.left}, {self.right})'

    @property
    @functools.lru_cache()
    def variables(self):
        return self.left.variables | self.right.variables


class AndExpression(BinaryExpression):
    def __repr__(self):
        return super().__repr__().format('AND')

    def calculate(self, variable_values):
        result = (self.left.calculate(variable_values)
                  and self.right.calculate(variable_values))
        return int(result)


class OrExpression(BinaryExpression):
    def __repr__(self):
        return super().__repr__().format('OR')

    def calculate(self, variable_values):
        result = (self.left.calculate(variable_values)
                  or self.right.calculate(variable_values))
        return int(result)


class XorExpression(BinaryExpression):
    def __repr__(self):
        return super().__repr__().format('XOR')

    def calculate(self, variable_values):
        left_value = self.left.calculate(variable_values)
        right_value = self.right.calculate(variable_values)
        result = ((not left_value and right_value)
                  or (left_value and not right_value))
        return int(result)


class NorExpression(BinaryExpression):
    def __repr__(self):
        return super().__repr__().format('NOR')

    def calculate(self, variable_values):
        result = not (self.left.calculate(variable_values)
                      or self.right.calculate(variable_values))
        return int(result)


class NandExpression(BinaryExpression):
    def __repr__(self):
        return super().__repr__().format('NAND')

    def calculate(self, variable_values):
        result = not (self.left.calculate(variable_values)
                      and self.right.calculate(variable_values))
        return int(result)


class ImplyExpression(BinaryExpression):
    def __repr__(self):
        return super().__repr__().format('IMPLY')

    def calculate(self, variable_values):
        result = (not self.left.calculate(variable_values)
                  or self.right.calculate(variable_values))
        return int(result)


class EqExpression(BinaryExpression):
    def __repr__(self):
        return super().__repr__().format('EQ')

    def calculate(self, variable_values):
        left_value = self.left.calculate(variable_values)
        right_value = self.right.calculate(variable_values)
        result = ((not left_value and not right_value)
                  or left_value and right_value)
        return int(result)
