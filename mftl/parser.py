# type: ignore

class Spot:
    def __init__(self, type, value=None) -> None:
        self.type: str = type
        self.value = value

    def __call__(self, tokens):
        #print("Spot", self.type, self.value, tokens)
        token = tokens[0]
        if token[0] == self.type:
            if self.value is not None:
                if token[1] == self.value:
                    return (tokens[0], tokens[1:])
                return None
            return (tokens[0], tokens[1:])
        return None

class Reserved (Spot):
    def __init__(self, word) -> None:
        super().__init__('Reserved', word)

class Strip:
    def __init__(self, parser) -> None:
        self.parser = parser
    def __call__(self, tokens):
        res = self.parser(tokens)
        if res is not None:
            ((_, value), tokens) = res
            res = (value, tokens)
        return res

class Generic:
    def __init__(self, parser) -> None:
        self.parser = parser
    def __call__(self, tokens):
        return self.parser(tokens)

class Literal (Generic):
    def __init__(self, type) -> None:
        super().__init__(Strip(Spot(type)))

class Int (Literal):
    def __init__(self) -> None:
        super().__init__('Int')

class Bool (Literal):
    def __init__(self) -> None:
        super().__init__('Bool')

class OneOf:
    def __init__(self, parsers) -> None:
        self.parsers = parsers
    def __call__(self, tokens):
        for parser in self.parsers:
            res = parser(tokens)
            if res is not None:
                return res
        return None

class Ignore:
    def __init__(self, parser) -> None:
        self.parser = parser
    def __call__(self, tokens):
        if self.parser(tokens) is not None:
            return ('__IGNORE__', tokens[1:])
        return None

class Seq:
    def __init__(self, parsers) -> None:
        self.parsers = parsers
    def __call__(self, tokens):
        results = []
        for parser in self.parsers:
            resTup = parser(tokens)
            if resTup is None:
                return None
            (res, tokens) = resTup
            if res != '__IGNORE__':
                results.append(res)
        return (results, tokens)

class If:
    def __init__(self) -> None:
        self.parser = Seq([Ignore(Reserved('if')),
                           Bool(),
                           Ignore(Reserved('then')),
                           Int(),
                           Ignore(Reserved('else')),
                           Int()])
    def __call__(self, tokens):
        res = self.parser(tokens)
        if res is not None:
            ([cond, conseq, alt], tokens) = res
            res = (('If', cond, conseq, alt), tokens)
        return res

def parse(tokens):
    parser = If()
    return parser(tokens)

if __name__ == '__main__':
    tokens = [('Reserved', 'if'), ('Bool', True), ('Reserved', 'then'), ('Int', 100), ('Reserved', 'else'), ('Int', 200), ('EOI', None)]
    if1 = If()
    res = if1(tokens)
    print("if =", res)
