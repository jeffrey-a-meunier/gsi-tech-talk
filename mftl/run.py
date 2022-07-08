# type: ignore

import lexer
import parser
import eval

def run() -> None:
    string = "if false then 100 else 200"
    tokens = lexer.lex(string)
    print("tokens =", tokens)
    (expr, rest) = parser.parse(tokens)
    print("expr =", expr)
    res = eval.evaluate(expr)
    print("res =", res)

if __name__ == '__main__':
    run()
