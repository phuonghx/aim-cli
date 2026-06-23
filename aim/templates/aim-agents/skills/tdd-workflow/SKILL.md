---
name: tdd-workflow
description: Lays out test-driven development as a repeating loop, where a failing test is written first, the smallest code that satisfies it comes next, and a cleanup pass follows once the test is green. Applies when building a new feature, fixing a bug by first capturing it as a failing test, or working through logic intricate enough that a test should define correctness before any implementation. Covers the red-green-refactor rhythm, test structure, what to test in what order, and the traps that quietly defeat the practice.
---

# TDD Workflow

In test-driven development the test comes before the code. You describe the behavior you
want as an executable expectation, watch it fail, then write just enough to satisfy it.
The test becomes the specification, and a passing suite becomes the proof.

## The loop

```text
  ┌─────────────────────────────────────────────┐
  │  RED      write a test; run it; watch it fail │
  │   ↓                                           │
  │  GREEN    write the least code that passes it │
  │   ↓                                           │
  │  REFACTOR tidy up while every test stays green│
  │   ↓                                           │
  └──── repeat for the next behavior ─────────────┘
```

Three constraints keep the loop honest:

1. Add production code only in response to a test that is currently failing.
2. Write no more of a test than it takes to show that failure.
3. Write no more code than it takes to turn that test green.

## RED — start with a failing test

Express *what the code should do*, never how it does it.

| Aim at | Example name |
|---|---|
| Core behavior | `adds two positive numbers` |
| Boundaries | `returns zero for an empty list` |
| Failure modes | `raises on a negative quantity` |

Ground rules: the test must fail before you write any implementation, its name should
read as a sentence about behavior, and each test should pin down a single idea.

```python
# RED — this fails because cart_total does not exist yet
def test_cart_total_sums_line_items():
    cart = Cart(items=[Item(price=300), Item(price=150)])
    assert cart.total() == 450
```

## GREEN — do the minimum to pass

Write the plainest thing that turns the bar green. No speculative features, no tuning.

| Principle | What it means here |
|---|---|
| Avoid speculation | If a test does not demand it, do not build it |
| Plainest solution | The most obvious code that satisfies the assertion |
| Defer performance | Make it correct now; make it fast later, if measured |

```python
# GREEN — just enough to satisfy the test
class Cart:
    def __init__(self, items):
        self.items = items
    def total(self):
        return sum(item.price for item in self.items)
```

## REFACTOR — improve with a safety net

Now that the test guards behavior, reshape the code without changing what it does.

| Target | Move |
|---|---|
| Repetition | Pull shared logic into one place |
| Murky names | Rename for intent |
| Awkward structure | Reorganize for clarity |
| Tangled logic | Simplify the flow |

Refactor in small steps, keep the suite green throughout, and commit once it settles.

## Shape every test the same way

A readable test separates setup, action, and check:

```python
def test_discount_applies_to_subtotal():
    cart = Cart(items=[Item(price=1000)])   # set up the inputs
    cart.apply_discount(0.10)               # exercise the behavior
    assert cart.total() == 900              # check the result
```

## Where TDD pays off most

| Situation | Value of leading with tests |
|---|---|
| New feature | High — the test defines "done" |
| Bug fix | High — reproduce it as a failing test first |
| Intricate logic | High — correctness is hard to eyeball |
| Open-ended exploration | Low — spike first, then come back and test |
| Pure visual layout | Low — tests are a poor fit |

## What to test first

1. The expected, everyday path.
2. The ways it is meant to fail.
3. The edges — empty, zero, maximum, boundary values.
4. Performance characteristics, only where they actually matter.

## Traps that defeat TDD

| Trap | Practice instead |
|---|---|
| Skipping RED and writing code first | Always see the test fail before you fix it |
| Writing tests after the fact | Let the test lead the implementation |
| Gold-plating the first pass | Keep it minimal until a test asks for more |
| Cramming many assertions in | One behavior per test |
| Asserting on internals | Assert on observable behavior |

A closing reminder: if you cannot write the test, you do not yet understand the requirement.
