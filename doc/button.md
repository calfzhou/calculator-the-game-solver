# Calculator Buttons

## v1 Buttons

* Add

Adds button's number to the total.

Command line & solution display: `+N` where N is a positive number.

* Multiply

Multiplies the total by button's number.

Command line & solution display: `xN` where N is a positive number.

* Subtract

Subtracts the total by button's number.

Command line & solution display: `-N` where N is a positive number.

* Divide

Divides the total by button's number.
Can only be pressed when the total is divisible.

Command line & solution display: `/N` where N is a positive number.

* Backspace

Deletes the lowest digit from the total.
If the total has only one digit, it became `0`, of course.

Command line & solution display: `<<`.

* Number

Appends button's number to the end of the total.

Command line & solution display: `N` where N is a digit sequence.

* Convert

Converts button's former number from the total to button's latter number.
All matches (from left to right) will be converted.
Will not be pressed if no match.

Command line & solution display: `N1=>N2` where N1 and N2 are digit sequences.

* Square

Applies square to the total.

Command line & solution display: `^2`.

* Cube

Applies cube to the total.

Command line & solution display: `^3`.

* Sign (Plus/Minus)

Reverses the sign of the total.

Command line & solution display: `+/-`.

* Reverse

Reverses the order of digits of the total.

Command line: `reverse`.

Solution display: `Reverse`.

* Sum

Calculates the sum of all digits of the total (keeps the sign unchanged).

Command line: `sum`.

Solution display: `SUM`.

* Shift Left

Shifts all digits of the total from right to left, once.

Command line: `<`.

Solution display: `<Shift`.

* Shift Right

Shifts all digits of the total from left to right, once.

Command line: `>`.

Solution display: `Shift>`.

* Mirror

Appends the mirror of the total's digits sequence to the right of the total.

Command line: `mirror`.

Solution display: `Mirror`.

* Change

Adds button's number to several kinds of other buttons' numbers:
Add, Multiply, Subtract, Divide, Number;
and in v2 also: Cut, Insert, Digit Add, Digit Subtract.

Command line & solution display: `[+]N` where N is a positive number.

* Store

Long presses the button to remember the total.
Presses the button to append the memory to the end of the total.
Will not be pressed when nothing in memory.

Note that long press doesn't cost move.
In v2, long press also costs one move, use Store v2 instead.

Command line: `store`.

Normal press solution display: `Store(N)` where N is the stored number.

Long press solution display: `long press Store to Store(N)` or `long press Store(N1) to Store(N2)`.

* Invert 10

Subtracts every digit of the total by ten and flips it.
For example, `1` will become `9`, `6` will become `4`, etc.
But `5` remains `5`, and `0` remains `0`.

Command line: `inv10`.

Solution display: `Inv10`.

## v2 new Buttons

* Sort Asc

Sorts all digits of the total, from smallest to largest (from left to right).

Command line: `sort>`.

Solution display: `Sort>`.

* Sort Desc

Sorts all digits of the total, from largest to smallest (from left to right).

Command line: `sort<`.

Solution display: `Sort<`.

* Cut

Removes button's number from the total.
All matches (from left to right) will be removed.
Will not be pressed if no match.

Command line: `cutN`, where N is a digit sequence.

Solution display: `CUT N`.

* Delete

Upgraded version of Backspace button. Deletes the digit from the total at given position.

Command line: `delete`.

Solution display: `DELETE{'pos': P}`
where P is the position of digit to be removed (the lowest digit is pos 0).
It also indicates that you can press P times the left (`<`) arrow to move the cursor.

* Insert

Upgraded version of Number button.
Inserts button's number into the total at given position.

Command line: `insertN` where N is a positive number.

Solution display: `INSERT N{'pos': P}`.

* Round

Command line: `round`.

Solution display: `ROUND{'pos': P}`.

* Digit Add (Blue Add)

Upgraded version of Add button (the background color became blue).
Adds button's number to any digit of the total at given position.

Command line: `digit+N` or `blue+N` where N is a one-digit number.

Solution display: `(blue)digit+N{'pos': P}`.

* Digit Subtract (Blue Subtract)

Upgraded version of Subtract button (the background color became blue).
Subtracts any digit of the total at given position by button's number.

Command line: `digit-N` or `blue-N` where N is a one-digit number.

Solution display: `(blue)digit-N{'pos': P}`.

* Shift

Upgraded version of Shift Left/Right button.
Shifts the total using arrow pads (left or right).

Command line: `shift`.

Solution display: `Shift{'actions': 'ACT'}`
where ACT is the direction sequence, `>` means press right arrow, `<` means press left arrow.

* Replace (Blue Number)

Another upgraded version of Number button (the button's background color became blue).
Substitutes any digit in the total with button's number, at given position.

Command line: `replaceN` or `blueN` where N is a positive number.

Solution display: `(blue)REPLACE N{'pos': P}`.

* Store v2

Same with Store button, but this time long-press costs a move.

Command line: `storev2`.

Solution display: `Store(N)` for normal move (where N is the stored number),
`Store{'long_press': True}` or `Store(N){'long_press': True}` for long-press move.

* Lock

Locks up a digit of the total at given position.
The locked digit won't change during next move.
The lock will be removed after next move.

Command line: `lock`.

Solution display: `LOCK{'pos': P}`.
