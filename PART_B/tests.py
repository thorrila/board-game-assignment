from BeliefBase import KB, revise
from Tree_AST_CNF import SentenceTree, Sentence
from postulates import *

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

    # Test 2: Empty KB edge case
    print("\n" + "=" * 60)
    print("TEST 2: Empty KB, phi = A")
    print("=" * 60)
    kb2 = KB()
    run_postulates(kb2, SentenceTree("A").root)


    # Test 3: Larger KB with priority gradient
    print("\n" + "=" * 60)
    print("TEST 3: Larger KB with priority gradient, phi = ~Q")
    print("=" * 60)
    kb3 = KB()
    kb3.add(SentenceTree("P").root, priority=10)
    kb3.add(SentenceTree("P => Q").root, priority=5)
    kb3.add(SentenceTree("Q => R").root, priority=3)
    kb3.add(SentenceTree("R => S").root, priority=1)
    run_postulates(kb3, SentenceTree("~Q").root, SentenceTree("~(Q | Q)").root)


        # Test 4: De Morgan
    print("\n" + "=" * 60)
    print("TEST 4: De Morgan extensionality, phi = ~(A & B), psi = ~A | ~B")
    print("(phi and psi are logically equivalent but syntactically different)")
    print("=" * 60)
    kb4 = KB()
    kb4.add(SentenceTree("A").root, priority=5)
    kb4.add(SentenceTree("B").root, priority=5)
    run_postulates(kb4, SentenceTree("~(A & B)").root, SentenceTree("~A | ~B").root)


    # Test 5: Material implication extensionality
    print("\n" + "=" * 60)
    print("TEST 5: Material implication extensionality, phi = A => B, psi = ~A | B")
    print("=" * 60)
    kb5 = KB()
    kb5.add(SentenceTree("A").root, priority=5)
    kb5.add(SentenceTree("A => B").root, priority=3)
    run_postulates(kb5, SentenceTree("A => B").root, SentenceTree("~A | B").root)


    # Test 6: Revision by a formula that conflicts with low-priority belief
    print("\n" + "=" * 60)
    print("TEST 6: Priority gradient revision, phi = ~B")
    print("(High-priority A should survive, low-priority B should be displaced)")
    print("=" * 60)
    kb6 = KB()
    kb6.add(SentenceTree("A").root, priority=10)
    kb6.add(SentenceTree("B").root, priority=1)
    run_postulates(kb6, SentenceTree("~B").root)


    # Test 7: Disjunctive input where neither disjunct is in KB
    print("\n" + "=" * 60)
    print("TEST 7: Disjunctive input, phi = A | B")
    print("(KB contains ~A and ~B, so revising by A | B forces a real change)")
    print("=" * 60)
    kb7 = KB()
    kb7.add(SentenceTree("~A").root, priority=3)
    kb7.add(SentenceTree("~B").root, priority=3)
    run_postulates(kb7, SentenceTree("A | B").root)


    # Test 8: Conjunctive contraction with an unrelated belief
    print("\n" + "=" * 60)
    print("TEST 8: Conjunctive contraction, phi = A & B")
    print("(Unrelated belief C should survive contraction)")
    print("=" * 60)
    kb8 = KB()
    kb8.add(SentenceTree("A").root, priority=5)
    kb8.add(SentenceTree("B").root, priority=5)
    kb8.add(SentenceTree("C").root, priority=5)
    run_postulates(kb8, SentenceTree("A & B").root, SentenceTree("B & A").root)


    print("\nTesting complete :-)")