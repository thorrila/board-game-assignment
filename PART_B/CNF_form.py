# get tree structure : placeholder
from logics import SentenceTree

class Sentence:
    """ Starting from the leafs/literals and up the tree, convert each node to CNF. """
    def __init__(self, op, args):
        self.op = op  # "AND", "OR", "NOT", etc.
        self.args = args

    def to_cnf(self):
        # DEBUGGING:
        print(f"Transforming: {self.op}") # print the operations starting from the innermost brackets and moving outward

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
