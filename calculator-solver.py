#!/usr/bin/env python3
import argparse
import itertools


class CalcError(Exception):
    pass


class FailedError(Exception):
    pass


def sign(value):
    if value > 0:
        return 1
    elif value < 0:
        return -1
    else:
        return 0


class Button:
    def press(self, **kwargs):
        pass

    def revert(self, **kwargs):
        pass

    def inc(self, value):
        pass

    def __repr__(self):
        return self.__str__()


class Add(Button):
    def __init__(self, value):
        self._value = value

    def press(self, total, **kwargs):
        return total + self._value

    def inc(self, value):
        self._value += value

    def __str__(self):
        return '+{}'.format(self._value)


class Mul(Button):
    def __init__(self, value):
        self._value = value

    def press(self, total, **kwargs):
        return total * self._value

    def inc(self, value):
        self._value += value

    def __str__(self):
        return 'x{}'.format(self._value)


class Sub(Add):
    def __init__(self, value):
        super().__init__(-value)

    def inc(self, value):
        self._value -= value

    def __str__(self):
        return '{}'.format(self._value)


class Div(Button):
    def __init__(self, value):
        self._value = value

    def press(self, total, **kwargs):
        if total % self._value != 0:
            raise CalcError('aliquant')

        return total // self._value

    def inc(self, value):
        self._value += value

    def __str__(self):
        return '/{}'.format(self._value)


class Backspace(Button):
    def press(self, total, **kwargs):
        return total // 10

    def __str__(self):
        return '<<'


class Num(Button):
    def __init__(self, value):
        self._value = value

    def press(self, total, **kwargs):
        return int('{}{}'.format(total, self._value))

    def inc(self, value):
        self._value += value

    def __str__(self):
        return '{}'.format(self._value)


class Convert(Button):
    def __init__(self, value, to):
        self._value = str(value)
        self._to = str(to)

    def press(self, total, **kwargs):
        if self._value not in str(total):
            raise CalcError('pattern not found')

        t = str(total).replace(self._value, self._to)
        if t == '' or t == '-':
            return 0
        else:
            return int(t)

    def __str__(self):
        return '{}=>{}'.format(self._value, self._to)


class Pow(Button):
    def __init__(self, value):
        self._value = value

    def press(self, total, **kwargs):
        return total ** self._value

    def __str__(self):
        return '^{}'.format(self._value)


class Sign(Button):
    def press(self, total, **kwargs):
        return -total

    def __str__(self):
        return '+/-'


class Reverse(Button):
    def press(self, total, **kwargs):
        return sign(total) * int(''.join(reversed(str(abs(total)))))

    def __str__(self):
        return 'Reverse'


class Sum(Button):
    def press(self, total, **kwargs):
        return sign(total) * sum(int(d) for d in str(abs(total)))

    def __str__(self):
        return 'SUM'


class ShiftRight(Button):
    def press(self, total, **kwargs):
        t = str(abs(total))
        return sign(total) * int(t[-1] + t[:-1])

    def __str__(self):
        return 'Shift>'


class ShiftLeft(Button):
    def press(self, total, **kwargs):
        t = str(abs(total))
        return sign(total) * int(t[1:] + t[0])

    def __str__(self):
        return '<Shift'


class Mirror(Button):
    def press(self, total, **kwargs):
        # if total > 999 or total < -999:
        #     raise CalcError('overflow')

        t = str(abs(total))
        t += ''.join(reversed(t))
        return sign(total) * int(t)

    def __str__(self):
        return 'Mirror'


class Change(Button):
    def __init__(self, value):
        self._value = value

    def press(self, total, buttons, **kwargs):
        for b in buttons:
            b.inc(self._value)

        return total

    def revert(self, buttons, **kwargs):
        for b in buttons:
            b.inc(-self._value)

    def __str__(self):
        return '[+]{}'.format(self._value)


class Store(Num):
    def __init__(self, value=''):
        super().__init__(value)

    def store(self, total):
        self._value = total

    def get_value(self):
        return self._value

    def press(self, total, **kwargs):
        if self._value == '':
            raise CalcError('store is empty')
        elif self._value < 0:
            raise CalcError('store is < 0')

        return super().press(total, **kwargs)

    def __str__(self):
        return 'Store({})'.format(self._value)


class Inv10(Button):
    def press(self, total, **kwargs):
        return int(''.join(map(self._invert, str(total))))

    def _invert(self, digit):
        if digit in '12346789':
            return str(10 - int(digit))
        else:
            return digit

    def __str__(self):
        return 'Inv10'


class Sort(Button):
    def __init__(self, desc: bool):
        self._desc = desc

    def press(self, total, **kwargs):
        t = sorted(str(abs(total)))
        if self._desc:
            t = reversed(t)

        return sign(total) * int(''.join(t))

    def __str__(self):
        return 'Sort{}'.format(self._desc and '<' or '>')


class Cut(Convert):
    def __init__(self, value):
        super().__init__(value, '')

    def __str__(self):
        return 'Cut{}'.format(self._value)


class Delete(Button):
    def press(self, total, pos, **kwargs):
        s = sign(total)
        total = abs(total)
        base = 10 ** pos
        total = total // base // 10 * base + total % base
        return s * total

    def __str__(self):
        return 'DELETE'


class Insert(Button):
    def __init__(self, value):
        self._value = value

    def press(self, total, pos, **kwargs):
        s = sign(total)
        total = abs(total)
        base = 10 ** pos
        base_mid = 10 ** len(str(self._value))
        left, right = divmod(total, base)
        total = left * base * base_mid + self._value * base + right
        return s *total

    def __str__(self):
        return 'INSERT{}'.format(self._value)


class Round(Button):
    def press(self, total, pos, **kwargs):
        s = sign(total)
        total = abs(total)
        base = 10 ** pos
        # NOTE: Python's round is not suitable for this button.
        # total = round(total / base) * base
        left, right = divmod(total, base)
        if right >= (base >> 1):
            left += 1
        total = left * base
        return s * total

    def __str__(self):
        return 'ROUND'


class DigitAdd(Button):
    def __init__(self, value):
        self._value = value

    def press(self, total, pos, **kwargs):
        t = list(str(total))
        digit = int(t[-pos - 1])
        if digit == 0:
            digit = 10
        digit = abs(digit + self._value) % 10
        t[-pos - 1] = str(digit)
        return int(''.join(t))

    def __str__(self):
        return 'digit+{}'.format(self._value)


class DigitSub(DigitAdd):
    def __init__(self, value):
        super().__init__(-value)

    def __str__(self):
        return 'digit{}'.format(self._value)


class Shift(Button):
    _shift_left = ShiftLeft()
    _shift_right = ShiftRight()

    # def press(self, total, pos, **kwargs):
    #     t = str(abs(total))
    #     return sign(total) * int(t[pos:] + t[:pos])

    def press(self, total, actions, **kwargs):
        for act in actions:
            if act == '<':
                total = self._shift_left.press(total)
            elif act == '>':
                total = self._shift_right.press(total)
            elif act in ' ,;':
                pass
            else:
                raise CalcError('unknown action', act)

        return total

    def iter_action_groups(self, total):
        if -9 <= total <= 9:
            return

        t = str(abs(total))
        zeros = [i for i, d in enumerate(t) if d == '0']
        n = len(zeros)

        for r in range(n + 1):
            # Shift right to remove r '0's (counting start from right to left).
            right_moves = r and (len(t) - zeros[-r])
            for l in range(max(n - r, 1)):
                # Continuous '0's will be removed together when shifting left.
                if l < n and zeros[l] == zeros[l - 1] + 1:
                    continue

                # Shift left to remove l '0's (counting start from left to right).
                left_moves = l and ((right_moves - r) + (zeros[l - 1] - l + 1))

                # ('>' * offset + '<' * -offset) can recover the origin order.
                offset = left_moves - (right_moves - r)

                # Safe shifting bound without removing more '0's.
                if r + l == n:
                    left_bound = (len(t) - n) // 2 + offset
                    right_bound = len(t) - n - left_bound - 1
                else:
                    left_bound = zeros[l] - l - 1
                    right_bound = len(t) - zeros[-r - 1] - r - 1

                for index in range(-left_bound, right_bound + 1):
                    actions = '>' * right_moves + '<' * left_moves + '>' * (index + offset) + '<' * (-index - offset)
                    if actions:
                        actions = ' '.join(actions[i:i + 5] for i in range(0, len(actions), 5))
                        yield actions

    def __str__(self):
        return 'Shift'


def do_portal(total, left, right):
    s = sign(total)
    total = abs(total)
    t = str(abs(total))
    right = 10 ** right
    while len(t) > left:
        d = int(t[0])
        t = t[1:]
        t = str(int(t) + d * right)

    return s * int(t)


def iter_buttons(total, buttons):
    for button in buttons:
        if isinstance(button, (Delete, DigitAdd, DigitSub)):
            for pos in range(len(str(abs(total)))):
                yield button, { 'pos': pos }
        elif isinstance(button, Insert):
            for pos in range(len(str(abs(total))) + 1):
                yield button, { 'pos': pos }
        elif isinstance(button, Round):
            for pos in range(1, len(str(abs(total)))):
                yield button, { 'pos': pos }
        elif isinstance(button, Shift):
            for actions in button.iter_action_groups(total):
                yield button, { 'actions': actions }
        else:
            yield button, {}


def solve(total: int, goal: int, moves: int, buttons, portals=None, **kwargs):
    if total == goal:
        print(total)
        return

    if moves <= 0:
        raise FailedError

    known_totals: set = kwargs.setdefault('known_totals', set())
    known_totals.add(total)

    stores = [b for b in buttons if isinstance(b, Store)]
    prev_values = [store.get_value() for store in stores]
    # Only store non-negative total
    repeat = total >= 0 and len(stores) or 0
    for switches in itertools.product((False, True), repeat=repeat):
        # Long press a `store` button if corresponding switch is `True`.
        for need_store, store, prev_value in zip(switches, stores, prev_values):
            if need_store:
                store.store(total)
            else:
                store.store(prev_value)

        for button, params in iter_buttons(total, buttons):
            try:
                new_total = button.press(total=total, buttons=buttons, **params)
                if new_total > 999999 or new_total < -999999:
                    raise CalcError('overflow')

                if portals:
                    new_total = do_portal(new_total, *portals)

                if not isinstance(button, Change) and new_total in known_totals:
                    raise CalcError('redundant step')
            except CalcError:
                continue

            # if new_total != goal:
            try:
                solve(new_total, goal, moves - 1, buttons, portals=portals, known_totals=known_totals)
                print(total, str(button) + str(params or ''), '->', new_total)
                # for store in stores:
                #     if store.get_value() == total:
                #         print('long press store({}) to {}'.format(prev_value, store))
                for store, prev_value in zip(stores, prev_values):
                    if store.get_value() == total:
                        print('long press {} to {}'.format(Store(prev_value), store))
                    store.store(prev_value)
                return
            except FailedError:
                # button.revert(buttons=buttons)
                continue
            finally:
                button.revert(buttons=buttons)
                # for store, prev_value in zip(stores, prev_values):
                #     store.store(prev_value)

            # print(total, button, '->', new_total)
            # button.revert(buttons=buttons)
            # for store, prev_value in zip(stores, prev_values):
            #     store.store(prev_value)

            # return

    known_totals.remove(total)
    for store, prev_value in zip(stores, prev_values):
        store.store(prev_value)

    raise FailedError


def named_button(text):
    try:
        if text == '<<':
            return Backspace()
        elif text == '<':
            return ShiftLeft()
        elif text == '>':
            return ShiftRight()
        elif text == '+/-':
            return Sign()
        elif text == 'reverse':
            return Reverse()
        elif text == 'sum':
            return Sum()
        elif text == 'mirror':
            return Mirror()
        elif text == 'store':
            return Store()
        elif text == 'inv10':
            return Inv10()
        elif text == 'sort>':
            return Sort(False)
        elif text == 'sort<':
            return Sort(True)
        elif text == 'delete':
            return Delete()
        elif text == 'round':
            return Round()
        elif text == 'shift':
            return Shift()
        elif text.startswith('insert'):
            return Insert(int(text[6:]))
        elif text.startswith('digit+'):
            return DigitAdd(int(text[6:]))
        elif text.startswith('digit-'):
            return DigitSub(int(text[6:]))
        elif text.startswith('cut'):
            return Cut(text[3:])
        elif text.startswith('[+]'):
            return Change(int(text[3:]))
        elif text.startswith('+'):
            return Add(int(text[1:]))
        elif text.startswith('-'):
            return Sub(int(text[1:]))
        elif text.startswith('x'):
            return Mul(int(text[1:]))
        elif text.startswith('/'):
            return Div(int(text[1:]))
        elif text.startswith('^'):
            return Pow(int(text[1:]))
        elif text.isdigit():
            return Num(int(text))
        elif '=>' in text:
            pattern, to = text.split('=>', 1)
            return Convert(pattern, to)
    except argparse.ArgumentTypeError:
        raise
    except Exception as e:
        raise argparse.ArgumentTypeError('invalid button {}: {}'.format(text, e))

    raise argparse.ArgumentTypeError('unknown button {}'.format(text))


def translate_password(word):
    return int(''.join(map(lambda c: str((ord(c.lower()) - ord('a')) // 3 + 1), word)))


def main():
    parser = argparse.ArgumentParser(description='Calculator: The Game - Puzzle Solver')
    parser.add_argument('-g', '--goals', nargs='+', metavar='GOAL', required=True,
                        help='the goal number(s) or password(s)')

    parser.add_argument('-m', '--moves', type=int, required=True,
                        help='the number of moves can make')
    parser.add_argument('-t', '--total', type=int, default=0,
                        help='the initial total number')
    parser.add_argument('-b', '--buttons', type=named_button, nargs='+', metavar='BUTTON', required=True,
                        help='the buttons')
    parser.add_argument('-p', '--portals', type=int, nargs=2, metavar=('LEFT', 'RIGHT'),
                        help='portal range (zero based)')

    args = parser.parse_args()
    print(args)

    for word in args.goals:
        if word.isdigit():
            goal = int(word)
            print('goal:', goal)
        else:
            goal = translate_password(word)
            print('goal:', word, '=>', goal)

        try:
            solve(args.total, goal, args.moves, args.buttons, portals=args.portals)
        except FailedError:
            print('no solution found!')

        print()


if __name__ == '__main__':
    main()
