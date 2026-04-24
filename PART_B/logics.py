
def tokenize(s):
    tokens = []
    i = 0

    while i < len(s):
        if s[i].isspace():
            i += 1
            continue

        if s[i].isalpha(): # if it's a variable
            tokens.append(s[i])
            i += 1

        elif s[i] == '<' and s[i:i+3] == '<=>': # if it's a biimplication
            tokens.append('<=>')
            i += 3

        elif s[i] == '=' and s[i+1] == '>': # if it's an implication
            tokens.append('=>')
            i += 2

        elif s[i] in ('&', '|', '~', '(', ')'): # if it's an operator or parenthesis
            tokens.append(s[i])
            i += 1

        else: # if it's an invalid character
            raise ValueError(f"Invalid character: {s[i]}")

    return tokens


def parse(tokens):
    values = [] # value stack
    ops = [] # operator stack

    # operator heirarchy: NOT > AND > OR > IF > IFF
    OPS = {
    '~': (NOT, 3), # highest precedence 
    '&': (AND, 2), 
    '|': (OR, 1),
    '=>': (IF, 0),
    '<=>': (IFF, -1) # lowest precedence
    }

    def apply_op():
        op = ops.pop()
        cls, _ = OPS[op] # get the class and precedence for the operator

        if op == '~':             # unary
            a = values.pop()
            values.append(cls(a))
        else:                     # binary
            b = values.pop()
            a = values.pop()
            values.append(cls(a, b))

    i = 0
    while i < len(tokens):
        t = tokens[i]

        if t.isalpha():
            values.append(t) 

        elif t in OPS:
            # pop operators from the stack while they have higher or equal precedence than the current operator
            while (
                ops and ops[-1] in OPS and
                OPS[ops[-1]][1] >= OPS[t][1]
            ):
                apply_op()
            ops.append(t)

        elif t == '(': 
            ops.append(t)

        elif t == ')': 
            # pop operators from the stack until we find a left parenthesis
            while ops[-1] != '(':
                apply_op()
            ops.pop()

        i += 1

    while ops:
        apply_op()

    return values[0]


class SentenceTree:
    def __init__(self, string):
        self.string = string
        self.root = parse(tokenize(string))

class AND:
    def __init__(self, *args):
        self.args = args
        self.op = "AND"

class OR:
    def __init__(self, *args):
        self.args = args
        self.op = "OR"

class NOT:
    def __init__(self, *args):
        self.args = args
        self.op = "NOT"

class IF:
    def __init__(self, *args):
        self.args = args
        self.op = "IF"

class IFF:
    def __init__(self, *args):
        self.args = args
        self.op = "IFF"


if __name__ == "__main__":
    s1 = "A & B => C"
    tree = SentenceTree(s1)
    print(s1)
    print(tree.root.op)  # IF
    print(tree.root.args[0].op)  # AND
    print(tree.root.args[0].args)  # ['A', 'B']
    print(tree.root.args[1], "\n")  # 'C'

    s2 = "(A | B) & ~C"
    tree2 = SentenceTree(s2)
    print(s2)
    print(tree2.root.op)  # AND
    print(tree2.root.args[0].op)  # OR
    print(tree2.root.args[0].args)  # ['A', 'B']
    print(tree2.root.args[1].op)  # NOT
    print(tree2.root.args[1].args, "\n")  # ['C']


    s3 = "A | B | C & D"
    tree3 = SentenceTree(s3)
    print(s3)
    print(tree3.root.op)  # OR  
    print(tree3.root.args[0].op)  # OR
    print(tree3.root.args[0].args)  # ['A', 'B']
    print(tree3.root.args[1].op)  # AND
    print(tree3.root.args[1].args, "\n")  # ['C', 'D']


