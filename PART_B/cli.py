"""
Commands:
  add <formula> [priority]   add a belief (default priority = 1)
  expand <formula> [pri]     same as add (AGM expansion: B + phi)
  contract <formula>         AGM contraction: B / phi
  revise <formula> [pri]     AGM revision via Levi identity
  entails <formula>          ask whether KB entails phi
  consistent                 check if KB is consistent
  show                       print the current KB
  clear                      empty the KB
  postulates <phi> [| psi]   run all AGM postulate checks on current KB
  example                    load a small demo KB
  help                       show this help
  quit / exit                leave

Formula syntax:  variables are single letters; operators are
  ~  (not),  &  (and),  |  (or),  =>  (implies),  <=>  (iff)
Examples:  A,  ~A,  A => B,  (A | B) & ~C,  A <=> B
"""

from BeliefBase import KB, revise
from Tree_AST_CNF import SentenceTree
from postulates import (
    success_contraction, inclusion_contraction, vacuity_contraction, recovery_contraction,
    extensionality_contraction, success_revision, inclusion_revision, vacuity_revision,
    consistency_revision, extensionality_revision,
)


HELP = __doc__


def parse_formula(text):
    """Parse a string into a SentenceTree root, or return None and print the error."""
    text = text.strip()
    if not text:
        print("  ! empty formula")
        return None
    try:
        return SentenceTree(text).root
    except (ValueError, IndexError) as e:
        print(f"  ! could not parse '{text}': {e}")
        return None


def split_formula_and_priority(rest):
    """
    Split the tail of a command into (formula_str, priority).
    Priority is the last whitespace-separated token IF it's an integer,
    otherwise priority defaults to 1 and the whole tail is the formula.
    This is friendlier than requiring a separator.
    """
    rest = rest.strip()
    if not rest:
        return "", 1
    parts = rest.rsplit(None, 1)
    if len(parts) == 2:
        try:
            return parts[0], int(parts[1])
        except ValueError:
            pass
    return rest, 1


def cmd_add(kb, rest):
    formula_str, pri = split_formula_and_priority(rest)
    f = parse_formula(formula_str)
    if f is None:
        return
    kb.add(f, priority=pri)
    print(f"  + added (priority={pri})")


def cmd_contract(kb, rest):
    f = parse_formula(rest)
    if f is None:
        return
    new_kb = kb.contraction(f)
    kb.entries = new_kb.entries  # mutate in place so the user keeps working with the same KB
    print("  - contracted. KB is now:")
    kb.show()


def cmd_revise(kb, rest):
    formula_str, pri = split_formula_and_priority(rest)
    f = parse_formula(formula_str)
    if f is None:
        return
    new_kb = revise(kb, f, priority=pri)
    kb.entries = new_kb.entries
    print(f"  * revised (priority={pri}). KB is now:")
    kb.show()


def cmd_entails(kb, rest):
    f = parse_formula(rest)
    if f is None:
        return
    result = kb.entails(f)
    print(f"  => {'YES' if result else 'no'}, KB {'entails' if result else 'does not entail'} {rest.strip()}")


def cmd_consistent(kb):
    print(f"  => {'consistent' if kb.is_consistent() else 'INCONSISTENT'}")


def cmd_postulates(kb, rest):
    """
    Usage:  postulates <phi>
            postulates <phi> | <psi>
    The optional psi enables the extensionality checks.
    """
    if "|" in rest and rest.count("|") == 1 and "||" not in rest:
        # Heuristic: a single bare '|' separates phi and psi.
        # If the user actually wants a disjunction inside phi, they should wrap it.
        phi_str, psi_str = [s.strip() for s in rest.split("|", 1)]
    else:
        phi_str, psi_str = rest.strip(), None

    phi = parse_formula(phi_str)
    if phi is None:
        return
    psi = parse_formula(psi_str) if psi_str else None

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


def cmd_example(kb):
    kb.entries.clear()
    kb.add(SentenceTree("A").root, priority=10)
    kb.add(SentenceTree("A => B").root, priority=1)
    print("  loaded example KB:")
    kb.show()


def repl():
    kb = KB()
    print("Belief Revision CLI. Type 'help' for commands, 'quit' to exit.")
    while True:
        try:
            line = input("\nbr> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue

        # Split into command + remainder
        parts = line.split(None, 1)
        cmd = parts[0].lower()
        rest = parts[1] if len(parts) > 1 else ""

        if cmd in ("quit", "exit"):
            break
        elif cmd == "help":
            print(HELP)
        elif cmd in ("add", "expand"):
            cmd_add(kb, rest)
        elif cmd == "contract":
            cmd_contract(kb, rest)
        elif cmd == "revise":
            cmd_revise(kb, rest)
        elif cmd == "entails":
            cmd_entails(kb, rest)
        elif cmd == "consistent":
            cmd_consistent(kb)
        elif cmd == "show":
            kb.show()
        elif cmd == "clear":
            kb.entries.clear()
            print("  KB cleared")
        elif cmd == "postulates":
            cmd_postulates(kb, rest)
        elif cmd == "example":
            cmd_example(kb)
        else:
            print(f"  ! unknown command '{cmd}'. Type 'help'.")

    print("Goodbye.")


if __name__ == "__main__":
    repl()




 