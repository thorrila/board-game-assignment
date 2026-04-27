from dataclasses import dataclass
from Tree_AST_CNF import *


@dataclass
class BeliefEntry:
    formula: object # as a SentenceTree().root
    priority: int


class KB:
    def __init__(self):
        self.entries = []

    def formulas(self):
        """ output: list of formulas """
        return [entry.formula for entry in self.entries]

    def add(self, formula, priority=1):
        """ modifies the KB """
        self.entries.append(BeliefEntry(formula, priority))

    def expand(self, formula, priority=1):
        """ Modifies the KB """
        self.add(formula, priority)

    def entails(self, phi):
        ''' in: string, out: true/false) '''
        return resolution(self.formulas(), phi)

    def copy(self):
        '''out: the new KB'''
        new_base = KB()
        for entry in self.entries:
            new_base.add(entry.formula, entry.priority)
        return new_base

    def contraction(self, phi):
        ''' in: string, out: new KB '''
        if not self.entails(phi):
            return self.copy()

        new_base = self.copy()
        removed_indicator = True

        while new_base.entails(phi) and removed_indicator:
            removed_indicator = False

            indexed_entries = list(enumerate(new_base.entries))
            indexed_entries.sort(key=lambda x: x[1].priority)

            for idx, entry in indexed_entries:
                trial = new_base.copy()
                del trial.entries[idx]

                if not trial.entails(phi):
                    return trial

            if indexed_entries:
                weakest_idx, weakest_entry = indexed_entries[0]
                del new_base.entries[weakest_idx]
                removed_indicator = True

        return new_base

    def is_consistent(self):
        ''' out: true/false '''
        # A KB is inconsistent iff it entails an arbitrary fresh symbol.
        return not self.entails("__contradiction__")

    def show(self):
        if not self.entries:
            print("{}")
            return

        print("{")
        for entry in self.entries:
            print(f"  {formula_to_string(entry.formula)}   [priority={entry.priority}]")
        print("}")


def revise(base, formula, priority=1):
    ''' in: KB, string, int, out: new KB '''
    # Levi identity: B * phi = (B ÷ not phi) + phi
    not_formula = Sentence("NOT", [formula])
    contracted_base = base.contraction(not_formula)
    contracted_base.expand(formula, priority)
    return contracted_base


def cnf_to_clauses(formula):
    ''' in: AST or string, out: list of clauses '''
    if isinstance(formula, str):
        return [{formula}]

    return formula.get_clauses()


def complementary(l1, l2):
    ''' in: literals, out: true/false '''
    return (
        l1 == f"NOT({l2})" or
        l2 == f"NOT({l1})"
    )


def resolve(c1, c2):
    ''' in: list of clauses, out: new list of clauses '''
    resolvents = []

    for l1 in c1:
        for l2 in c2:
            if complementary(l1, l2):
                new_clause = (c1 - {l1}) | (c2 - {l2})

                if new_clause not in resolvents:
                    resolvents.append(new_clause)

    return resolvents


def resolution(belief_base_formulas, query):
    ''' list of formulas(KB), formula (Phi), out: true/false '''
    clauses = []

    for formula in belief_base_formulas:
        clauses.extend(cnf_to_clauses(formula))

    negated_query = Sentence("NOT", [query])
    clauses.extend(cnf_to_clauses(negated_query))

    clauses = {frozenset(c) for c in clauses}

    while True:
        new = set()
        clause_list = list(clauses)

        for i in range(len(clause_list)):
            for j in range(i + 1, len(clause_list)):
                resolvents = resolve(set(clause_list[i]), set(clause_list[j]))

                for resolvent in resolvents:
                    frozen = frozenset(resolvent)

                    if len(frozen) == 0:
                        return True

                    if frozen not in clauses:
                        new.add(frozen)

        if not new:
            return False

        clauses |= new

def formula_to_string(formula):
    """ Good for printing and testing later """
    if isinstance(formula, str):
        return formula

    if formula.op == "NOT":
        return f"~{formula_to_string(formula.args[0])}"

    if formula.op == "AND":
        return f"({formula_to_string(formula.args[0])} & {formula_to_string(formula.args[1])})"

    if formula.op == "OR":
        return f"({formula_to_string(formula.args[0])} | {formula_to_string(formula.args[1])})"

    if formula.op == "IF":
        return f"({formula_to_string(formula.args[0])} => {formula_to_string(formula.args[1])})"

    if formula.op == "IFF":
        return f"({formula_to_string(formula.args[0])} <=> {formula_to_string(formula.args[1])})"

    return str(formula)


if __name__ == "__main__":
    kb = KB()

    kb.add(SentenceTree("A").root, priority=10)
    kb.add(SentenceTree("A => B").root, priority=1)

    print("Original KB:")
    kb.show()

    print("\nDoes KB entail B?")
    print(kb.entails("B"))

    contracted = kb.contraction("B")

    print("\nAfter contracting by B:")
    contracted.show()

    print("\nDoes contracted KB entail B?")
    print(contracted.entails("B"))

    revised = revise(kb, SentenceTree("~B").root, priority=5)

    print("\nAfter revising by ~B:")
    revised.show()
