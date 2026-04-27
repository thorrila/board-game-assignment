from BeliefBase import KB, revise
from Tree_AST_CNF import SentenceTree, Sentence

###### Helper functions ######

def equal(kb1, kb2):
    """Two KBs are 'equal' if they entail the same things — 
    we approximate by checking mutual entailment of all formulas.
    Used to test extensionality and vacuity postulates."""
    for entry in kb1.entries:
        # Convert formula to string for entails() — depends on your resolution impl
        if not kb2.entails(entry.formula):
            return False
    for entry in kb2.entries:
        if not kb1.entails(entry.formula):
            return False
    return True


def subset(kb1, kb2):
    """kb1 is a subset of kb2 if everything kb1 entails, kb2 also entails. ⊆. 
    Used to test inclusion postulate."""
    for entry in kb1.entries:
        if not kb2.entails(entry.formula):
            return False
    return True


def is_tautology(phi):
    """phi is a tautology if an empty KB entails it.
    Used to test extensionality."""
    empty_kb = KB()
    return empty_kb.entails(phi)


def iff(phi, psi):
    """phi and psi are iff if (phi <=> psi) is a tautology."""
    iff_formula = Sentence("IFF", [phi, psi])
    return is_tautology(iff_formula)


def negate(phi):
    """Wrap phi in a NOT."""
    return Sentence("NOT", [phi])

###### Contraction postulates - excluding Closure, Conjunctive Inclusion and Conjuctive Overlap ######

# 1
def success_contraction(kb, phi):
    """The outcome does not contain phi (unless phi is a tautology)."""
    if is_tautology(phi):
        return True
    contracted = kb.contraction(phi)
    if not contracted.entails(phi):
        print("success postulate satisfied")
        return True
    else:
        print("success postulate not satisfied")
        return False

# 2
def inclusion_contraction(kb, phi):
    """The contracted KB is a subset of the original KB."""
    contracted = kb.contraction(phi)
    if subset(contracted, kb):
        print("inclusion postulate satisfied")
        return True
    else:
        print("inclusion postulate not satisfied")
        return False

# 3
def vacuity_contraction(kb, phi):
    """If phi is not in the KB, the KB remains unchanged after contracting by phi."""
    if not kb.entails(phi):
        contracted = kb.contraction(phi)
        if equal(contracted, kb):
            print("vacuity postulate satisfied")
            return True
        else:
            print("vacuity postulate not satisfied")
            return False
    # Vacuously true if phi IS entailed
    print("vacuity postulate satisfied (precondition not met)")
    return True

# 4
def extensionality_contraction(kb, phi, psi):
    """Contracting by iff formulas yields equivalent results."""
    if iff(phi, psi):
        contracted_phi = kb.contraction(phi)
        contracted_psi = kb.contraction(psi)
        if equal(contracted_phi, contracted_psi):
            print("extensionality postulate satisfied")
            return True
        else:
            print("extensionality postulate not satisfied")
            return False
    print("extensionality postulate satisfied (precondition not met)")
    return True

# 5
def recovery_contraction(kb, phi):
    """If you contract by phi and then add phi back, you recover the original."""
    contracted = kb.contraction(phi)
    contracted.expand(phi)
    if subset(kb, contracted):
        print("recovery postulate satisfied")
        return True
    else:
        print("recovery postulate not satisfied")
        return False


###### Revision postulates - excluding Closure, Superexpansion and Subexpansion ######

# 1
def success_revision(kb, phi):
    """The result of revising by phi contains phi."""
    revised = revise(kb, phi)
    if revised.entails(phi):
        print("success postulate satisfied")
        return True
    else:
        print("success postulate not satisfied")
        return False

# 2
def inclusion_revision(kb, phi):
    """Revision is a subset of expansion (B * phi <= B + phi)."""
    revised = revise(kb, phi)
    expanded = kb.copy()
    expanded.expand(phi)
    if subset(revised, expanded):
        print("inclusion postulate satisfied")
        return True
    else:
        print("inclusion postulate not satisfied")
        return False

# 3
def vacuity_revision(kb, phi):
    """If NOT phi is not in B, then B * phi == B + phi."""
    not_phi = negate(phi)
    if not kb.entails(not_phi):
        revised = revise(kb, phi)
        expanded = kb.copy()
        expanded.expand(phi)
        if equal(revised, expanded):
            print("vacuity postulate satisfied")
            return True
        else:
            print("vacuity postulate not satisfied")
            return False
    print("vacuity postulate satisfied (precondition not met)")
    return True

# 4
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

# 5
def extensionality_revision(kb, phi, psi):
    """Revising by iff formulas yields equivalent results."""
    if iff(phi, psi):
        revised_phi = revise(kb, phi)
        revised_psi = revise(kb, psi)
        if equal(revised_phi, revised_psi):
            print("extensionality postulate satisfied")
            return True
        else:
            print("extensionality postulate not satisfied")
            return False
    print("extensionality postulate satisfied (precondition not met)")
    return True


###### Test runner ######

if __name__ == "__main__":

    def run_postulates(kb, phi, psi=None):
        """Run all postulates on a single (kb, phi) pair, optionally with psi for extensionality."""
        print("\nKB contents:")
        kb.show()
        
        print("\n--- Contraction ---")
        success_contraction(kb, phi)
        inclusion_contraction(kb, phi)
        vacuity_contraction(kb, phi)
        if psi is not None:
            extensionality_contraction(kb, phi, psi)
        recovery_contraction(kb, phi)
        
        print("\n--- Revision ---")
        success_revision(kb, phi)
        inclusion_revision(kb, phi)
        vacuity_revision(kb, phi)
        consistency_revision(kb, phi)
        if psi is not None:
            extensionality_revision(kb, phi, psi)


    # Test 1: Modus Ponens KB
    print("=" * 60)
    print("TEST 1: Modus Ponens KB, phi = B, psi = B & B")
    print("=" * 60)
    kb1 = KB()
    kb1.add(SentenceTree("A").root, priority=10)
    kb1.add(SentenceTree("A => B").root, priority=1)
    run_postulates(kb1, SentenceTree("B").root, SentenceTree("B & B").root)


    # Test 2: Disjunctive KB - Recovery should fail here
    print("\n" + "=" * 60)
    print("TEST 2: Disjunctive KB, phi = A | C")
    print("(Recovery is expected to fail on this configuration)")
    print("=" * 60)
    kb2 = KB()
    kb2.add(SentenceTree("A").root, priority=1)
    kb2.add(SentenceTree("C").root, priority=1)
    run_postulates(kb2, SentenceTree("A | C").root)


    # Test 3: Empty KB edge case
    print("\n" + "=" * 60)
    print("TEST 3: Empty KB, phi = A")
    print("=" * 60)
    kb3 = KB()
    run_postulates(kb3, SentenceTree("A").root)


    # Test 4: Larger KB with priority gradient
    print("\n" + "=" * 60)
    print("TEST 4: Larger KB with priority gradient, phi = ~Q")
    print("=" * 60)
    kb4 = KB()
    kb4.add(SentenceTree("P").root, priority=10)
    kb4.add(SentenceTree("P => Q").root, priority=5)
    kb4.add(SentenceTree("Q => R").root, priority=3)
    kb4.add(SentenceTree("R => S").root, priority=1)
    run_postulates(kb4, SentenceTree("~Q").root, SentenceTree("~(Q | Q)").root)


    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETE")
    print("=" * 60)