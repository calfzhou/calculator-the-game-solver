import unittest

import ddt

import calculator_solver as solver


@ddt.ddt
class Foo(unittest.TestCase):
    @ddt.file_data('test-data/button-press-cases.yaml')
    def test_button_press(self, **case_info):
        class_name = case_info['button']
        init_args = case_info.get('init')
        press_args = case_info.get('press') or {}
        total = case_info['total']
        expected = case_info.get('result')

        if init_args is None:
            init_args = []
        elif not isinstance(init_args, list):
            init_args = [init_args]

        button_class = getattr(solver, class_name)
        button = button_class(*init_args)

        try:
            new_total = button.press(total, **press_args)
            self.assertEqual(new_total, expected)
        except solver.CalcError:
            self.assertIsNone(expected)


if __name__ == '__main__':
    unittest.main()
