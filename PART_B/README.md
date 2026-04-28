# Belief Revision Engine

A belief revision engine, built for the **02180 Introduction to AI** course assignment at DTU.

The system maintains a prioritized knowledge base, supports logical entailment via resolution, and implements expansion, partial-meet contraction, and revision (via the Levi identity). Includes tests that verifies the implementation against the AGM postulates. Includes a CLI interface for custom knowledge bases and AGM postulate checks.

## File structure

```
PART_B
├── agm.py            # AGM postulates
├── BeliefBase.py     # KB class, resolution, contraction, revision
├── README.md         # This file
├── tests.py          # Tests for AGM postulates
└── Tree_AST_CNF.py   # Tokenizer, parser, AST, and CNF conversion
```

`Tree_AST_CNF` provides parsing and CNF conversion, `BeliefBase` builds the prioritized belief base and the resolution-based entailment check on top of it, and `agm.py` exercises the whole stack against the postulates.

## Running (todo)

The project is pure Python with no external dependencies. To run the postulate tests:

```bash
python agm.py
```

To run the small standalone demo inside `BeliefBase.py`:

```bash
python BeliefBase.py
```

To inspect parsing and CNF conversion on a single formula:

```bash
python Tree_AST_CNF.py
```

## Formula Syntax

Formulas are written as infix strings and parsed by `SentenceTree`. Variables are single alphabetic characters.

| Operator | Symbol  | Precedence | Associativity |
|----------|---------|------------|---------------|
| Not      | `~`     | highest    | right         |
| And      | `&`     |            | left          |
| Or       | `\|`    |            | left          |
| Implies  | `=>`    |            | right         |
| Iff      | `<=>`   | lowest     | left          |

Parentheses override precedence in the usual way. Examples: `A => B`, `~(A & B)`, `(A | B) & ~C`, `A <=> B`.

## Belief Base

Implemented in `BeliefBase.py` as the `KB` class. Each entry is a `BeliefEntry(formula, priority)` where `formula` is the root of a parsed AST and `priority` is an integer (higher = more entrenched). Higher-priority beliefs are preferred during contraction.

Included methods:

- `add(formula, priority=1)` - insert a belief
- `expand(formula, priority=1)` - alias for `add`, used to express AGM expansion (`B + φ`)
- `entails(phi)` - resolution-based entailment check
- `contraction(phi)` - returns a new KB not entailing φ
- `copy()` - deep-ish copy preserving priorities
- `is_consistent()` - checks whether the KB entails an arbitrary fresh symbol
- `show()` - pretty-prints the KB
- `formulas()` - returns the underlying list of formulas
- `entries` - list of `BeliefEntry` records

## Entailment by Resolution

Entailment is implemented from scratch (no external SAT or theorem-proving libraries) in three layers:

1. **AST construction**: `tokenize` and `parse` in `Tree_AST_CNF.py` use a shunting-yard-style stack algorithm to build a `Sentence(op, args)` tree.
2. **CNF conversion**:`Sentence.to_cnf()` recursively rewrites the tree by eliminating `IFF` and `IF`, pushing `NOT` inward via De Morgan's laws and double-negation, and distributing `OR` over `AND`. `get_clauses()` then flattens the CNF tree into a list of clauses (sets of literals, where negated literals are encoded as the string `"NOT(X)"`).
3. **Refutation resolution**: `resolution(formulas, query)` in `BeliefBase.py` adds the negation of the query, exhaustively resolves complementary literal pairs, and returns `True` iff it derives the empty clause. The clause set is stored as `frozenset`s to deduplicate, and resolution terminates when no new clauses are produced.

`KB.entails(phi)` is just `resolution(self.formulas(), phi)`.

## Contraction (priority-based partial meet)

`KB.contraction(phi)` follows a priority-ordered partial-meet strategy:

1. If the KB doesn't entail φ, return a copy unchanged (vacuity).
2. Otherwise, sort entries ascending by priority and try removing each one individually. If any single removal already breaks entailment of φ, return that result.
3. If no single removal suffices, drop the lowest-priority entry permanently and repeat.
4. Loop until φ is no longer entailed.

This biases removal toward low-priority beliefs while still producing a φ-free result in cases where multiple beliefs jointly entail φ.

## Expansion and Revision

**Expansion** (`KB.expand`) simply appends the new formula at the given priority, no consistency check is performed, matching the AGM definition of `B + φ`.

**Revision** is implemented as a top-level function `revise(base, formula, priority)` using the **Levi identity**:

> B ∗ φ = (B ÷ ¬φ) + φ

That is: contract by the negation of the input, then expand by the input. This is the standard AGM construction connecting contraction and revision.

## AGM Postulate Tests

Our tests checks the following postulates:

**Contraction**: Success, Inclusion, Vacuity, Extensionality, Recovery

**Revision**: Success, Inclusion, Vacuity, Consistency, Extensionality

Per the assignment brief, Closure, Conjunctive Inclusion, Conjunctive Overlap, Superexpansion, and Subexpansion are excluded.

Each postulate function prints `satisfied`, `not satisfied`, or `satisfied (precondition not met)` for the corresponding test.

### Test Cases

| # | Scenario                              | Notes                                                          |
|---|---------------------------------------|----------------------------------------------------------------|
| 1 | Modus ponens KB                       | φ = `B`, ψ = `B & B`                                           |
| 2 | Disjunctive KB                        | φ = `A \| C` — Recovery is expected to fail here              |
| 3 | Empty KB                              | Edge case; vacuity should hold trivially                       |
| 4 | Four-formula priority gradient        | Stress test for prioritized contraction                        |
| 5 | De Morgan extensionality              | φ = `~(A & B)`, ψ = `~A \| ~B`                                |
| 6 | Material implication extensionality   | φ = `A => B`, ψ = `~A \| B`                                   |
| 7 | Priority-driven revision              | High-priority `A` survives, low-priority `B` displaced by `~B`|
| 8 | Disjunctive input forcing change      | KB has `~A`, `~B`; revising by `A \| B` requires real change  |
| 9 | Conjunctive contraction               | Unrelated belief `C` should survive contracting `A & B`       |
