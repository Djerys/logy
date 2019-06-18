from abc import ABC, abstractmethod


class Expression(ABC):
    @abstractmethod
    def __repr__(self):
        pass

    @property
    @abstractmethod
    def variables(self):
        pass

    @abstractmethod
    def calculate(self, variables):
        pass


class NotExpression(Expression):
    def __init__(self, expression):
        self.expression = expression

    def __repr__(self):
        return f'NOT({self.expression})'

    @property
    def variables(self):
        return self.expression.variables

    def calculate(self, variables):
        return self.expression.calculate(variables)


class ConstantExpression(Expression):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f'{self.value}'

    @property
    def variables(self):
        return set()

    def calculate(self, variables):
        return self.value


class VariableExpression(Expression):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

    @property
    def variables(self):
        return {self.name}

    def calculate(self, variables):
        if self.name not in variables:
            raise ValueError('No such variable value in given variables.')
        return variables[self.name]


class BinaryExpression(Expression):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    @abstractmethod
    def __repr__(self):
        return '{}' + f'({self.left}, {self.right})'

    @property
    def variables(self):
        return self.left.variables | self.right.variables


class AndExpression(BinaryExpression):
    def __repr__(self):
        return super().__repr__().format('AND')

    def calculate(self, variables):
        result = (self.left.calculate(variables)
                  and self.right.calculate(variables))

        return int(result)


class OrExpression(BinaryExpression):
    def __repr__(self):
        return super().__repr__().format('OR')

    def calculate(self, variables):
        result = (self.left.calculate(variables)
                  or self.right.calculate(variables))

        return int(result)


class XorExpression(BinaryExpression):
    def __repr__(self):
        return super().__repr__().format('XOR')

    def calculate(self, variables):
        left_value = self.left.calculate(variables)
        right_value = self.right.calculate(variables)
        result = ((not left_value and right_value)
                  or (left_value and not right_value))

        return int(result)


class NorExpression(BinaryExpression):
    def __repr__(self):
        return super().__repr__().format('NOR')

    def calculate(self, variables):
        result = not (self.left.calculate(variables)
                      or self.right.calculate(variables))

        return int(result)


class NandExpression(BinaryExpression):
    def __repr__(self):
        return super().__repr__().format('NAND')

    def calculate(self, variables):
        result = not (self.left.calculate(variables)
                      and self.right.calculate(variables))

        return int(result)


class ImplyExpression(BinaryExpression):
    def __repr__(self):
        return super().__repr__().format('IMPLY')

    def calculate(self, variables):
        result = (not self.left.calculate(variables)
                  or self.right.calculate(variables))

        return int(result)


class EqExpression(BinaryExpression):
    def __repr__(self):
        return super().__repr__().format('EQ')

    def calculate(self, variables):
        left_value = self.left.calculate(variables)
        right_value = self.right.calculate(variables)
        result = ((not left_value and not right_value)
                  or left_value and right_value)

        return int(result)
