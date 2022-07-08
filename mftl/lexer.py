# type: ignore

STATES = {
    'Init': (
        # charset  next    action  token
        ('0', '9', 'Int',  'Keep', None),
        ('a', 'z', 'Word', 'Keep', None),
        ('A', 'Z', 'Word', 'Keep', None),
        (' ', ' ', 'Init', 'Ignore', None),
        (None, None, 'Init', 'Keep', 'Special')
    ),
    'Int': (
        ('0', '9', 'Int', 'Keep', None),
        (None, None, 'Init', 'Reuse', 'Int')
    ),
    'Word': (
        ('a', 'z', 'Word', 'Keep', None),
        ('A', 'Z', 'Word', 'Keep', None),
        (None, None, 'Init', 'Reuse', 'Word')
    )
}

def findTransition(c, stateName):
    rules = STATES[stateName]
    for rule in rules:
        (c1, c2, _, _, _) = rule
        if c1 is None or (c >= c1 and c <= c2):
            return rule
    raise Exception("rule not found", c, stateName)

RESERVED = {'fun', 'if', 'let', 'then', 'else'}

def checkWord(word):
    if word in RESERVED:
        return ('Reserved', word)
    if word == 'true':
        return ('Bool', True)
    if word == 'false':
        return ('Bool', False)
    return ('Ident', word)

def lex(string):
    stringIndex = 0
    stateName = 'Init'
    tokenString = ''
    tokens = []
    rule = ()
    EOI = '\0'
    string += EOI  # forces completion of any incomplete token
    while True:
        c = string[stringIndex]
        stringIndex += 1
        rule = findTransition(c, stateName)
        print(c, stateName, rule, tokenString)
        (c1, c2, stateName, action, tokenType) = rule
        # check the action
        if action == 'Keep':
            tokenString += c
        elif action == 'Reuse':
            stringIndex -= 1
        elif action == 'Ignore':
            pass
        # check the token type
        if tokenType is not None:
            if tokenType == 'Int':
                tokenValue = int(tokenString)
            elif tokenType == 'Word':
                (tokenType, tokenValue) = checkWord(tokenString)
            else:
                tokenValue = tokenString
            token = (tokenType, tokenValue)
            tokenString = ''
            tokens.append(token)
        if c == EOI:
            break
    # append EOI token
    tokens.append(('EOI', None))
    return tokens

if __name__ == '__main__':
    tokens = lex("let a = 1, b = true")
    print(tokens)

