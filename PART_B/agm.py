from BeliefBase import KB, revise
from Tree_AST_CNF import SentenceTree, Sentence

###### Helper functions ######

def kb_from_formulas(formulas, priority=1):
    """Build a KB from a list of formula strings or ASTs."""
    kb = KB()
    for f in formulas:
        if isinstance(f, str):
            f = SentenceTree(f).root
        kb.add(f, priority)
    return kb


def kb_equals(kb1, kb2):
    """Two KBs are 'equal' if they entail the same things — 
    we approximate by checking mutual entailment of all formulas."""
    for entry in kb1.entries:
        # Convert formula to string for entails() — depends on your resolution impl
        if not kb2.entails(entry.formula):
            return False
    for entry in kb2.entries:
        if not kb1.entails(entry.formula):
            return False
    return True


def kb_subset(kb1, kb2):
    """kb1 is a subset of kb2 if everything kb1 entails, kb2 also entails."""
    for entry in kb1.entries:
        if not kb2.entails(entry.formula):
            return False
    return True


def is_tautology(phi):
    """phi is a tautology if an empty KB entails it."""
    empty_kb = KB()
    return empty_kb.entails(phi)


def equivalent(phi, psi):
    """phi and psi are equivalent if (phi <=> psi) is a tautology."""
    iff_formula = Sentence("IFF", [phi, psi])
    return is_tautology(iff_formula)


def negate(phi):
    """Wrap phi in a NOT."""
    return Sentence("NOT", [phi])


def conjoin(phi, psi):
    """Build phi AND psi."""
    return Sentence("AND", [phi, psi])

###### Contraction postulates ######

def success_contraction(kb, phi):
    """The outcome does not contain phi (unless phi is a tautology)."""
    if is_tautology(phi):
        # Tautologies can't be removed
        return True
    contracted = kb.contraction(phi)
    if not contracted.entails(phi):
        print("success postulate satisfied")
        return True
    else:
        print("success postulate not satisfied")
        return False


def inclusion_contraction(kb, phi):
    """The contracted KB is a subset of the original KB."""
    contracted = kb.contraction(phi)
    if kb_subset(contracted, kb):
        print("inclusion postulate satisfied")
        return True
    else:
        print("inclusion postulate not satisfied")
        return False


def vacuity_contraction(kb, phi):
    """If phi is not in the KB, the KB remains unchanged after contracting by phi."""
    if not kb.entails(phi):
        contracted = kb.contraction(phi)
        if kb_equals(contracted, kb):
            print("vacuity postulate satisfied")
            return True
        else:
            print("vacuity postulate not satisfied")
            return False
    # Vacuously true if phi IS entailed
    print("vacuity postulate satisfied (precondition not met)")
    return True


def extensionality_contraction(kb, phi, psi):
    """Contracting by equivalent formulas yields equivalent results."""
    if equivalent(phi, psi):
        contracted_phi = kb.contraction(phi)
        contracted_psi = kb.contraction(psi)
        if kb_equals(contracted_phi, contracted_psi):
            print("extensionality postulate satisfied")
            return True
        else:
            print("extensionality postulate not satisfied")
            return False
    print("extensionality postulate satisfied (precondition not met)")
    return True


def recovery_contraction(kb, phi):
    """If you contract by phi and then add phi back, you recover the original."""
    contracted = kb.contraction(phi)
    contracted.expand(phi)
    if kb_subset(kb, contracted):
        print("recovery postulate satisfied")
        return True
    else:
        print("recovery postulate not satisfied")
        return False



###### Revision postulates ######


def success_revision(kb, phi):
    """The result of revising by phi contains phi."""
    revised = revise(kb, phi)
    if revised.entails(phi):
        print("success postulate satisfied")
        return True
    else:
        print("success postulate not satisfied")
        return False


def inclusion_revision(kb, phi):
    """Revision is a subset of expansion (B * phi <= B + phi)."""
    revised = revise(kb, phi)
    expanded = kb.copy()
    expanded.expand(phi)
    if kb_subset(revised, expanded):
        print("inclusion postulate satisfied")
        return True
    else:
        print("inclusion postulate not satisfied")
        return False


def vacuity_revision(kb, phi):
    """If NOT phi is not in B, then B * phi == B + phi."""
    not_phi = negate(phi)
    if not kb.entails(not_phi):
        revised = revise(kb, phi)
        expanded = kb.copy()
        expanded.expand(phi)
        if kb_equals(revised, expanded):
            print("vacuity postulate satisfied")
            return True
        else:
            print("vacuity postulate not satisfied")
            return False
    print("vacuity postulate satisfied (precondition not met)")
    return True


def consistency_revision(kb, phi):
    """B * phi is consistent if phi is consistent (i.e., not a contradiction)."""
    # phi is consistent iff NOT(phi) is not a tautology
    if is_tautology(negate(phi)):
        # phi itself is a contradiction — no consistency required
        print("consistency postulate satisfied (precondition not met)")
        return True
    
    revised = revise(kb, phi)
    if revised.is_consistent():
        print("consistency postulate satisfied")
        return True
    else:
        print("consistency postulate not satisfied")
        return False


def extensionality_revision(kb, phi, psi):
    """Revising by equivalent formulas yields equivalent results."""
    if equivalent(phi, psi):
        revised_phi = revise(kb, phi)
        revised_psi = revise(kb, psi)
        if kb_equals(revised_phi, revised_psi):
            print("extensionality postulate satisfied")
            return True
        else:
            print("extensionality postulate not satisfied")
            return False
    print("extensionality postulate satisfied (precondition not met)")
    return True


###### Test runner ######

if __name__ == "__main__":
    kb = KB()
    kb.add(SentenceTree("A").root, priority=10)
    kb.add(SentenceTree("A => B").root, priority=1)

    print("Testing contraction postulates with phi = B:")
    success_contraction(kb, SentenceTree("B").root)
    inclusion_contraction(kb, SentenceTree("B").root)
    vacuity_contraction(kb, SentenceTree("C").root)
    recovery_contraction(kb, SentenceTree("B").root)

    print("\nTesting revision postulates with phi = ~B:")
    success_revision(kb, SentenceTree("~B").root)
    inclusion_revision(kb, SentenceTree("~B").root)
    consistency_revision(kb, SentenceTree("~B").root)

    