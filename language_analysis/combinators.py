from abc import ABC, abstractmethod


class Result(object):
    def __init__(self, subtree, position):
        self.tree = subtree
        self.position = position

    def __repr__(self):
        return f'Result: {self.tree}, {self.position}'


class Parser(ABC):
    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass

    def __add__(self, other):
        return Concatenate(self, other)

    def __mul__(self, other):
        return Expression(self, other)

    def __or__(self, other):
        return Alternative(self, other)

    def __xor__(self, function):
        return Process(self, function)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.__dict__})'


class Tag(Parser):
    def __init__(self, tag):
        self.tag = tag

    def __call__(self, tokens, position):
        if position < len(tokens) and tokens[position][1] is self.tag:
            return Result(tokens[position][0], position + 1)
        return None


class Reserved(Parser):
    def __init__(self, term, tag):
        self.term = term
        self.tag = tag

    def __call__(self, tokens, position):
        if (position < len(tokens)
                and tokens[position][0] == self.term
                and tokens[position][1] is self.tag):
            return Result(tokens[position][0], position + 1)
        return None


class Concatenate(Parser):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __call__(self, tokens, position):
        left_result = self.left(tokens, position)
        if left_result:
            right_result = self.right(tokens, left_result.position)
            if right_result:
                combined_trees = (left_result.tree, right_result.tree)
                return Result(combined_trees, right_result.position)
        return None


class Expression(Parser):
    def __init__(self, parser, separator_parser):
        self.parser = parser
        self.separator_parser = separator_parser

    def __call__(self, tokens, position):
        result = self.parser(tokens, position)

        def process_next(parsed):
            separate_function, right = parsed
            return separate_function(result.tree, right)

        next_parser = self.separator_parser + self.parser ^ process_next
        next_result = result
        while next_result:
            next_result = next_parser(tokens, result.position)
            if next_result:
                result = next_result
        return result


class Alternative(Parser):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __call__(self, tokens, position):
        left_result = self.left(tokens, position)
        if left_result:
            return left_result
        right_result = self.right(tokens, position)
        return right_result


class Option(Parser):
    def __init__(self, parser):
        self.parser = parser

    def __call__(self, tokens, position):
        result = self.parser(tokens, position)
        if result:
            return result
        return Result(None, position)


class Repeat(Parser):
    def __init__(self, parser):
        self.parser = parser

    def __call__(self, tokens, position):
        results = []
        result = self.parser(tokens, position)
        while result:
            results.append(result.tree)
            position = result.position
            result = self.parser(tokens, position)
        return Result(results, position)


class Process(Parser):
    def __init__(self, parser, function):
        self.parser = parser
        self.function = function

    def __call__(self, tokens, position):
        result = self.parser(tokens, position)
        if result:
            result.tree = self.function(result.tree)
            return result
        return None


class Lazy(Parser):
    def __init__(self, parser_function):
        self.parser = None
        self.parser_function = parser_function

    def __call__(self, tokens, position):
        if not self.parser:
            self.parser = self.parser_function()
        return self.parser(tokens, position)


class Phrase(Parser):
    def __init__(self, parser):
        self.parser = parser

    def __call__(self, tokens, position):
        result = self.parser(tokens, position)
        if result and result.position == len(tokens):
            return result
        return None
