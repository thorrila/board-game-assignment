
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
    """ Tree Construction (Abstract Syntax Tree (AST))"""
    values = [] # value stack
    ops = [] # operator stack

    # operator heirarchy: NOT > AND > OR > IF > IFF
    OPS = {
        '~': (Sentence, 'NOT', 3), 
        '&': (Sentence, 'AND', 2), 
        '|': (Sentence, 'OR', 1),
        '=>': (Sentence, 'IF', 0),
        '<=>': (Sentence, 'IFF', -1)
    }

    def apply_op():
        op_symbol = ops.pop()
        cls, op_name, _ = OPS[op_symbol]

        if op_symbol == '~':
            a = values.pop()
            values.append(cls(op_name, [a])) # creates Sentence("NOT", [a])
        else:
            b = values.pop()
            a = values.pop()
            values.append(cls(op_name, [a, b])) # creates Sentence("AND", [a, b])

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


class Sentence:
    """ Starting from the leafs/literals and up the tree, convert each node to CNF. """
    def __init__(self, op, args):
        self.op = op  # "AND", "OR", "NOT", etc.
        self.args = args

    def to_cnf(self):
        # DEBUGGING:
        #print(f"Transforming: {self.op}") # print the operations starting from the innermost brackets and moving outward

        # We ensure every branch below us is already simplified.
        processed_args = []
        for arg in self.args:
            if isinstance(arg, Sentence):
                # Recursive call: fix the child before fixing the parent
                new_child = arg.to_cnf()
                processed_args.append(new_child)
            else:
                processed_args.append(arg) # Literal, no CNF needed

        # Create a new version of ourselves with the processed children
        current = Sentence(self.op, processed_args)

        # ELIMINATE IFF
        if current.op == "IFF":
            return current._handle_iff()

        # ELIMINATE IF
        if current.op == "IF":
            return current._handle_if()

        # Move NOT inwards (De Morgan's)
        if current.op == "NOT":
            return current._handle_not()

        # Distribute OR over AND
        if current.op == "OR":
            return current._handle_or()

        # If it's an AND or a literal, we just return the current state
        return current
    
    def get_clauses(self):
        """
        Converts the CNF tree into a list of CLAUSES (sets)
        Example: AND(OR(A, B), NOT(C)) -> [{'A', 'B'}, {'NOT(C)'}]
        """
        # Ensure the tree is in CNF
        cnf_tree = self.to_cnf()
        
        # Handle the different possible root operators of a CNF tree
        if cnf_tree.op == "AND":
            # The children of an AND are clauses (either OR nodes or Literals)
            clauses = []
            for arg in cnf_tree.args:
                clauses.append(self._extract_literals(arg))
            return clauses
        else:
            # If the root isn't AND, the whole tree is just one single clause
            return [self._extract_literals(cnf_tree)]

    def _extract_literals(self, node):
        """Helper to collect literals from an OR node or a single Literal."""
        # set() to avoid duplicates or ordering issues
        literals = set()
        
        if isinstance(node, str):
            literals.add(node) # Node is already a literal 'A'
        elif node.op == "NOT":
            # Is also a literal 'NOT(A)'
            literals.add(f"NOT({node.args[0]})")
        elif node.op == "OR":
            # Recursive case: collect from both sides of the OR
            for arg in node.args:
                literals.update(self._extract_literals(arg))
        
        return literals

    def _handle_iff(self):
        # IFF(A, B) becomes AND(IF(A, B), IF(B, A))
        left_arg = self.args[0]
        right_arg = self.args[1]
        
        new_left = Sentence("IF", [left_arg, right_arg])
        new_right = Sentence("IF", [right_arg, left_arg])
        
        combined = Sentence("AND", [new_left, new_right])

        return combined.to_cnf() # turn the new 'IF' nodes into 'OR' nodes

    def _handle_if(self):
        # IF(A, B) becomes OR(NOT(A), B)
        left_arg = self.args[0]
        right_arg = self.args[1]
        
        negated_left = Sentence("NOT", [left_arg])
        combined = Sentence("OR", [negated_left, right_arg])
        
        return combined.to_cnf() # turn the new 'NOT' node into a CNF form if necessary
    
    def _handle_not(self):
        child = self.args[0]
        
        # If NOT(literal), it's already in CNF
        if not isinstance(child, Sentence):
            return self

        # NOT(NOT(A)) -> A (Double Negation)
        if child.op == "NOT":
            grandchild = child.args[0]
            if isinstance(grandchild, Sentence):
                return grandchild.to_cnf()
            return grandchild

        # NOT(AND(A, B)) -> OR(NOT(A), NOT(B)) (De Morgan)
        if child.op == "AND":
            new_args = []
            for a in child.args:
                new_args.append(Sentence("NOT", [a]).to_cnf())
            return Sentence("OR", new_args).to_cnf()

        # NOT(OR(A, B)) -> AND(NOT(A), NOT(B)) (De Morgan)
        if child.op == "OR":
            new_args = []
            for a in child.args:
                new_args.append(Sentence("NOT", [a]).to_cnf())
            return Sentence("AND", new_args).to_cnf()
            
        return self
    
    def _handle_or(self):
        # We need to check if we are ORing an AND: OR(A, AND(B, C))
        left = self.args[0]
        right = self.args[1]

        # Case 1: OR(AND(B, C), A)
        if isinstance(left, Sentence) and left.op == "AND":
            distributed_args = []
            for arg in left.args:
                new_or = Sentence("OR", [arg, right])
                distributed_args.append(new_or.to_cnf())
            return Sentence("AND", distributed_args)

        # Case 2: OR(A, AND(B, C))
        if isinstance(right, Sentence) and right.op == "AND":
            distributed_args = []
            for arg in right.args:
                new_or = Sentence("OR", [left, arg])
                distributed_args.append(new_or.to_cnf())
            return Sentence("AND", distributed_args)

        return self
    



class SentenceTree:
    def __init__(self, string):
        self.string = string
        self.root = parse(tokenize(string))

"""
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
"""
"""
if __name__ == "__main__":
    # Test a complex case: ~(A => (B | C))
    complex_s = "~(A => (B | C))"
    tree = SentenceTree(complex_s)
    
    print(f"Input: {complex_s}")
    cnf_result = tree.root.to_cnf()
    
    # This should output: AND(A, AND(NOT(B), NOT(C))) 
    # (after De Morgan's and Double Negation)
    print(f"Final CNF: {cnf_result}")
"""