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


class Del(Button):
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
    def __init__(self, pattern, to):
        self._pattern = str(pattern)
        self._to = str(to)

    def press(self, total, **kwargs):
        if self._pattern not in str(total):
            raise CalcError('pattern not found')

        return int(str(total).replace(self._pattern, self._to))

    def __str__(self):
        return '{}=>{}'.format(self._pattern, self._to)


class Pow(Button):
    def __init__(self, value):
        self._value = value

    def press(self, total, **kwargs):
        return total ** self._value

    def __str__(self):
        return '^{}'.format(self._value)


class Flip(Button):
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


def do_portal(total, left, right):
    s = sign(total)
    total = abs(total)
    t = str(abs(total))
    right = 10 ** right
    while len(t) > left:
        d = int(t[0])
        t = t[1:]
        t = str(int(t) + d * right)

    return int(t) * s


def solve(total, goal, moves, buttons, portals=None):
    if total == goal:
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

        for button in buttons:
            try:
                new_total = button.press(total=total, buttons=buttons)
                if new_total > 999999 or new_total < -999999:
                    raise CalcError('overflow')
            except CalcError:
                continue

            if portals:
                new_total = do_portal(new_total, *portals)

            # if new_total != goal:
            try:
                solve(new_total, goal, moves - 1, buttons, portals=portals)
                print(total, button, '->', new_total)
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
            return Del()
        elif text == '<':
            return ShiftLeft()
        elif text == '>':
            return ShiftRight()
        elif text == '+/-':
            return Flip()
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
    except Exception as e:
        raise argparse.ArgumentTypeError('invalid button {}: {}'.format(text, e))

    raise argparse.ArgumentTypeError('unknown button {}'.format(text))


def main():
    parser = argparse.ArgumentParser(description='Calculator: The Game - Puzzle Solver')
    parser.add_argument('-g', '--goals', '--goal', type=int, nargs='+', required=True,
                        help='the goal number(s)')
    parser.add_argument('-m', '--moves', type=int, required=True,
                        help='the number of moves can make')
    parser.add_argument('-t', '--total', type=int, default=0,
                        help='the initial total number')
    parser.add_argument('-b', '--buttons', '--button', type=named_button, nargs='+', required=True,
                        help='the buttons')
    parser.add_argument('-p', '--portals', type=int, nargs=2,
                        help='portal range LEFT, RIGHT (zero based)')

    args = parser.parse_args()
    print(args)

    for goal in args.goals:
        print('goal:', goal)
        try:
            solve(args.total, goal, args.moves, args.buttons, portals=args.portals)
        except FailedError:
            print('no solution found!')

        print()


if __name__ == '__main__':
    main()
