# Goal

## Goal Number in v1

In v1, the goal is a number, e.g. `128`, `-11`.
Use `-g NUMBER` to tell the solver the goal.

## Multiple Goals and Password Goal in v2

In v2, there could be more than one goals for one level.
Parameter `-g` supports multi-goals, just separate them with space, i.e. `-g GOAL1 GOAL2 ...`.
The solver will find solution for every goal.

For some special levels (the last level before each satellite back online),
the goals might be english words (say Clicky's password).
Actually each word can be converted to a certain number, the solver will find solution for this number,
and then the last move is using `ABC` button to convert number to word.

e.g.:

``` console
$ ./calculator-solver.py -m 3 -g even odd -t 2825 -b 'sort<' cut8
goal: EVEN
2825 ABC -> EVEN

goal: ODD
522 ABC -> ODD
8522 Cut8 -> 522
2825 Sort< -> 8522
```
