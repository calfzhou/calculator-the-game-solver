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

        return int(str(total).replace(self._value, self._to))

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
        if isinstance(button, Delete):
            for pos in range(len(str(abs(total)))):
                yield button, { 'pos': pos }
        else:
            yield button, {}


def solve(total, goal, moves, buttons, portals=None):
    if total == goal:
        print(total)
        return

    if moves <= 0:
        raise FailedError

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

                if not isinstance(button, Change) and new_total == total:
                    raise CalcError('redundant step')
            except CalcError:
                continue

            # if new_total != goal:
            try:
                solve(new_total, goal, moves - 1, buttons, portals=portals)
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
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-g', '--goals', type=int, nargs='+', metavar='GOAL',
                       help='the goal number(s)')
    group.add_argument('-w', '--words', nargs='+', metavar='WORD',
                       help='the goal password(s)')

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

    if args.words:
        args.goals = []
        for word in args.words:
            goal = translate_password(word)
            print('translate password', word, 'to numeric goal:', goal)
            args.goals.append(goal)

    print()

    for goal in args.goals:
        print('goal:', goal)
        try:
            solve(args.total, goal, args.moves, args.buttons, portals=args.portals)
        except FailedError:
            print('no solution found!')

        print()


if __name__ == '__main__':
    main()
