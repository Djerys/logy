from abc import ABC, abstractmethod

import boolean_lexer as blex


class Expression(ABC):
    def __init__(self):
        self.parent = None

    @abstractmethod
    def __repr__(self):
        pass

    @abstractmethod
    def __str__(self):
        pass

    def __and__(self, other):
        return AndExpression(self, other)

    def __or__(self, other):
        return OrExpression(self, other)

    def __xor__(self, other):
        return XorExpression(self, other)

    def __invert__(self):
        return NotExpression(self)

    @property
    @abstractmethod
    def variables(self):
        pass

    @abstractmethod
    def calculate(self, variable_values):
        pass


class ConstantExpression(Expression):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def __repr__(self):
        return f'{self.value}'

    def __str__(self):
        return self.__repr__()

    @property
    def variables(self):
        return set()

    def calculate(self, variable_values):
        return self.value


class VariableExpression(Expression):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.__repr__()

    @property
    def variables(self):
        return {self.name}

    def calculate(self, variable_values):
        if self.name not in variable_values:
            raise ValueError('No such variable value in given variables.')
        return variable_values[self.name]


class OperationExpression(Expression):
    @property
    @abstractmethod
    def precedence_level(self):
        pass


class NotExpression(OperationExpression):
    def __init__(self, expression):
        super().__init__()
        self.expression = expression
        self.expression.parent = self

    def __repr__(self):
        return f'NOT({self.expression})'

    def __str__(self):
        return f'{blex.NOT}{self.expression}'

    @property
    def precedence_level(self):
        return 4

    @property
    def variables(self):
        return self.expression.variables

    def calculate(self, variable_values):
        result = not self.expression.calculate(variable_values)
        return int(result)


class BinaryExpression(OperationExpression):
    def __init__(self, left, right):
        super().__init__()
        self.left = left
        self.left.parent = self
        self.right = right
        self.right.parent = self

    def __repr__(self):
        return '{}' + f'({self.left}, {self.right})'

    def __str__(self):
        view = f'{self.left}' + ' {} ' + f'{self.right}'
        if (self.parent is not None
                and self.parent.precedence_level > self.precedence_level):
            view = f'({view})'
        return view

    @property
    def variables(self):
        return self.left.variables | self.right.variables


class AndExpression(BinaryExpression):
    def __repr__(self):
        return super().__repr__().format('AND')

    def __str__(self):
        return super().__str__().format(blex.AND)

    @property
    def precedence_level(self):
        return 3

    def calculate(self, variable_values):
        result = (self.left.calculate(variable_values)
                  and self.right.calculate(variable_values))
        return int(result)


class OrExpression(BinaryExpression):
    def __repr__(self):
        return super().__repr__().format('OR')

    def __str__(self):
        return super().__str__().format(blex.OR)

    @property
    def precedence_level(self):
        return 2

    def calculate(self, variable_values):
        result = (self.left.calculate(variable_values)
                  or self.right.calculate(variable_values))
        return int(result)


class XorExpression(BinaryExpression):
    def __repr__(self):
        return super().__repr__().format('XOR')

    def __str__(self):
        return super().__str__().format(blex.XOR)

    @property
    def precedence_level(self):
        return 1

    def calculate(self, variable_values):
        left_value = self.left.calculate(variable_values)
        right_value = self.right.calculate(variable_values)
        result = ((not left_value and right_value)
                  or (left_value and not right_value))
        return int(result)


class NorExpression(BinaryExpression):
    def __repr__(self):
        return super().__repr__().format('NOR')

    def __str__(self):
        return super().__str__().format(blex.NOR)

    @property
    def precedence_level(self):
        return 2

    def calculate(self, variable_values):
        result = not (self.left.calculate(variable_values)
                      or self.right.calculate(variable_values))
        return int(result)


class NandExpression(BinaryExpression):
    def __repr__(self):
        return super().__repr__().format('NAND')

    def __str__(self):
        return super().__str__().format(blex.NAND)

    @property
    def precedence_level(self):
        return 3

    def calculate(self, variable_values):
        result = not (self.left.calculate(variable_values)
                      and self.right.calculate(variable_values))
        return int(result)


class ImplyExpression(BinaryExpression):
    def __repr__(self):
        return super().__repr__().format('IMPLY')

    def __str__(self):
        return super().__str__().format(blex.IMPLY)

    @property
    def precedence_level(self):
        return 1

    def calculate(self, variable_values):
        result = (not self.left.calculate(variable_values)
                  or self.right.calculate(variable_values))
        return int(result)


class EqExpression(BinaryExpression):
    def __repr__(self):
        return super().__repr__().format('EQ')

    def __str__(self):
        return super().__str__().format(blex.EQ)

    @property
    def precedence_level(self):
        return 1

    def calculate(self, variable_values):
        left_value = self.left.calculate(variable_values)
        right_value = self.right.calculate(variable_values)
        result = ((not left_value and not right_value)
                  or left_value and right_value)
        return int(result)
